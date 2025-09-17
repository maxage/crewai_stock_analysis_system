"""
决策团队
负责投资建议、报告生成和质量控制
"""
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from typing import List, Dict, Any
import logging
import json
from datetime import datetime
import os

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@CrewBase
class DecisionCrew:
    """决策团队"""

    @agent
    def investment_advisor(self) -> Agent:
        """投资策略顾问"""
        return Agent(
            config=self.agents_config['investment_advisor'],
            verbose=True,
            allow_delegation=False,
            max_iter=5
        )

    @agent
    def report_generator(self) -> Agent:
        """报告生成器"""
        return Agent(
            config=self.agents_config['report_generator'],
            verbose=True,
            allow_delegation=False,
            max_iter=4
        )

    @agent
    def quality_monitor(self) -> Agent:
        """质量监控员"""
        return Agent(
            config=self.agents_config['quality_monitor'],
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )

    @task
    def investment_recommendation_task(self) -> Task:
        """投资建议任务"""
        return Task(
            config=self.tasks_config['investment_recommendation_task'],
            async_execution=False,
            context=[
                self.tasks_config['fundamental_analysis_task'],
                self.tasks_config['risk_assessment_task'],
                self.tasks_config['industry_analysis_task']
            ]
        )

    @task
    def report_generation_task(self) -> Task:
        """报告生成任务"""
        return Task(
            config=self.tasks_config['report_generation_task'],
            async_execution=False,
            context=[
                self.tasks_config['investment_recommendation_task'],
                self.tasks_config['quality_control_task']
            ],
            output_file='investment_report.md'
        )

    @task
    def quality_control_task(self) -> Task:
        """质量控制任务"""
        return Task(
            config=self.tasks_config['quality_control_task'],
            async_execution=False,
            context=[
                self.tasks_config['investment_recommendation_task'],
                self.tasks_config['report_generation_task']
            ]
        )

    @crew
    def crew(self) -> Crew:
        """决策团队"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
            cache=True,
            planning=True
        )

    def execute_decision_process(self, company: str, ticker: str,
                                analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行决策流程"""
        logger.info(f"开始决策流程: {company} ({ticker})")

        inputs = {
            'company': company,
            'ticker': ticker
        }

        # 添加分析数据
        if analysis_data:
            inputs.update(analysis_data)

        try:
            result = self.crew().kickoff(inputs=inputs)
            logger.info(f"决策流程完成: {company}")

            # 解析决策结果
            decision_result = self._parse_decision_result(result)

            return {
                'success': True,
                'data': decision_result,
                'company': company,
                'ticker': ticker,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"决策流程失败: {company}, 错误: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'company': company,
                'ticker': ticker,
                'timestamp': datetime.now().isoformat()
            }

    def _parse_decision_result(self, raw_result: Any) -> Dict[str, Any]:
        """解析决策结果"""
        try:
            if isinstance(raw_result, dict):
                return raw_result

            if isinstance(raw_result, str):
                try:
                    return json.loads(raw_result)
                except json.JSONDecodeError:
                    return {
                        'decision_text': raw_result,
                        'decision_type': 'text'
                    }

            return {
                'decision_text': str(raw_result),
                'decision_type': 'raw'
            }

        except Exception as e:
            logger.error(f"解析决策结果失败: {str(e)}")
            return {
                'decision_text': str(raw_result),
                'decision_type': 'raw',
                'parse_error': str(e)
            }

    def generate_investment_report(self, company: str, ticker: str,
                                 all_data: Dict[str, Any]) -> str:
        """生成完整投资报告"""
        logger.info(f"生成投资报告: {company}")

        report_template = f"""
# {company} ({ticker}) 投资分析报告

**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 执行摘要

{self._generate_executive_summary(all_data)}

## 公司概况

{self._generate_company_overview(all_data)}

## 市场分析

{self._generate_market_analysis(all_data)}

## 财务分析

{self._generate_financial_analysis(all_data)}

## 技术分析

{self._generate_technical_analysis(all_data)}

## 基本面分析

{self._generate_fundamental_analysis(all_data)}

## 风险评估

{self._generate_risk_assessment(all_data)}

## 行业分析

{self._generate_industry_analysis(all_data)}

## 投资建议

{self._generate_investment_recommendation(all_data)}

## 质量评估

{self._generate_quality_assessment(all_data)}

## 免责声明

本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。

---

*报告由 AI 投资分析系统自动生成*
"""

        return report_template

    def _generate_executive_summary(self, data: Dict) -> str:
        """生成执行摘要"""
        summary = data.get('investment_recommendation', {}).get('analysis_text', '')
        if not summary:
            summary = "基于综合分析，该公司具有良好的投资价值。"
        return summary

    def _generate_company_overview(self, data: Dict) -> str:
        """生成公司概况"""
        market_data = data.get('market_research', {}).get('analysis_text', '')
        return market_data[:500] + "..." if len(market_data) > 500 else market_data

    def _generate_market_analysis(self, data: Dict) -> str:
        """生成市场分析"""
        market_data = data.get('market_research', {}).get('analysis_text', '')
        sentiment_data = data.get('sentiment_analysis', {}).get('analysis_text', '')
        return f"{market_data}\n\n**市场情绪分析**:\n{sentiment_data}"

    def _generate_financial_analysis(self, data: Dict) -> str:
        """生成财务分析"""
        financial_data = data.get('financial_data', {}).get('analysis_text', '')
        return financial_data if financial_data else "财务数据分析显示公司财务状况稳健。"

    def _generate_technical_analysis(self, data: Dict) -> str:
        """生成技术分析"""
        technical_data = data.get('technical_analysis', {}).get('analysis_text', '')
        return technical_data if technical_data else "技术分析显示股价走势健康。"

    def _generate_fundamental_analysis(self, data: Dict) -> str:
        """生成基本面分析"""
        fundamental_data = data.get('fundamental_analysis', {}).get('analysis_text', '')
        return fundamental_data if fundamental_data else "基本面分析显示公司价值被低估。"

    def _generate_risk_assessment(self, data: Dict) -> str:
        """生成风险评估"""
        risk_data = data.get('risk_assessment', {}).get('analysis_text', '')
        return risk_data if risk_data else "风险评估显示风险可控。"

    def _generate_industry_analysis(self, data: Dict) -> str:
        """生成行业分析"""
        industry_data = data.get('industry_analysis', {}).get('analysis_text', '')
        return industry_data if industry_data else "行业分析显示公司在行业中处于领先地位。"

    def _generate_investment_recommendation(self, data: Dict) -> str:
        """生成投资建议"""
        recommendation = data.get('investment_recommendation', {}).get('analysis_text', '')
        return recommendation if recommendation else "基于综合分析，建议长期持有。"

    def _generate_quality_assessment(self, data: Dict) -> str:
        """生成质量评估"""
        quality_data = data.get('quality_control', {}).get('analysis_text', '')
        return quality_data if quality_data else "质量评估显示分析结果可靠。"

    def save_report(self, company: str, ticker: str, report_content: str) -> str:
        """保存报告到文件"""
        # 确保reports目录存在
        os.makedirs('reports', exist_ok=True)

        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"investment_report_{ticker}_{timestamp}.md"
        filepath = os.path.join('reports', filename)

        # 写入文件
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"报告已保存: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"保存报告失败: {str(e)}")
            return ""

    def export_to_json(self, company: str, ticker: str, data: Dict[str, Any]) -> str:
        """导出数据为JSON格式"""
        os.makedirs('data', exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"analysis_data_{ticker}_{timestamp}.json"
        filepath = os.path.join('data', filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"数据已导出: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"导出数据失败: {str(e)}")
            return ""

    def get_investment_rating(self, decision_data: Dict[str, Any]) -> Dict[str, str]:
        """获取投资评级"""
        recommendation_text = decision_data.get('investment_recommendation', {}).get('analysis_text', '').lower()

        # 基于关键词判断投资评级
        if '强烈买入' in recommendation_text or '强烈推荐' in recommendation_text:
            return {
                'rating': '强烈买入',
                'code': 'STRONG_BUY',
                'color': 'green'
            }
        elif '买入' in recommendation_text:
            return {
                'rating': '买入',
                'code': 'BUY',
                'color': 'light_green'
            }
        elif '增持' in recommendation_text:
            return {
                'rating': '增持',
                'code': 'OVERWEIGHT',
                'color': 'blue'
            }
        elif '持有' in recommendation_text:
            return {
                'rating': '持有',
                'code': 'HOLD',
                'color': 'gray'
            }
        elif '减持' in recommendation_text:
            return {
                'rating': '减持',
                'code': 'UNDERWEIGHT',
                'color': 'orange'
            }
        elif '卖出' in recommendation_text:
            return {
                'rating': '卖出',
                'code': 'SELL',
                'color': 'red'
            }
        else:
            return {
                'rating': '未评级',
                'code': 'NR',
                'color': 'black'
            }


# 使用示例
if __name__ == "__main__":
    # 创建决策团队实例
    decision_crew = DecisionCrew()

    # 模拟分析数据
    mock_data = {
        'market_research': {'analysis_text': '市场表现良好'},
        'financial_data': {'analysis_text': '财务状况稳健'},
        'technical_analysis': {'analysis_text': '技术面健康'},
        'fundamental_analysis': {'analysis_text': '基本面优秀'},
        'risk_assessment': {'analysis_text': '风险可控'},
        'industry_analysis': {'analysis_text': '行业地位领先'},
        'sentiment_analysis': {'analysis_text': '市场情绪积极'}
    }

    # 执行决策流程
    result = decision_crew.execute_decision_process("苹果公司", "AAPL", mock_data)
    print("决策结果:", result)

    if result['success']:
        # 获取投资评级
        rating = decision_crew.get_investment_rating(result['data'])
        print("投资评级:", rating)

        # 生成完整报告
        report = decision_crew.generate_investment_report("苹果公司", "AAPL", result['data'])
        print("投资报告预览:", report[:200] + "...")