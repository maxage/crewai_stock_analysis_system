"""
基本面分析工具
包含公司基本面评估、价值分析等功能
"""
from crewai import Agent, Task
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
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


class FundamentalAnalysisTool(BaseTool):
    """基本面分析工具"""

    name: str = "Fundamental Analysis Tool"
    description: str = "进行公司基本面分析和价值评估"

    def _run(self, company_data: str, analysis_type: str = "comprehensive") -> str:
        """
        执行基本面分析

        Args:
            company_data: 公司数据（JSON格式）
            analysis_type: 分析类型 (comprehensive, valuation, growth, quality)

        Returns:
            基本面分析报告
        """
        try:
            # 添加详细的调试日志
            logger.debug(f"[基本面分析] 开始分析，公司数据长度: {len(company_data)} 字符, 分析类型: {analysis_type}")
            logger.info(f"开始基本面分析，类型: {analysis_type}")
            
            # 解析公司数据
            logger.debug(f"[数据处理] 开始解析公司数据")
            data = json.loads(company_data)
            logger.debug(f"[数据处理] 成功解析公司数据，包含字段: {', '.join(data.keys())}")

            results = {}
            logger.debug(f"[分析流程] 开始执行分析流程")

            if analysis_type in ["comprehensive", "valuation"]:
                logger.debug(f"[分析模块] 开始估值分析")
                results['valuation_analysis'] = self._analyze_valuation(data)
                logger.debug(f"[分析模块] 完成估值分析")

            if analysis_type in ["comprehensive", "growth"]:
                logger.debug(f"[分析模块] 开始增长分析")
                results['growth_analysis'] = self._analyze_growth(data)
                logger.debug(f"[分析模块] 完成增长分析")

            if analysis_type in ["comprehensive", "quality"]:
                logger.debug(f"[分析模块] 开始质量分析")
                results['quality_analysis'] = self._analyze_quality(data)
                logger.debug(f"[分析模块] 完成质量分析")

            if analysis_type in ["comprehensive", "financial_health"]:
                logger.debug(f"[分析模块] 开始财务健康分析")
                results['financial_health'] = self._analyze_financial_health(data)
                logger.debug(f"[分析模块] 完成财务健康分析")

            # 生成分析报告
            logger.debug(f"[报告生成] 开始生成基本面分析报告，分析结果数量: {len(results)}")
            report = self._generate_fundamental_report(results, analysis_type)
            logger.debug(f"[报告生成] 成功生成分析报告，报告长度: {len(report)} 字符")

            logger.info("基本面分析完成")
            return report

        except Exception as e:
            # 添加详细的错误日志
            error_msg = f"基本面分析失败: {str(e)}"
            logger.error(error_msg)
            logger.debug(f"[分析错误] 详细信息 - 数据长度: {len(company_data)} 字符, 分析类型: {analysis_type}, 错误类型: {type(e).__name__}, 错误详情: {str(e)}")
            return error_msg

    def _analyze_valuation(self, data: Dict) -> Dict[str, Any]:
        """分析估值水平"""
        valuation = {}

        try:
            # 市盈率分析
            pe_ratio = data.get('pe_ratio', 0)
            industry_pe = data.get('industry_pe', 0)

            if pe_ratio > 0 and industry_pe > 0:
                valuation['pe_analysis'] = {
                    'current_pe': pe_ratio,
                    'industry_pe': industry_pe,
                    'relative_valuation': '高估' if pe_ratio > industry_pe * 1.2 else '低估' if pe_ratio < industry_pe * 0.8 else '合理'
                }

            # 市净率分析
            pb_ratio = data.get('pb_ratio', 0)
            industry_pb = data.get('industry_pb', 0)

            if pb_ratio > 0 and industry_pb > 0:
                valuation['pb_analysis'] = {
                    'current_pb': pb_ratio,
                    'industry_pb': industry_pb,
                    'relative_valuation': '高估' if pb_ratio > industry_pb * 1.2 else '低估' if pb_ratio < industry_pb * 0.8 else '合理'
                }

            # 市销率分析
            ps_ratio = data.get('ps_ratio', 0)
            if ps_ratio > 0:
                valuation['ps_analysis'] = {
                    'current_ps': ps_ratio,
                    'assessment': '较高' if ps_ratio > 5 else '合理' if ps_ratio > 1 else '较低'
                }

            # DCF估值
            dcf_value = self._calculate_dcf_valuation(data)
            if dcf_value:
                valuation['dcf_analysis'] = dcf_value

        except Exception as e:
            logger.error(f"估值分析失败: {str(e)}")

        return valuation

    def _analyze_growth(self, data: Dict) -> Dict[str, Any]:
        """分析成长性"""
        growth = {}

        try:
            # 营收增长
            revenue_growth = data.get('revenue_growth', 0)
            growth['revenue_growth'] = {
                'rate': revenue_growth,
                'assessment': '高增长' if revenue_growth > 20 else '中等增长' if revenue_growth > 10 else '低增长'
            }

            # 净利润增长
            net_income_growth = data.get('net_income_growth', 0)
            growth['net_income_growth'] = {
                'rate': net_income_growth,
                'assessment': '高增长' if net_income_growth > 25 else '中等增长' if net_income_growth > 10 else '低增长'
            }

            # 每股收益增长
            eps_growth = data.get('eps_growth', 0)
            growth['eps_growth'] = {
                'rate': eps_growth,
                'assessment': '高增长' if eps_growth > 20 else '中等增长' if eps_growth > 10 else '低增长'
            }

            # 历史增长趋势
            growth_trend = self._analyze_growth_trend(data)
            if growth_trend:
                growth['growth_trend'] = growth_trend

        except Exception as e:
            logger.error(f"成长性分析失败: {str(e)}")

        return growth

    def _analyze_quality(self, data: Dict) -> Dict[str, Any]:
        """分析公司质量"""
        quality = {}

        try:
            # 盈利能力
            roe = data.get('roe', 0)
            roa = data.get('roa', 0)
            gross_margin = data.get('gross_margin', 0)

            quality['profitability'] = {
                'roe': roe,
                'roe_assessment': '优秀' if roe > 15 else '良好' if roe > 10 else '一般',
                'roa': roa,
                'roa_assessment': '优秀' if roa > 8 else '良好' if roa > 5 else '一般',
                'gross_margin': gross_margin,
                'margin_assessment': '优秀' if gross_margin > 50 else '良好' if gross_margin > 30 else '一般'
            }

            # 财务健康度
            current_ratio = data.get('current_ratio', 0)
            debt_to_equity = data.get('debt_to_equity', 0)

            quality['financial_health'] = {
                'current_ratio': current_ratio,
                'liquidity_assessment': '优秀' if current_ratio > 2 else '良好' if current_ratio > 1.5 else '一般',
                'debt_to_equity': debt_to_equity,
                'leverage_assessment': '保守' if debt_to_equity < 0.5 else '适中' if debt_to_equity < 1 else '激进'
            }

            # 管理效率
            asset_turnover = data.get('asset_turnover', 0)
            inventory_turnover = data.get('inventory_turnover', 0)

            quality['efficiency'] = {
                'asset_turnover': asset_turnover,
                'efficiency_assessment': '高效' if asset_turnover > 1.5 else '一般' if asset_turnover > 0.8 else '低效',
                'inventory_turnover': inventory_turnover,
                'inventory_assessment': '高效' if inventory_turnover > 8 else '一般' if inventory_turnover > 4 else '低效'
            }

        except Exception as e:
            logger.error(f"质量分析失败: {str(e)}")

        return quality

    def _analyze_financial_health(self, data: Dict) -> Dict[str, Any]:
        """分析财务健康度"""
        health = {}

        try:
            # 流动性分析
            current_ratio = data.get('current_ratio', 0)
            quick_ratio = data.get('quick_ratio', 0)
            cash_ratio = data.get('cash_ratio', 0)

            health['liquidity'] = {
                'current_ratio': current_ratio,
                'quick_ratio': quick_ratio,
                'cash_ratio': cash_ratio,
                'overall_liquidity': '优秀' if current_ratio > 2 else '良好' if current_ratio > 1.5 else '一般' if current_ratio > 1 else '较差'
            }

            # 杠杆分析
            debt_to_equity = data.get('debt_to_equity', 0)
            debt_to_assets = data.get('debt_to_assets', 0)
            interest_coverage = data.get('interest_coverage', 0)

            health['leverage'] = {
                'debt_to_equity': debt_to_equity,
                'debt_to_assets': debt_to_assets,
                'interest_coverage': interest_coverage,
                'leverage_assessment': '保守' if debt_to_equity < 0.5 else '适中' if debt_to_equity < 1 else '激进'
            }

            # 盈利能力
            operating_margin = data.get('operating_margin', 0)
            net_margin = data.get('net_margin', 0)
            return_on_equity = data.get('roe', 0)

            health['profitability'] = {
                'operating_margin': operating_margin,
                'net_margin': net_margin,
                'roe': return_on_equity,
                'profitability_assessment': '优秀' if return_on_equity > 15 else '良好' if return_on_equity > 10 else '一般'
            }

        except Exception as e:
            logger.error(f"财务健康度分析失败: {str(e)}")

        return health

    def _calculate_dcf_valuation(self, data: Dict) -> Optional[Dict[str, Any]]:
        """计算DCF估值"""
        try:
            # 简化的DCF计算
            current_fcf = data.get('free_cash_flow', 0)
            growth_rate = data.get('growth_rate', 0.05)
            discount_rate = data.get('discount_rate', 0.10)
            terminal_growth_rate = 0.03

            if current_fcf <= 0:
                return None

            # 5年FCF预测
            fcf_projections = []
            for year in range(1, 6):
                fcf = current_fcf * (1 + growth_rate) ** year
                fcf_projections.append(fcf)

            # 计算现值
            present_values = []
            for i, fcf in enumerate(fcf_projections):
                pv = fcf / ((1 + discount_rate) ** (i + 1))
                present_values.append(pv)

            # 终值计算
            terminal_fcf = fcf_projections[-1] * (1 + terminal_growth_rate)
            terminal_value = terminal_fcf / (discount_rate - terminal_growth_rate)
            terminal_pv = terminal_value / ((1 + discount_rate) ** 5)

            # 总估值
            total_value = sum(present_values) + terminal_pv

            return {
                'fcf_projections': fcf_projections,
                'present_values': present_values,
                'terminal_value': terminal_value,
                'total_value': total_value,
                'assumptions': {
                    'growth_rate': growth_rate,
                    'discount_rate': discount_rate,
                    'terminal_growth_rate': terminal_growth_rate
                }
            }

        except Exception as e:
            logger.error(f"DCF估值计算失败: {str(e)}")
            return None

    def _analyze_growth_trend(self, data: Dict) -> Optional[Dict[str, Any]]:
        """分析增长趋势"""
        try:
            # 获取历史数据
            historical_revenue = data.get('historical_revenue', [])
            historical_net_income = data.get('historical_net_income', [])

            if len(historical_revenue) < 3:
                return None

            # 计算增长率
            revenue_growth_rates = []
            for i in range(1, len(historical_revenue)):
                growth_rate = (historical_revenue[i] - historical_revenue[i-1]) / historical_revenue[i-1] * 100
                revenue_growth_rates.append(growth_rate)

            # 计算平均增长率
            avg_growth_rate = sum(revenue_growth_rates) / len(revenue_growth_rates)

            # 分析趋势
            trend = '稳定增长' if all(g > 0 for g in revenue_growth_rates[-3:]) else '波动增长'

            return {
                'revenue_growth_rates': revenue_growth_rates,
                'average_growth_rate': avg_growth_rate,
                'trend': trend
            }

        except Exception as e:
            logger.error(f"增长趋势分析失败: {str(e)}")
            return None

    def _generate_fundamental_report(self, results: Dict, analysis_type: str) -> str:
        """生成基本面分析报告"""
        report = f"# 基本面分析报告\n\n"
        report += f"**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"**分析类型**: {analysis_type}\n\n"

        # 估值分析
        if 'valuation_analysis' in results:
            report += self._generate_valuation_section(results['valuation_analysis'])

        # 成长性分析
        if 'growth_analysis' in results:
            report += self._generate_growth_section(results['growth_analysis'])

        # 质量分析
        if 'quality_analysis' in results:
            report += self._generate_quality_section(results['quality_analysis'])

        # 财务健康度分析
        if 'financial_health' in results:
            report += self._generate_financial_health_section(results['financial_health'])

        # 综合评估
        report += self._generate_overall_assessment(results)

        return report

    def _generate_valuation_section(self, valuation: Dict) -> str:
        """生成估值分析部分"""
        section = "## 估值分析\n\n"

        if 'pe_analysis' in valuation:
            pe = valuation['pe_analysis']
            section += f"### 市盈率分析\n"
            section += f"- 当前市盈率: {pe['current_pe']}\n"
            section += f"- 行业平均: {pe['industry_pe']}\n"
            section += f"- 估值状态: {pe['relative_valuation']}\n\n"

        if 'pb_analysis' in valuation:
            pb = valuation['pb_analysis']
            section += f"### 市净率分析\n"
            section += f"- 当前市净率: {pb['current_pb']}\n"
            section += f"- 行业平均: {pb['industry_pb']}\n"
            section += f"- 估值状态: {pb['relative_valuation']}\n\n"

        if 'dcf_analysis' in valuation:
            dcf = valuation['dcf_analysis']
            section += f"### DCF估值\n"
            section += f"- 估值结果: ${dcf['total_value']:,.2f}\n"
            section += f"- 增长率假设: {dcf['assumptions']['growth_rate']*100:.1f}%\n"
            section += f"- 折现率: {dcf['assumptions']['discount_rate']*100:.1f}%\n\n"

        return section

    def _generate_growth_section(self, growth: Dict) -> str:
        """生成成长性分析部分"""
        section = "## 成长性分析\n\n"

        if 'revenue_growth' in growth:
            rev = growth['revenue_growth']
            section += f"### 营收增长\n"
            section += f"- 增长率: {rev['rate']:.1f}%\n"
            section += f"- 评估: {rev['assessment']}\n\n"

        if 'net_income_growth' in growth:
            net = growth['net_income_growth']
            section += f"### 净利润增长\n"
            section += f"- 增长率: {net['rate']:.1f}%\n"
            section += f"- 评估: {net['assessment']}\n\n"

        if 'growth_trend' in growth:
            trend = growth['growth_trend']
            section += f"### 增长趋势\n"
            section += f"- 平均增长率: {trend['average_growth_rate']:.1f}%\n"
            section += f"- 趋势特征: {trend['trend']}\n\n"

        return section

    def _generate_quality_section(self, quality: Dict) -> str:
        """生成质量分析部分"""
        section = "## 质量分析\n\n"

        if 'profitability' in quality:
            profit = quality['profitability']
            section += f"### 盈利能力\n"
            section += f"- 净资产收益率: {profit['roe']:.1f}% ({profit['roe_assessment']})\n"
            section += f"- 总资产收益率: {profit['roa']:.1f}% ({profit['roa_assessment']})\n"
            section += f"- 毛利率: {profit['gross_margin']:.1f}% ({profit['margin_assessment']})\n\n"

        if 'efficiency' in quality:
            efficiency = quality['efficiency']
            section += f"### 运营效率\n"
            section += f"- 资产周转率: {efficiency['asset_turnover']:.2f} ({efficiency['efficiency_assessment']})\n"
            section += f"- 库存周转率: {efficiency['inventory_turnover']:.1f} ({efficiency['inventory_assessment']})\n\n"

        return section

    def _generate_financial_health_section(self, health: Dict) -> str:
        """生成财务健康度部分"""
        section = "## 财务健康度\n\n"

        if 'liquidity' in health:
            liquidity = health['liquidity']
            section += f"### 流动性\n"
            section += f"- 流动比率: {liquidity['current_ratio']:.2f}\n"
            section += f"- 速动比率: {liquidity['quick_ratio']:.2f}\n"
            section += f"- 现金比率: {liquidity['cash_ratio']:.2f}\n"
            section += f"- 整体评估: {liquidity['overall_liquidity']}\n\n"

        if 'leverage' in health:
            leverage = health['leverage']
            section += f"### 杠杆水平\n"
            section += f"- 资产负债率: {leverage['debt_to_equity']:.2f}\n"
            section += f"- 负债资产比: {leverage['debt_to_assets']:.1f}%\n"
            section += f"- 利息保障倍数: {leverage['interest_coverage']:.1f}\n"
            section += f"- 杠杆评估: {leverage['leverage_assessment']}\n\n"

        return section

    def _generate_overall_assessment(self, results: Dict) -> str:
        """生成综合评估"""
        assessment = "## 综合评估\n\n"

        # 计算综合评分
        score = self._calculate_fundamental_score(results)
        assessment += f"### 基本面评分\n"
        assessment += f"- 综合评分: {score:.1f}/100\n"

        # 评估等级
        if score >= 80:
            grade = "优秀"
            outlook = "强烈看好"
        elif score >= 70:
            grade = "良好"
            outlook = "看好"
        elif score >= 60:
            grade = "一般"
            outlook = "中性"
        else:
            grade = "较差"
            outlook = "看淡"

        assessment += f"- 评估等级: {grade}\n"
        assessment += f"- 投资展望: {outlook}\n\n"

        # 关键发现
        assessment += "### 关键发现\n"
        assessment += "- " + self._generate_key_findings(results) + "\n"

        # 投资建议
        assessment += "### 投资建议\n"
        if score >= 70:
            assessment += "- 基于基本面分析，该股票具有良好的投资价值\n"
            assessment += "- 建议关注估值回调机会进行适当配置\n"
        elif score >= 60:
            assessment += "- 基本面表现一般，需要结合其他因素综合判断\n"
            assessment += "- 建议观望，等待更好的投资时机\n"
        else:
            assessment += "- 基本面存在明显问题，建议谨慎对待\n"
            assessment += "- 需要深入分析风险因素\n"

        return assessment

    def _calculate_fundamental_score(self, results: Dict) -> float:
        """计算基本面综合评分"""
        score = 50.0  # 基础分

        # 估值评分 (0-20分)
        if 'valuation_analysis' in results:
            valuation = results['valuation_analysis']
            if 'pe_analysis' in valuation:
                pe_valuation = valuation['pe_analysis']['relative_valuation']
                if pe_valuation == '低估':
                    score += 15
                elif pe_valuation == '合理':
                    score += 10
                elif pe_valuation == '高估':
                    score += 5

        # 成长性评分 (0-30分)
        if 'growth_analysis' in results:
            growth = results['growth_analysis']
            if 'revenue_growth' in growth:
                rev_rate = growth['revenue_growth']['rate']
                if rev_rate > 20:
                    score += 25
                elif rev_rate > 10:
                    score += 20
                elif rev_rate > 5:
                    score += 15
                else:
                    score += 10

        # 质量评分 (0-30分)
        if 'quality_analysis' in results:
            quality = results['quality_analysis']
            if 'profitability' in quality:
                roe = quality['profitability']['roe']
                if roe > 15:
                    score += 25
                elif roe > 10:
                    score += 20
                elif roe > 5:
                    score += 15
                else:
                    score += 10

        # 财务健康度评分 (0-20分)
        if 'financial_health' in results:
            health = results['financial_health']
            if 'liquidity' in health:
                current_ratio = health['liquidity']['current_ratio']
                if current_ratio > 2:
                    score += 15
                elif current_ratio > 1.5:
                    score += 10
                elif current_ratio > 1:
                    score += 5

        return min(100, max(0, score))

    def _generate_key_findings(self, results: Dict) -> str:
        """生成关键发现"""
        findings = []

        if 'valuation_analysis' in results:
            valuation = results['valuation_analysis']
            if 'pe_analysis' in valuation:
                pe_valuation = valuation['pe_analysis']['relative_valuation']
                findings.append(f"估值水平{pe_valuation}")

        if 'growth_analysis' in results:
            growth = results['growth_analysis']
            if 'revenue_growth' in growth:
                rev_assessment = growth['revenue_growth']['assessment']
                findings.append(f"营收增长{rev_assessment}")

        if 'quality_analysis' in results:
            quality = results['quality_analysis']
            if 'profitability' in quality:
                roe_assessment = quality['profitability']['roe_assessment']
                findings.append(f"盈利能力{roe_assessment}")

        return "；".join(findings) if findings else "无明显特征"


# 使用示例
if __name__ == "__main__":
    # 测试基本面分析工具
    tool = FundamentalAnalysisTool()

    test_data = {
        "company": "测试公司",
        "pe_ratio": 15.5,
        "industry_pe": 20.0,
        "pb_ratio": 2.1,
        "industry_pb": 2.5,
        "revenue_growth": 18.5,
        "net_income_growth": 22.3,
        "roe": 16.8,
        "roa": 8.5,
        "gross_margin": 45.2,
        "current_ratio": 2.3,
        "debt_to_equity": 0.6,
        "free_cash_flow": 1000000,
        "growth_rate": 0.15,
        "discount_rate": 0.10
    }

    print("=== 测试基本面分析工具 ===")
    result = tool._run(json.dumps(test_data), "comprehensive")
    print(result)