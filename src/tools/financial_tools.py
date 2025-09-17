"""
金融数据工具包
包含股票数据获取、财务计算等工具
"""
from crewai_tools import BaseTool
from typing import Dict, Any, List, Optional
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class YFinanceTool(BaseTool):
    """雅虎财经数据工具"""

    name: str = "Yahoo Finance Data Tool"
    description: str = "获取股票的财务数据、价格数据和市场信息"

    def _run(self, ticker: str, period: str = "1y") -> str:
        """
        获取股票数据

        Args:
            ticker: 股票代码
            period: 数据周期 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

        Returns:
            股票数据报告
        """
        try:
            logger.info(f"获取 {ticker} 的数据，周期: {period}")

            # 获取股票对象
            stock = yf.Ticker(ticker)

            # 获取基本信息
            info = stock.info

            # 获取历史价格数据
            hist = stock.history(period=period)

            # 获取财务数据
            financials = stock.financials
            balance_sheet = stock.balance_sheet
            cashflow = stock.cashflow

            # 生成数据报告
            report = self._generate_stock_report(ticker, info, hist, financials, balance_sheet, cashflow)

            logger.info(f"成功获取 {ticker} 的数据")
            return report

        except Exception as e:
            error_msg = f"获取 {ticker} 数据失败: {str(e)}"
            logger.error(error_msg)
            return error_msg

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
        report += f"- **市值**: ${info.get('marketCap', 0):,.0f}\n"
        report += f"- **当前价格**: ${info.get('currentPrice', 0):.2f}\n"
        report += f"- **52周最高**: ${info.get('fiftyTwoWeekHigh', 0):.2f}\n"
        report += f"- **52周最低**: ${info.get('fiftyTwoWeekLow', 0):.2f}\n\n"

        # 价格统计
        if not hist.empty:
            report += "## 价格统计\n\n"
            current_price = hist['Close'].iloc[-1]
            period_return = ((current_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100

            report += f"- **当前价格**: ${current_price:.2f}\n"
            report += f"- **期间涨幅**: {period_return:.2f}%\n"
            report += f"- **期间最高**: ${hist['High'].max():.2f}\n"
            report += f"- **期间最低**: ${hist['Low'].min():.2f}\n"
            report += f"- **平均成交额**: ${hist['Volume'].mean():,.0f}\n\n"

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
            latest_revenue = financials.iloc[0].get('Total Revenue', 0)
            if latest_revenue:
                metrics['最新营收'] = f"${latest_revenue:,.0f}"

            latest_net_income = financials.iloc[0].get('Net Income', 0)
            if latest_net_income:
                metrics['最新净利润'] = f"${latest_net_income:,.0f}"

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


class FinancialCalculatorTool(BaseTool):
    """金融计算器工具"""

    name: str = "Financial Calculator Tool"
    description: str = "计算各种财务指标和比率"

    def _run(self, financial_data: str, calculation_type: str = "all") -> str:
        """
        计算财务指标

        Args:
            financial_data: 财务数据（JSON格式）
            calculation_type: 计算类型 (liquidity, profitability, leverage, growth, all)

        Returns:
            财务指标计算结果
        """
        try:
            import json
            data = json.loads(financial_data)
            logger.info(f"开始计算财务指标，类型: {calculation_type}")

            results = {}

            if calculation_type in ["liquidity", "all"]:
                results['liquidity_ratios'] = self._calculate_liquidity_ratios(data)

            if calculation_type in ["profitability", "all"]:
                results['profitability_ratios'] = self._calculate_profitability_ratios(data)

            if calculation_type in ["leverage", "all"]:
                results['leverage_ratios'] = self._calculate_leverage_ratios(data)

            if calculation_type in ["growth", "all"]:
                results['growth_rates'] = self._calculate_growth_rates(data)

            report = self._generate_financial_report(results)
            logger.info("财务指标计算完成")
            return report

        except Exception as e:
            error_msg = f"财务指标计算失败: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def _calculate_liquidity_ratios(self, data: Dict) -> Dict[str, float]:
        """计算流动性比率"""
        ratios = {}

        try:
            # 流动比率
            current_assets = data.get('current_assets', 0)
            current_liabilities = data.get('current_liabilities', 0)
            if current_liabilities > 0:
                ratios['current_ratio'] = current_assets / current_liabilities

            # 速动比率
            inventory = data.get('inventory', 0)
            quick_assets = current_assets - inventory
            if current_liabilities > 0:
                ratios['quick_ratio'] = quick_assets / current_liabilities

            # 现金比率
            cash = data.get('cash', 0)
            if current_liabilities > 0:
                ratios['cash_ratio'] = cash / current_liabilities

        except Exception as e:
            logger.error(f"计算流动性比率失败: {str(e)}")

        return ratios

    def _calculate_profitability_ratios(self, data: Dict) -> Dict[str, float]:
        """计算盈利能力比率"""
        ratios = {}

        try:
            # 毛利率
            revenue = data.get('revenue', 0)
            gross_profit = data.get('gross_profit', 0)
            if revenue > 0:
                ratios['gross_margin'] = (gross_profit / revenue) * 100

            # 净利率
            net_income = data.get('net_income', 0)
            if revenue > 0:
                ratios['net_margin'] = (net_income / revenue) * 100

            # 资产收益率
            total_assets = data.get('total_assets', 0)
            if total_assets > 0:
                ratios['roa'] = (net_income / total_assets) * 100

            # 净资产收益率
            equity = data.get('equity', 0)
            if equity > 0:
                ratios['roe'] = (net_income / equity) * 100

        except Exception as e:
            logger.error(f"计算盈利能力比率失败: {str(e)}")

        return ratios

    def _calculate_leverage_ratios(self, data: Dict) -> Dict[str, float]:
        """计算杠杆比率"""
        ratios = {}

        try:
            # 资产负债率
            total_assets = data.get('total_assets', 0)
            total_debt = data.get('total_debt', 0)
            if total_assets > 0:
                ratios['debt_to_assets'] = (total_debt / total_assets) * 100

            # 权益乘数
            equity = data.get('equity', 0)
            if equity > 0:
                ratios['equity_multiplier'] = total_assets / equity

            # 利息保障倍数
            ebit = data.get('ebit', 0)
            interest_expense = data.get('interest_expense', 0)
            if interest_expense > 0:
                ratios['interest_coverage'] = ebit / interest_expense

        except Exception as e:
            logger.error(f"计算杠杆比率失败: {str(e)}")

        return ratios

    def _calculate_growth_rates(self, data: Dict) -> Dict[str, float]:
        """计算增长率"""
        rates = {}

        try:
            # 营收增长率
            current_revenue = data.get('current_revenue', 0)
            previous_revenue = data.get('previous_revenue', 0)
            if previous_revenue > 0:
                rates['revenue_growth'] = ((current_revenue - previous_revenue) / previous_revenue) * 100

            # 净利润增长率
            current_net_income = data.get('current_net_income', 0)
            previous_net_income = data.get('previous_net_income', 0)
            if previous_net_income > 0:
                rates['net_income_growth'] = ((current_net_income - previous_net_income) / previous_net_income) * 100

            # 资产增长率
            current_assets = data.get('current_assets', 0)
            previous_assets = data.get('previous_assets', 0)
            if previous_assets > 0:
                rates['asset_growth'] = ((current_assets - previous_assets) / previous_assets) * 100

        except Exception as e:
            logger.error(f"计算增长率失败: {str(e)}")

        return rates

    def _generate_financial_report(self, results: Dict) -> str:
        """生成财务指标报告"""
        report = "# 财务指标分析报告\n\n"
        report += f"**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        for category, ratios in results.items():
            report += f"## {category.replace('_', ' ').title()}\n\n"

            if not ratios:
                report += "无可用数据\n\n"
                continue

            for ratio_name, value in ratios.items():
                ratio_name_chinese = self._translate_ratio_name(ratio_name)
                if 'growth' in ratio_name or 'margin' in ratio_name or ratio_name in ['roa', 'roe']:
                    report += f"- **{ratio_name_chinese}**: {value:.2f}%\n"
                else:
                    report += f"- **{ratio_name_chinese}**: {value:.2f}\n"

            report += "\n"

        # 添加分析建议
        report += self._generate_analysis_suggestions(results)

        return report

    def _translate_ratio_name(self, ratio_name: str) -> str:
        """翻译财务指标名称"""
        translations = {
            'current_ratio': '流动比率',
            'quick_ratio': '速动比率',
            'cash_ratio': '现金比率',
            'gross_margin': '毛利率',
            'net_margin': '净利率',
            'roa': '资产收益率',
            'roe': '净资产收益率',
            'debt_to_assets': '资产负债率',
            'equity_multiplier': '权益乘数',
            'interest_coverage': '利息保障倍数',
            'revenue_growth': '营收增长率',
            'net_income_growth': '净利润增长率',
            'asset_growth': '资产增长率'
        }
        return translations.get(ratio_name, ratio_name)

    def _generate_analysis_suggestions(self, results: Dict) -> str:
        """生成分析建议"""
        suggestions = "## 分析建议\n\n"

        # 流动性分析
        liquidity = results.get('liquidity_ratios', {})
        current_ratio = liquidity.get('current_ratio', 0)
        if current_ratio < 1:
            suggestions += "- **流动性风险**: 流动比率低于1，可能存在短期偿债压力\n"
        elif current_ratio > 2:
            suggestions += "- **资金利用**: 流动比率较高，可考虑提高资金使用效率\n"

        # 盈利能力分析
        profitability = results.get('profitability_ratios', {})
        net_margin = profitability.get('net_margin', 0)
        if net_margin < 5:
            suggestions += "- **盈利能力**: 净利率较低，需要提高盈利能力\n"
        elif net_margin > 20:
            suggestions += "- **盈利能力**: 净利率表现优秀，具有较强的竞争优势\n"

        # 杠杆分析
        leverage = results.get('leverage_ratios', {})
        debt_to_assets = leverage.get('debt_to_assets', 0)
        if debt_to_assets > 70:
            suggestions += "- **财务风险**: 资产负债率较高，财务风险需要关注\n"
        elif debt_to_assets < 30:
            suggestions += "- **财务保守**: 资产负债率较低，可考虑适度增加财务杠杆\n"

        # 增长分析
        growth = results.get('growth_rates', {})
        revenue_growth = growth.get('revenue_growth', 0)
        if revenue_growth > 20:
            suggestions += "- **增长强劲**: 营收增长率较高，业务发展良好\n"
        elif revenue_growth < 0:
            suggestions += "- **增长停滞**: 营收出现负增长，需要关注业务发展\n"

        return suggestions


class MarketDataTool(BaseTool):
    """市场数据工具"""

    name: str = "Market Data Tool"
    description: str = "获取实时市场数据和行业信息"

    def _run(self, query: str, data_type: str = "market_overview") -> str:
        """
        获取市场数据

        Args:
            query: 查询内容
            data_type: 数据类型 (market_overview, sector_performance, etf_flows, market_sentiment)

        Returns:
            市场数据报告
        """
        try:
            logger.info(f"获取市场数据: {query}, 类型: {data_type}")

            if data_type == "market_overview":
                return self._get_market_overview()
            elif data_type == "sector_performance":
                return self._get_sector_performance()
            elif data_type == "market_sentiment":
                return self._get_market_sentiment()
            else:
                return "不支持的数据类型"

        except Exception as e:
            error_msg = f"获取市场数据失败: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def _get_market_overview(self) -> str:
        """获取市场概览"""
        # 这里可以集成实际的市场数据API
        # 目前使用模拟数据

        report = "# 市场概览\n\n"
        report += f"**更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # 主要指数
        report += "## 主要指数表现\n\n"
        indices = {
            "S&P 500": {"price": 4520.35, "change": "+0.85%", "volume": "2.1B"},
            "NASDAQ": {"price": 14113.70, "change": "+1.20%", "volume": "3.2B"},
            "DOW JONES": {"price": 35457.31, "change": "+0.45%", "volume": "1.8B"}
        }

        for index, data in indices.items():
            report += f"- **{index}**: {data['price']} ({data['change']}) - 成交量: {data['volume']}\n"

        # 市场状态
        report += "\n## 市场状态\n\n"
        report += "- **市场情绪**: 积极乐观\n"
        report += "- **波动率**: 中等 (VIX: 16.5)\n"
        report += "- **避险情绪**: 低\n"
        report += "- **资金流向**: 风险资产流入\n"

        return report

    def _get_sector_performance(self) -> str:
        """获取行业表现"""
        report = "# 行业表现分析\n\n"
        report += f"**更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # 行业表现数据
        sectors = {
            "科技": {"performance": "+2.5%", "trend": "强势上涨", "volume": "高"},
            "金融": {"performance": "+0.8%", "trend": "温和上涨", "volume": "中"},
            "医疗": {"performance": "-0.3%", "trend": "弱势整理", "volume": "低"},
            "能源": {"performance": "+1.2%", "trend": "稳步上涨", "volume": "中"},
            "消费品": {"performance": "+0.5%", "trend": "小幅波动", "volume": "中"}
        }

        for sector, data in sectors.items():
            report += f"- **{sector}**: {data['performance']} - {data['trend']} - 成交量: {data['volume']}\n"

        return report

    def _get_market_sentiment(self) -> str:
        """获取市场情绪"""
        report = "# 市场情绪分析\n\n"
        report += f"**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        report += "## 情绪指标\n\n"
        report += "- **恐慌贪婪指数**: 72 (贪婪)\n"
        report += "- **看涨/看跌比例**: 1.8:1\n"
        report += "- **期权看跌/看涨比率**: 0.85\n"
        report += "- **资金流向**: 净流入\n"

        report += "\n## 情绪分析\n\n"
        report += "当前市场情绪偏向乐观，投资者风险偏好较高。技术指标显示市场处于强势状态，但需要注意可能的过度乐观风险。"

        return report


# 使用示例
if __name__ == "__main__":
    # 测试雅虎财经工具
    yf_tool = YFinanceTool()
    print("=== 测试雅虎财经工具 ===")
    result = yf_tool._run("AAPL", "6mo")
    print(result[:500] + "...")

    # 测试金融计算器工具
    calc_tool = FinancialCalculatorTool()
    print("\n=== 测试金融计算器工具 ===")
    test_data = {
        "current_assets": 1000000,
        "current_liabilities": 500000,
        "inventory": 200000,
        "cash": 300000,
        "revenue": 2000000,
        "gross_profit": 800000,
        "net_income": 400000,
        "total_assets": 3000000,
        "equity": 1500000,
        "total_debt": 1000000
    }
    import json
    calc_result = calc_tool._run(json.dumps(test_data))
    print(calc_result)

    # 测试市场数据工具
    market_tool = MarketDataTool()
    print("\n=== 测试市场数据工具 ===")
    market_result = market_tool._run("market", "market_overview")
    print(market_result)