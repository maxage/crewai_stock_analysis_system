"""使用akshare获取股票数据的工具类"""
from crewai import Agent, Task, tools
from typing import Dict, Any, List, Optional
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import time

# 使用项目自定义的BaseTool类
from src.tools.reporting_tools import BaseTool

# 设置日志配置为DEBUG级别，确保所有调试信息都能被记录
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 确保该模块的日志级别为DEBUG


class AkShareTool(BaseTool):
    """AkShare数据工具"""

    name: str = "AkShare Data Tool"
    description: str = "获取股票的财务数据、价格数据和市场信息"

    def _run(self, ticker: str, period: str = "1y") -> str:
        """
        获取股票数据

        Args:
            ticker: 股票代码（A股格式，如：'sh600000'）
            period: 数据周期 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

        Returns:
            股票数据报告
        """
        try:
            # 添加请求延迟以避免请求过于频繁
            time.sleep(1)
            # 添加详细的请求参数日志
            logger.debug(f"[API请求] 开始获取 {ticker} 的数据，周期: {period}")
            logger.info(f"获取 {ticker} 的数据，周期: {period}")

            # 获取基本信息
            logger.debug(f"[API请求] 获取基本信息: {ticker}")
            # 添加额外延迟
            time.sleep(0.5)
            info = self._get_stock_basic_info(ticker)
            logger.debug(f"[API响应] 成功获取基本信息，字段数量: {len(info) if isinstance(info, dict) else 0}")

            # 获取历史价格数据
            logger.debug(f"[API请求] 获取历史价格数据: {ticker}, 周期: {period}")
            # 添加延迟避免请求过于频繁
            time.sleep(0.5)
            hist = self._get_stock_history_data(ticker, period)
            logger.debug(f"[API响应] 成功获取历史数据，数据行数: {len(hist) if hasattr(hist, 'shape') else 0}")

            # 获取财务数据
            logger.debug(f"[API请求] 获取财务报表数据: {ticker}")
            # 添加延迟避免请求过于频繁
            time.sleep(0.5)
            financials = self._get_financial_statements(ticker, "利润表")
            # 添加额外延迟
            time.sleep(0.3)
            balance_sheet = self._get_financial_statements(ticker, "资产负债表")
            # 添加额外延迟
            time.sleep(0.3)
            cashflow = self._get_financial_statements(ticker, "现金流量表")
            logger.debug(f"[API响应] 成功获取财务数据")

            # 生成数据报告
            report = self._generate_stock_report(ticker, info, hist, financials, balance_sheet, cashflow)
            logger.debug(f"[数据处理] 成功生成数据报告，长度: {len(report)} 字符")

            logger.info(f"成功获取 {ticker} 的数据")
            return report

        except Exception as e:
            # 添加详细的错误日志
            error_msg = f"获取 {ticker} 数据失败: {str(e)}"
            logger.error(error_msg)
            logger.debug(f"[API错误] 详细信息 - 股票代码: {ticker}, 周期: {period}, 错误类型: {type(e).__name__}, 错误详情: {str(e)}")
            return error_msg

    def _get_stock_basic_info(self, ticker: str) -> Dict:
        """获取股票基本信息"""
        try:
            # 使用akshare获取股票基本信息
            # 注意：akshare的股票代码需要是带市场标识的格式，如 'sh600000' 或 'sz000001'
            stock_zh_a_spot_df = ak.stock_zh_a_spot_em()
            # 安全地获取股票信息，如果找不到指定股票代码则返回空字典
            stock_info_row = stock_zh_a_spot_df[stock_zh_a_spot_df['代码'] == ticker]
            stock_info = stock_info_row.iloc[0].to_dict() if not stock_info_row.empty else {}
            
            # 尝试获取更多财务数据
            try:
                # 获取财务指标数据
                financial_indicator_df = ak.stock_financial_analysis_indicator_ths(symbol=ticker)
                financial_indicator = financial_indicator_df.set_index('指标名称')['最新'].to_dict() if not financial_indicator_df.empty else {}
            except:
                financial_indicator = {}
                logger.warning(f"获取财务指标数据失败，使用默认值")
                
            # 转换为与yfinance类似的格式
            info = {
                'longName': stock_info.get('名称', 'N/A'),
                'industry': stock_info.get('行业', 'N/A'),
                'marketCap': float(stock_info.get('市值', 0)) * 1000000 if stock_info.get('市值', 0) != 0 else 0,  # 转换为元
                'currentPrice': float(stock_info.get('现价', 0)) if stock_info.get('现价', 0) != 0 else 0,
                'fiftyTwoWeekHigh': float(stock_info.get('最高', 0)) if stock_info.get('最高', 0) != 0 else 0,
                'fiftyTwoWeekLow': float(stock_info.get('最低', 0)) if stock_info.get('最低', 0) != 0 else 0,
                'trailingPE': float(stock_info.get('市盈率-动', 0)) if stock_info.get('市盈率-动', 0) != 0 else 'N/A',
                'forwardPE': float(financial_indicator.get('预测市盈率', 0)) if financial_indicator.get('预测市盈率', 0) != 0 else 'N/A',
                'priceToBook': float(financial_indicator.get('市净率', 0)) if financial_indicator.get('市净率', 0) != 0 else 'N/A',
                'dividendYield': float(financial_indicator.get('股息率', 0)) / 100 if financial_indicator.get('股息率', 0) != 0 else 0,
                'beta': float(financial_indicator.get('贝塔系数', 0)) if financial_indicator.get('贝塔系数', 0) != 0 else 'N/A'
            }
            return info
        except Exception as e:
            logger.error(f"获取股票基本信息失败: {str(e)}")
            return {}

    def _get_stock_history_data(self, ticker: str, period: str) -> pd.DataFrame:
        """获取股票历史价格数据"""
        try:
            # 转换周期参数为日期范围
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = self._calculate_start_date(period)
            
            # 使用akshare获取历史数据
            stock_zh_a_daily_df = ak.stock_zh_a_daily(symbol=ticker, start_date=start_date, end_date=end_date, adjust="qfq")
            
            # 重命名列以匹配yfinance的格式
            if not stock_zh_a_daily_df.empty:
                stock_zh_a_daily_df = stock_zh_a_daily_df.rename(columns={
                    '开盘': 'Open',
                    '收盘': 'Close',
                    '最高': 'High',
                    '最低': 'Low',
                    '成交量': 'Volume'
                })
                # 安全地设置日期索引，处理可能没有'日期'列的情况
                if '日期' in stock_zh_a_daily_df.columns:
                    stock_zh_a_daily_df['Date'] = pd.to_datetime(stock_zh_a_daily_df['日期'])
                    stock_zh_a_daily_df = stock_zh_a_daily_df.set_index('Date')
                elif 'date' in stock_zh_a_daily_df.columns:
                    stock_zh_a_daily_df['Date'] = pd.to_datetime(stock_zh_a_daily_df['date'])
                    stock_zh_a_daily_df = stock_zh_a_daily_df.set_index('Date')
                else:
                    # 如果没有日期列，使用默认索引作为日期
                    logger.warning(f"获取历史数据缺少日期列，使用默认索引作为日期")
                    dates = pd.date_range(end=end_date, periods=len(stock_zh_a_daily_df), freq='D')
                    stock_zh_a_daily_df['Date'] = dates
                    stock_zh_a_daily_df = stock_zh_a_daily_df.set_index('Date')
                # 只保留需要的列
                # 确保所有需要的列都存在
                required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                for col in required_columns:
                    if col not in stock_zh_a_daily_df.columns:
                        stock_zh_a_daily_df[col] = 0
                stock_zh_a_daily_df = stock_zh_a_daily_df[required_columns]
            
            return stock_zh_a_daily_df
        except Exception as e:
            logger.error(f"获取股票历史数据失败: {str(e)}")
            return pd.DataFrame()

    def _get_financial_statements(self, ticker: str, statement_type: str) -> pd.DataFrame:
        """获取财务报表数据"""
        try:
            if statement_type == "利润表":
                # 获取利润表数据
                financial_df = ak.stock_financial_report_sina(symbol=ticker, report_type="利润表")
            elif statement_type == "资产负债表":
                # 获取资产负债表数据
                financial_df = ak.stock_financial_report_sina(symbol=ticker, report_type="资产负债表")
            elif statement_type == "现金流量表":
                # 获取现金流量表数据
                financial_df = ak.stock_financial_report_sina(symbol=ticker, report_type="现金流量表")
            else:
                financial_df = pd.DataFrame()
            
            return financial_df
        except Exception as e:
            logger.error(f"获取{statement_type}失败: {str(e)}")
            return pd.DataFrame()

    def _calculate_start_date(self, period: str) -> str:
        """根据周期计算开始日期"""
        today = datetime.now()
        if period == "1d":
            start_date = today - timedelta(days=1)
        elif period == "5d":
            start_date = today - timedelta(days=5)
        elif period == "1mo":
            start_date = today - timedelta(days=30)
        elif period == "3mo":
            start_date = today - timedelta(days=90)
        elif period == "6mo":
            start_date = today - timedelta(days=180)
        elif period == "1y":
            start_date = today - timedelta(days=365)
        elif period == "2y":
            start_date = today - timedelta(days=730)
        elif period == "5y":
            start_date = today - timedelta(days=1825)
        elif period == "10y":
            start_date = today - timedelta(days=3650)
        elif period == "ytd":
            # 年初至今
            start_date = datetime(today.year, 1, 1)
        elif period == "max":
            # 尽可能早的日期
            start_date = datetime(2000, 1, 1)
        else:
            # 默认1年
            start_date = today - timedelta(days=365)
        
        return start_date.strftime('%Y%m%d')

    def _generate_stock_report(self, ticker: str, info: Dict, hist: pd.DataFrame, 
                             financials: pd.DataFrame, balance_sheet: pd.DataFrame, 
                             cashflow: pd.DataFrame) -> str:
        """生成股票数据报告"""
        report = f"# {ticker} 股票数据报告\n\n"
        report += f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # 基本信息
        report += "## 基本信息\n\n"
        report += f"- **公司名称**: {info.get('longName', 'N/A')}\n"
        report += f"- **行业**: {info.get('industry', 'N/A')}\n"
        report += f"- **市值**: ¥{info.get('marketCap', 0):,.0f}\n" if info.get('marketCap', 0) > 0 else f"- **市值**: {info.get('marketCap', 'N/A')}\n"
        report += f"- **当前价格**: ¥{info.get('currentPrice', 0):.2f}\n" if info.get('currentPrice', 0) > 0 else f"- **当前价格**: {info.get('currentPrice', 'N/A')}\n"
        report += f"- **52周最高**: ¥{info.get('fiftyTwoWeekHigh', 0):.2f}\n" if info.get('fiftyTwoWeekHigh', 0) > 0 else f"- **52周最高**: {info.get('fiftyTwoWeekHigh', 'N/A')}\n"
        report += f"- **52周最低**: ¥{info.get('fiftyTwoWeekLow', 0):.2f}\n\n" if info.get('fiftyTwoWeekLow', 0) > 0 else f"- **52周最低**: {info.get('fiftyTwoWeekLow', 'N/A')}\n\n"

        # 价格统计
        if not hist.empty:
            report += "## 价格统计\n\n"
            current_price = hist['Close'].iloc[-1]
            period_return = ((current_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100

            report += f"- **当前价格**: ¥{current_price:.2f}\n"
            report += f"- **期间涨幅**: {period_return:.2f}%\n"
            report += f"- **期间最高**: ¥{hist['High'].max():.2f}\n"
            report += f"- **期间最低**: ¥{hist['Low'].min():.2f}\n"
            report += f"- **平均成交额**: {hist['Volume'].mean():,.0f} 股\n\n"

        # 关键财务指标
        report += "## 关键财务指标\n\n"
        financial_metrics = self._extract_financial_metrics(info, financials)
        for metric, value in financial_metrics.items():
            report += f"- **{metric}**: {value}\n"

        # 技术指标
        if not hist.empty:
            report += "\n## 技术指标\n\n"
            tech_indicators = self._calculate_technical_indicators(hist)
            for indicator, value in tech_indicators.items():
                report += f"- **{indicator}**: {value}\n"

        return report

    def _extract_financial_metrics(self, info: Dict, financials: pd.DataFrame) -> Dict[str, str]:
        """提取关键财务指标"""
        metrics = {}

        # 从基本信息中提取
        metrics['市盈率'] = f"{info.get('trailingPE', 'N/A')}"
        metrics['前瞻市盈率'] = f"{info.get('forwardPE', 'N/A')}"
        metrics['市净率'] = f"{info.get('priceToBook', 'N/A')}"
        metrics['股息率'] = f"{info.get('dividendYield', 0) * 100:.2f}%"
        metrics['Beta'] = f"{info.get('beta', 'N/A')}"

        # 从财务报表中提取
        if not financials.empty:
            try:
                # 根据akshare返回的财务报表格式提取数据
                if '营业收入' in financials.columns:
                    latest_revenue = financials['营业收入'].iloc[0] if len(financials) > 0 else 'N/A'
                    metrics['最新营收'] = f"{latest_revenue:,.2f} 元" if latest_revenue != 'N/A' else 'N/A'
                
                if '净利润' in financials.columns:
                    latest_profit = financials['净利润'].iloc[0] if len(financials) > 0 else 'N/A'
                    metrics['最新净利润'] = f"{latest_profit:,.2f} 元" if latest_profit != 'N/A' else 'N/A'
                
                # 尝试计算一些额外的财务指标
                if '营业收入' in financials.columns and '营业成本' in financials.columns and len(financials) > 0:
                    revenue = financials['营业收入'].iloc[0]
                    cost = financials['营业成本'].iloc[0]
                    if revenue > 0:
                        gross_margin = ((revenue - cost) / revenue) * 100
                        metrics['毛利率'] = f"{gross_margin:.2f}%"
            except Exception as e:
                logger.warning(f"提取财务指标时出错: {str(e)}")
                metrics['最新营收'] = "N/A"
                metrics['最新净利润'] = "N/A"
        else:
            metrics['最新营收'] = "N/A"
            metrics['最新净利润'] = "N/A"

        return metrics

    def _calculate_technical_indicators(self, hist: pd.DataFrame) -> Dict[str, str]:
        """计算技术指标"""
        indicators = {}

        if len(hist) < 20:
            return indicators

        close_prices = hist['Close']

        # 移动平均线
        ma5 = close_prices.rolling(window=5).mean().iloc[-1]
        ma20 = close_prices.rolling(window=20).mean().iloc[-1]
        ma50 = close_prices.rolling(window=50).mean().iloc[-1]

        indicators['MA5'] = f"${ma5:.2f}"
        indicators['MA20'] = f"${ma20:.2f}"
        indicators['MA50'] = f"${ma50:.2f}"

        # RSI
        if len(hist) >= 14:
            rsi = self._calculate_rsi(close_prices)
            indicators['RSI(14)'] = f"{rsi:.1f}"

        # MACD
        if len(hist) >= 26:
            macd, signal = self._calculate_macd(close_prices)
            indicators['MACD'] = f"{macd:.3f}"
            indicators['Signal'] = f"{signal:.3f}"

        return indicators

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]

    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
        """计算MACD指标"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        return macd.iloc[-1], signal_line.iloc[-1]


# 使用示例
if __name__ == "__main__":
    # 测试AkShare工具
    ak_tool = AkShareTool()
    print("=== 测试AkShare工具 ===")
    # 注意：akshare需要A股格式的股票代码
    result = ak_tool._run("sh600000", "6mo")
    print(result[:500] + "...")