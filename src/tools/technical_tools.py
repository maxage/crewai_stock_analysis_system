"""
技术分析工具包
包含技术指标计算、图表生成等技术分析功能
"""
from crewai import Agent, Task
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import logging

# 自定义工具基类
class BaseTool:
    """工具基类"""
    name: str = "Base Tool"
    description: str = "基础工具类"
    
    def _run(self, *args, **kwargs):
        """运行工具"""
        raise NotImplementedError("子类必须实现_run方法")

# 设置日志配置为DEBUG级别
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


class TechnicalAnalysisTool(BaseTool):
    """技术分析工具"""

    name: str = "Technical Analysis Tool"
    description: str = "计算各种技术指标并生成技术分析报告"

    def _run(self, price_data: str, analysis_type: str = "comprehensive") -> str:
        """
        执行技术分析

        Args:
            price_data: 价格数据（JSON格式，包含OHLCV数据）
            analysis_type: 分析类型 (comprehensive, trend, momentum, volatility, volume)

        Returns:
            技术分析报告
        """
        try:
            # 添加详细的调试日志
            logger.debug(f"[技术分析] 开始分析，价格数据长度: {len(price_data)} 字符, 分析类型: {analysis_type}")
            logger.info(f"开始技术分析，类型: {analysis_type}")

            # 解析价格数据
            import json
            logger.debug(f"[数据处理] 开始解析价格数据")
            data = json.loads(price_data)
            logger.debug(f"[数据处理] 成功解析价格数据，数据点数量: {len(data)}")

            # 转换为DataFrame
            logger.debug(f"[数据处理] 开始转换为DataFrame")
            df = pd.DataFrame(data)
            logger.debug(f"[数据处理] 成功转换为DataFrame，原始列: {', '.join(df.columns)}")
            
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            logger.debug(f"[数据处理] 设置日期索引完成，时间范围: {df.index.min()} 至 {df.index.max()}")

            # 确保数据完整性
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            logger.debug(f"[数据验证] 验证必要列: {', '.join(required_columns)}")
            if not all(col in df.columns for col in required_columns):
                missing = [col for col in required_columns if col not in df.columns]
                logger.debug(f"[数据验证] 缺少必要列: {', '.join(missing)}")
                raise ValueError(f"价格数据缺少必要的列: {', '.join(missing)}")
            logger.debug(f"[数据验证] 数据完整性检查通过")

            results = {}
            logger.debug(f"[分析流程] 开始执行分析流程")

            if analysis_type in ["comprehensive", "trend"]:
                logger.debug(f"[分析模块] 开始趋势指标计算")
                results['trend_indicators'] = self._calculate_trend_indicators(df)
                logger.debug(f"[分析模块] 完成趋势指标计算，指标数量: {len(results['trend_indicators'])}")

            if analysis_type in ["comprehensive", "momentum"]:
                logger.debug(f"[分析模块] 开始动量指标计算")
                results['momentum_indicators'] = self._calculate_momentum_indicators(df)
                logger.debug(f"[分析模块] 完成动量指标计算，指标数量: {len(results['momentum_indicators'])}")

            if analysis_type in ["comprehensive", "volatility"]:
                logger.debug(f"[分析模块] 开始波动性指标计算")
                results['volatility_indicators'] = self._calculate_volatility_indicators(df)
                logger.debug(f"[分析模块] 完成波动性指标计算，指标数量: {len(results['volatility_indicators'])}")

            if analysis_type in ["comprehensive", "volume"]:
                logger.debug(f"[分析模块] 开始成交量指标计算")
                results['volume_indicators'] = self._calculate_volume_indicators(df)
                logger.debug(f"[分析模块] 完成成交量指标计算，指标数量: {len(results['volume_indicators'])}")

            # 生成分析报告
            logger.debug(f"[报告生成] 开始生成技术分析报告，结果类别数量: {len(results)}")
            report = self._generate_technical_report(df, results, analysis_type)
            logger.debug(f"[报告生成] 成功生成分析报告，报告长度: {len(report)} 字符")

            logger.info("技术分析完成")
            return report

        except Exception as e:
            # 添加详细的错误日志
            error_msg = f"技术分析失败: {str(e)}"
            logger.error(error_msg)
            logger.debug(f"[分析错误] 详细信息 - 数据长度: {len(price_data)} 字符, 分析类型: {analysis_type}, 错误类型: {type(e).__name__}, 错误详情: {str(e)}")
            return error_msg

    def _calculate_trend_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """计算趋势指标"""
        indicators = {}

        try:
            # 移动平均线
            indicators['ma_5'] = self._calculate_ma(df['Close'], 5)
            indicators['ma_10'] = self._calculate_ma(df['Close'], 10)
            indicators['ma_20'] = self._calculate_ma(df['Close'], 20)
            indicators['ma_50'] = self._calculate_ma(df['Close'], 50)
            indicators['ma_200'] = self._calculate_ma(df['Close'], 200)

            # MACD
            macd, signal, histogram = self._calculate_macd(df['Close'])
            indicators['macd'] = {
                'macd_line': macd,
                'signal_line': signal,
                'histogram': histogram
            }

            # 布林带
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(df['Close'])
            indicators['bollinger_bands'] = {
                'upper': bb_upper,
                'middle': bb_middle,
                'lower': bb_lower
            }

            # 抛物线SAR
            indicators['sar'] = self._calculate_sar(df['High'], df['Low'], df['Close'])

        except Exception as e:
            logger.error(f"计算趋势指标失败: {str(e)}")

        return indicators

    def _calculate_momentum_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """计算动量指标"""
        indicators = {}

        try:
            # RSI
            indicators['rsi'] = self._calculate_rsi(df['Close'])

            # 随机指标
            k_percent, d_percent = self._calculate_stochastic(df['High'], df['Low'], df['Close'])
            indicators['stochastic'] = {
                'k_percent': k_percent,
                'd_percent': d_percent
            }

            # 威廉指标
            indicators['williams_r'] = self._calculate_williams_r(df['High'], df['Low'], df['Close'])

            # 商品通道指标
            indicators['cci'] = self._calculate_cci(df['High'], df['Low'], df['Close'])

            # 动量指标
            indicators['momentum'] = self._calculate_momentum(df['Close'])

        except Exception as e:
            logger.error(f"计算动量指标失败: {str(e)}")

        return indicators

    def _calculate_volatility_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """计算波动率指标"""
        indicators = {}

        try:
            # 平均真实范围
            indicators['atr'] = self._calculate_atr(df['High'], df['Low'], df['Close'])

            # 布林带宽度
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(df['Close'])
            indicators['bollinger_bandwidth'] = ((bb_upper - bb_lower) / bb_middle) * 100

            # 历史波动率
            indicators['historical_volatility'] = self._calculate_historical_volatility(df['Close'])

        except Exception as e:
            logger.error(f"计算波动率指标失败: {str(e)}")

        return indicators

    def _calculate_volume_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """计算成交量指标"""
        indicators = {}

        try:
            # 成交量移动平均
            indicators['volume_ma_20'] = self._calculate_ma(df['Volume'], 20)

            # 成交量变化率
            indicators['volume_change'] = self._calculate_volume_change(df['Volume'])

            # 能量潮指标
            indicators['obv'] = self._calculate_obv(df['Close'], df['Volume'])

            # 累积/派发线
            indicators['accumulation_distribution'] = self._calculate_accumulation_distribution(
                df['High'], df['Low'], df['Close'], df['Volume']
            )

        except Exception as e:
            logger.error(f"计算成交量指标失败: {str(e)}")

        return indicators

    # 趋势指标计算方法
    def _calculate_ma(self, prices: pd.Series, period: int) -> pd.Series:
        """计算移动平均线"""
        return prices.rolling(window=period).mean()

    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """计算MACD指标"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """计算布林带"""
        ma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = ma + (std * std_dev)
        lower = ma - (std * std_dev)
        return upper, ma, lower

    def _calculate_sar(self, high: pd.Series, low: pd.Series, close: pd.Series,
                      acceleration: float = 0.02, maximum: float = 0.2) -> pd.Series:
        """计算抛物线SAR"""
        # 简化的SAR计算
        sar = pd.Series(index=close.index, dtype=float)
        sar.iloc[0] = low.iloc[0]

        ep = low.iloc[0]  # Extreme Point
        af = acceleration  # Acceleration Factor
        pos_trend = True  # Positive Trend

        for i in range(1, len(close)):
            if pos_trend:
                sar.iloc[i] = sar.iloc[i-1] + af * (ep - sar.iloc[i-1])
                if low.iloc[i] < sar.iloc[i]:
                    pos_trend = False
                    sar.iloc[i] = ep
                    ep = high.iloc[i]
                    af = acceleration
                else:
                    if high.iloc[i] > ep:
                        ep = high.iloc[i]
                        af = min(af + acceleration, maximum)
            else:
                sar.iloc[i] = sar.iloc[i-1] + af * (ep - sar.iloc[i-1])
                if high.iloc[i] > sar.iloc[i]:
                    pos_trend = True
                    sar.iloc[i] = ep
                    ep = low.iloc[i]
                    af = acceleration
                else:
                    if low.iloc[i] < ep:
                        ep = low.iloc[i]
                        af = min(af + acceleration, maximum)

        return sar

    # 动量指标计算方法
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series,
                            k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        """计算随机指标"""
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()
        return k_percent, d_percent

    def _calculate_williams_r(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """计算威廉指标"""
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()
        williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
        return williams_r

    def _calculate_cci(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> pd.Series:
        """计算商品通道指标"""
        tp = (high + low + close) / 3  # Typical Price
        sma_tp = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(lambda x: np.fabs(x - x.mean()).mean())
        cci = (tp - sma_tp) / (0.015 * mad)
        return cci

    def _calculate_momentum(self, prices: pd.Series, period: int = 10) -> pd.Series:
        """计算动量指标"""
        return prices.diff(period)

    # 波动率指标计算方法
    def _calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """计算平均真实范围"""
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        tr = np.maximum(high_low, np.maximum(high_close, low_close))
        atr = tr.rolling(window=period).mean()
        return atr

    def _calculate_historical_volatility(self, prices: pd.Series, period: int = 20) -> pd.Series:
        """计算历史波动率"""
        returns = np.log(prices / prices.shift(1))
        volatility = returns.rolling(window=period).std() * np.sqrt(252)
        return volatility * 100

    # 成交量指标计算方法
    def _calculate_volume_change(self, volume: pd.Series) -> pd.Series:
        """计算成交量变化率"""
        return volume.pct_change() * 100

    def _calculate_obv(self, close: pd.Series, volume: pd.Series) -> pd.Series:
        """计算能量潮指标"""
        obv = np.where(close > close.shift(), volume, np.where(close < close.shift(), -volume, 0))
        return pd.Series(obv, index=close.index).cumsum()

    def _calculate_accumulation_distribution(self, high: pd.Series, low: pd.Series,
                                           close: pd.Series, volume: pd.Series) -> pd.Series:
        """计算累积/派发线"""
        clv = ((close - low) - (high - close)) / (high - low)
        clv = clv.fillna(0)
        ad = clv * volume
        return ad.cumsum()

    def _generate_technical_report(self, df: pd.DataFrame, results: Dict, analysis_type: str) -> str:
        """生成技术分析报告"""
        report = f"# 技术分析报告\n\n"
        report += f"**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"**数据期间**: {df.index[0].strftime('%Y-%m-%d')} 至 {df.index[-1].strftime('%Y-%m-%d')}\n"
        report += f"**当前价格**: ${df['Close'].iloc[-1]:.2f}\n\n"

        # 趋势分析
        if 'trend_indicators' in results:
            report += self._generate_trend_analysis(df, results['trend_indicators'])

        # 动量分析
        if 'momentum_indicators' in results:
            report += self._generate_momentum_analysis(results['momentum_indicators'])

        # 波动率分析
        if 'volatility_indicators' in results:
            report += self._generate_volatility_analysis(results['volatility_indicators'])

        # 成交量分析
        if 'volume_indicators' in results:
            report += self._generate_volume_analysis(df, results['volume_indicators'])

        # 综合建议
        report += self._generate_trading_recommendations(results)

        return report

    def _generate_trend_analysis(self, df: pd.DataFrame, indicators: Dict) -> str:
        """生成趋势分析"""
        analysis = "## 趋势分析\n\n"

        # 移动平均线分析
        current_price = df['Close'].iloc[-1]
        ma_20 = indicators['ma_20'].iloc[-1]
        ma_50 = indicators['ma_50'].iloc[-1]

        analysis += "### 移动平均线\n"
        analysis += f"- 当前价格: ${current_price:.2f}\n"
        analysis += f"- MA20: ${ma_20:.2f}\n"
        analysis += f"- MA50: ${ma_50:.2f}\n"

        if current_price > ma_20 > ma_50:
            analysis += "- **趋势判断**: 强势上涨\n"
        elif current_price > ma_20 and ma_20 < ma_50:
            analysis += "- **趋势判断**: 短期反弹\n"
        elif current_price < ma_20 < ma_50:
            analysis += "- **趋势判断**: 弱势下跌\n"
        else:
            analysis += "- **趋势判断**: 震荡整理\n"

        # MACD分析
        macd_data = indicators['macd']
        macd_current = macd_data['macd_line'].iloc[-1]
        signal_current = macd_data['signal_line'].iloc[-1]

        analysis += "\n### MACD指标\n"
        analysis += f"- MACD线: {macd_current:.3f}\n"
        analysis += f"- 信号线: {signal_current:.3f}\n"

        if macd_current > signal_current:
            analysis += "- **信号**: 看涨信号\n"
        else:
            analysis += "- **信号**: 看跌信号\n"

        return analysis

    def _generate_momentum_analysis(self, indicators: Dict) -> str:
        """生成动量分析"""
        analysis = "\n## 动量分析\n\n"

        # RSI分析
        rsi_current = indicators['rsi'].iloc[-1]
        analysis += "### RSI指标\n"
        analysis += f"- RSI(14): {rsi_current:.1f}\n"

        if rsi_current > 70:
            analysis += "- **状态**: 超买区域\n"
        elif rsi_current < 30:
            analysis += "- **状态**: 超卖区域\n"
        else:
            analysis += "- **状态**: 正常区域\n"

        # 随机指标分析
        stochastic_data = indicators['stochastic']
        k_current = stochastic_data['k_percent'].iloc[-1]
        d_current = stochastic_data['d_percent'].iloc[-1]

        analysis += "\n### 随机指标\n"
        analysis += f"- %K: {k_current:.1f}\n"
        analysis += f"- %D: {d_current:.1f}\n"

        if k_current > 80:
            analysis += "- **信号**: 超买信号\n"
        elif k_current < 20:
            analysis += "- **信号**: 超卖信号\n"

        return analysis

    def _generate_volatility_analysis(self, indicators: Dict) -> str:
        """生成波动率分析"""
        analysis = "\n## 波动率分析\n\n"

        # ATR分析
        atr_current = indicators['atr'].iloc[-1]
        analysis += "### 平均真实范围 (ATR)\n"
        analysis += f"- ATR(14): {atr_current:.2f}\n"

        # 布林带分析
        bb_width = indicators['bollinger_bandwidth'].iloc[-1]
        analysis += "\n### 布林带\n"
        analysis += f"- 带宽: {bb_width:.1f}%\n"

        if bb_width > 20:
            analysis += "- **波动状态**: 高波动\n"
        elif bb_width < 10:
            analysis += "- **波动状态**: 低波动\n"
        else:
            analysis += "- **波动状态**: 正常波动\n"

        return analysis

    def _generate_volume_analysis(self, df: pd.DataFrame, indicators: Dict) -> str:
        """生成成交量分析"""
        analysis = "\n## 成交量分析\n\n"

        # 成交量变化分析
        volume_change = indicators['volume_change'].iloc[-1]
        analysis += "### 成交量变化\n"
        analysis += f"- 成交量变化率: {volume_change:+.1f}%\n"

        if volume_change > 50:
            analysis += "- **成交量状态**: 显著放量\n"
        elif volume_change < -30:
            analysis += "- **成交量状态**: 明显缩量\n"
        else:
            analysis += "- **成交量状态**: 正常水平\n"

        # OBV分析
        obv_current = indicators['obv'].iloc[-1]
        obv_prev = indicators['obv'].iloc[-2]

        analysis += "\n### 能量潮指标\n"
        if obv_current > obv_prev:
            analysis += "- **资金流向**: 资金流入\n"
        else:
            analysis += "- **资金流向**: 资金流出\n"

        return analysis

    def _generate_trading_recommendations(self, results: Dict) -> str:
        """生成交易建议"""
        recommendations = "\n## 综合交易建议\n\n"

        signals = []

        # 趋势信号
        if 'trend_indicators' in results:
            macd_data = results['trend_indicators']['macd']
            if macd_data['macd_line'].iloc[-1] > macd_data['signal_line'].iloc[-1]:
                signals.append("MACD看涨信号")
            else:
                signals.append("MACD看跌信号")

        # 动量信号
        if 'momentum_indicators' in results:
            rsi = results['momentum_indicators']['rsi'].iloc[-1]
            if rsi > 70:
                signals.append("RSI超买警告")
            elif rsi < 30:
                signals.append("RSI超卖机会")

        # 综合评级
        buy_signals = len([s for s in signals if '看涨' in s or '机会' in s])
        sell_signals = len([s for s in signals if '看跌' in s or '警告' in s])

        recommendations += "### 信号汇总\n"
        for signal in signals:
            recommendations += f"- {signal}\n"

        recommendations += "\n### 投资建议\n"
        if buy_signals > sell_signals:
            recommendations += "- **建议**: 适度看涨，可考虑逢低买入\n"
        elif sell_signals > buy_signals:
            recommendations += "- **建议**: 谨慎观望，注意风险控制\n"
        else:
            recommendations += "- **建议**: 中性观望，等待更明确信号\n"

        return recommendations


class ChartingTool(BaseTool):
    """图表生成工具"""

    name: str = "Charting Tool"
    description: str = "生成技术分析图表和可视化"

    def _run(self, price_data: str, chart_type: str = "candlestick") -> str:
        """
        生成技术分析图表

        Args:
            price_data: 价格数据（JSON格式）
            chart_type: 图表类型 (candlestick, line, volume, indicators)

        Returns:
            图表文件路径
        """
        try:
            import json
            data = json.loads(price_data)
            logger.info(f"生成图表，类型: {chart_type}")

            # 转换为DataFrame
            df = pd.DataFrame(data)
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)

            # 确保reports目录存在
            import os
            os.makedirs('reports/charts', exist_ok=True)

            # 生成图表
            if chart_type == "candlestick":
                filepath = self._generate_candlestick_chart(df)
            elif chart_type == "line":
                filepath = self._generate_line_chart(df)
            elif chart_type == "volume":
                filepath = self._generate_volume_chart(df)
            elif chart_type == "indicators":
                filepath = self._generate_indicators_chart(df)
            else:
                raise ValueError("不支持的图表类型")

            logger.info(f"图表生成完成: {filepath}")
            return filepath

        except Exception as e:
            error_msg = f"生成图表失败: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def _generate_candlestick_chart(self, df: pd.DataFrame) -> str:
        """生成K线图"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})

        # K线图
        from mplfinance.original_flavor import candlestick_ohlc
        ohlc = df[['Open', 'High', 'Low', 'Close']].copy()
        ohlc['Date'] = range(len(ohlc))
        candlestick_ohlc(ax1, ohlc.values, width=0.6, colorup='g', colordown='r')
        ax1.set_title('K线图')
        ax1.set_ylabel('价格')
        ax1.grid(True)

        # 成交量
        ax2.bar(df.index, df['Volume'], color='blue', alpha=0.6)
        ax2.set_title('成交量')
        ax2.set_ylabel('成交量')
        ax2.grid(True)

        plt.tight_layout()

        # 保存图表
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = f'reports/charts/candlestick_{timestamp}.png'
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return filepath

    def _generate_line_chart(self, df: pd.DataFrame) -> str:
        """生成价格走势图"""
        fig, ax = plt.subplots(figsize=(12, 6))

        # 价格线
        ax.plot(df.index, df['Close'], label='收盘价', color='blue', linewidth=2)
        ax.plot(df.index, df['Close'].rolling(window=20).mean(), label='MA20', color='orange', linewidth=1)
        ax.plot(df.index, df['Close'].rolling(window=50).mean(), label='MA50', color='red', linewidth=1)

        ax.set_title('价格走势图')
        ax.set_xlabel('日期')
        ax.set_ylabel('价格')
        ax.legend()
        ax.grid(True)

        plt.tight_layout()

        # 保存图表
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = f'reports/charts/line_{timestamp}.png'
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return filepath

    def _generate_volume_chart(self, df: pd.DataFrame) -> str:
        """生成成交量图"""
        fig, ax = plt.subplots(figsize=(12, 6))

        # 成交量柱状图
        colors = ['green' if close >= open else 'red' for close, open in zip(df['Close'], df['Open'])]
        ax.bar(df.index, df['Volume'], color=colors, alpha=0.6)

        # 成交量移动平均
        ax.plot(df.index, df['Volume'].rolling(window=20).mean(), label='成交量MA20', color='blue', linewidth=2)

        ax.set_title('成交量分析图')
        ax.set_xlabel('日期')
        ax.set_ylabel('成交量')
        ax.legend()
        ax.grid(True)

        plt.tight_layout()

        # 保存图表
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = f'reports/charts/volume_{timestamp}.png'
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return filepath

    def _generate_indicators_chart(self, df: pd.DataFrame) -> str:
        """生成技术指标图"""
        fig, axes = plt.subplots(4, 1, figsize=(12, 12))

        # 价格和移动平均线
        axes[0].plot(df.index, df['Close'], label='收盘价', color='black', linewidth=1)
        axes[0].plot(df.index, df['Close'].rolling(window=20).mean(), label='MA20', color='blue', linewidth=1)
        axes[0].plot(df.index, df['Close'].rolling(window=50).mean(), label='MA50', color='red', linewidth=1)
        axes[0].set_title('价格和移动平均线')
        axes[0].legend()
        axes[0].grid(True)

        # RSI
        rsi = self._calculate_rsi(df['Close'])
        axes[1].plot(df.index, rsi, label='RSI', color='purple', linewidth=1)
        axes[1].axhline(y=70, color='red', linestyle='--', alpha=0.5)
        axes[1].axhline(y=30, color='green', linestyle='--', alpha=0.5)
        axes[1].set_title('RSI指标')
        axes[1].legend()
        axes[1].grid(True)

        # MACD
        macd, signal, histogram = self._calculate_macd(df['Close'])
        axes[2].plot(df.index, macd, label='MACD', color='blue', linewidth=1)
        axes[2].plot(df.index, signal, label='Signal', color='red', linewidth=1)
        axes[2].bar(df.index, histogram, label='Histogram', color='gray', alpha=0.5)
        axes[2].set_title('MACD指标')
        axes[2].legend()
        axes[2].grid(True)

        # 成交量
        axes[3].bar(df.index, df['Volume'], color='blue', alpha=0.6)
        axes[3].set_title('成交量')
        axes[3].grid(True)

        plt.tight_layout()

        # 保存图表
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = f'reports/charts/indicators_{timestamp}.png'
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return filepath

    # 重用技术分析方法
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """计算MACD指标"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram


# 使用示例
if __name__ == "__main__":
    # 创建模拟价格数据
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    prices = np.random.normal(100, 5, len(dates)).cumsum()
    test_data = []
    for i, date in enumerate(dates):
        test_data.append({
            'Date': date.strftime('%Y-%m-%d'),
            'Open': prices[i] + np.random.normal(0, 1),
            'High': prices[i] + abs(np.random.normal(0, 2)),
            'Low': prices[i] - abs(np.random.normal(0, 2)),
            'Close': prices[i],
            'Volume': int(np.random.normal(1000000, 200000))
        })

    # 测试技术分析工具
    tech_tool = TechnicalAnalysisTool()
    print("=== 测试技术分析工具 ===")
    import json
    result = tech_tool._run(json.dumps(test_data), "comprehensive")
    print(result)

    # 测试图表工具
    chart_tool = ChartingTool()
    print("\n=== 测试图表工具 ===")
    chart_result = chart_tool._run(json.dumps(test_data), "candlestick")
    print(f"图表生成: {chart_result}")