"""
分析团队
负责基本面分析、风险分析和行业分析
"""
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from typing import List, Dict, Any
import logging
import json

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@CrewBase
class AnalysisCrew:
    """分析团队"""

    @agent
    def fundamental_analyst(self) -> Agent:
        """基本面分析师"""
        return Agent(
            config=self.agents_config['fundamental_analyst'],
            verbose=True,
            allow_delegation=False,
            max_iter=4
        )

    @agent
    def risk_assessor(self) -> Agent:
        """风险评估师"""
        return Agent(
            config=self.agents_config['risk_assessor'],
            verbose=True,
            allow_delegation=False,
            max_iter=4
        )

    @agent
    def industry_expert(self) -> Agent:
        """行业专家"""
        return Agent(
            config=self.agents_config['industry_expert'],
            verbose=True,
            allow_delegation=False,
            max_iter=4
        )

    @agent
    def market_sentiment_analyst(self) -> Agent:
        """市场情绪分析师"""
        return Agent(
            config=self.agents_config['market_sentiment_analyst'],
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )

    @task
    def fundamental_analysis_task(self) -> Task:
        """基本面分析任务"""
        return Task(
            config=self.tasks_config['fundamental_analysis_task'],
            async_execution=False,
            context=[
                self.tasks_config['financial_data_task'],
                self.tasks_config['market_research_task']
            ]
        )

    @task
    def risk_assessment_task(self) -> Task:
        """风险评估任务"""
        return Task(
            config=self.tasks_config['risk_assessment_task'],
            async_execution=False,
            context=[
                self.tasks_config['fundamental_analysis_task'],
                self.tasks_config['market_research_task']
            ]
        )

    @task
    def industry_analysis_task(self) -> Task:
        """行业分析任务"""
        return Task(
            config=self.tasks_config['industry_analysis_task'],
            async_execution=False,
            context=[
                self.tasks_config['market_research_task'],
                self.tasks_config['sentiment_analysis_task']
            ]
        )

    @task
    def sentiment_analysis_task(self) -> Task:
        """情绪分析任务"""
        return Task(
            config=self.tasks_config['sentiment_analysis_task'],
            async_execution=False
        )

    @crew
    def crew(self) -> Crew:
        """分析团队"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
            cache=True,
            planning=True
        )

    def execute_analysis(self, company: str, ticker: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行分析流程"""
        logger.info(f"开始分析 {company} ({ticker})")

        inputs = {
            'company': company,
            'ticker': ticker
        }

        if data:
            inputs.update(data)

        try:
            result = self.crew().kickoff(inputs=inputs)
            logger.info(f"分析完成: {company}")

            # 解析分析结果
            analysis_result = self._parse_analysis_result(result)

            return {
                'success': True,
                'data': analysis_result,
                'company': company,
                'ticker': ticker
            }
        except Exception as e:
            logger.error(f"分析失败: {company}, 错误: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'company': company,
                'ticker': ticker
            }

    def _parse_analysis_result(self, raw_result: Any) -> Dict[str, Any]:
        """解析分析结果"""
        try:
            # 如果结果已经是字典格式，直接返回
            if isinstance(raw_result, dict):
                return raw_result

            # 如果结果是字符串，尝试解析JSON
            if isinstance(raw_result, str):
                try:
                    return json.loads(raw_result)
                except json.JSONDecodeError:
                    # 不是JSON格式，返回结构化文本
                    return {
                        'analysis_text': raw_result,
                        'analysis_type': 'text'
                    }

            # 其他格式，转换为字符串
            return {
                'analysis_text': str(raw_result),
                'analysis_type': 'raw'
            }

        except Exception as e:
            logger.error(f"解析分析结果失败: {str(e)}")
            return {
                'analysis_text': str(raw_result),
                'analysis_type': 'raw',
                'parse_error': str(e)
            }

    def calculate_analysis_score(self, analysis_result: Dict[str, Any]) -> Dict[str, float]:
        """计算分析评分"""
        scores = {
            'fundamental_score': 0.0,
            'risk_score': 0.0,
            'industry_score': 0.0,
            'sentiment_score': 0.0,
            'overall_score': 0.0
        }

        try:
            # 基于分析结果计算各项评分
            # 这里可以根据实际分析结果实现更复杂的评分逻辑

            # 基本面评分 (0-100)
            fundamental_data = analysis_result.get('fundamental_analysis', {})
            scores['fundamental_score'] = self._calculate_fundamental_score(fundamental_data)

            # 风险评分 (0-100，分数越低风险越小)
            risk_data = analysis_result.get('risk_assessment', {})
            scores['risk_score'] = self._calculate_risk_score(risk_data)

            # 行业评分 (0-100)
            industry_data = analysis_result.get('industry_analysis', {})
            scores['industry_score'] = self._calculate_industry_score(industry_data)

            # 情绪评分 (0-100)
            sentiment_data = analysis_result.get('sentiment_analysis', {})
            scores['sentiment_score'] = self._calculate_sentiment_score(sentiment_data)

            # 综合评分
            scores['overall_score'] = (
                scores['fundamental_score'] * 0.35 +
                (100 - scores['risk_score']) * 0.25 +  # 风险分数反转
                scores['industry_score'] * 0.25 +
                scores['sentiment_score'] * 0.15
            )

        except Exception as e:
            logger.error(f"计算分析评分失败: {str(e)}")

        return scores

    def _calculate_fundamental_score(self, fundamental_data: Dict) -> float:
        """计算基本面评分"""
        # 简化的评分逻辑，实际应该基于具体的财务指标
        base_score = 70.0

        # 根据分析文本中的关键词调整评分
        text = fundamental_data.get('analysis_text', '').lower()
        if '优秀' in text or '强劲' in text:
            base_score += 15
        elif '良好' in text:
            base_score += 10
        elif '一般' in text:
            base_score += 0
        elif '较差' in text:
            base_score -= 15

        return max(0, min(100, base_score))

    def _calculate_risk_score(self, risk_data: Dict) -> float:
        """计算风险评分"""
        base_score = 30.0  # 默认风险较低

        text = risk_data.get('analysis_text', '').lower()
        if '高风险' in text or '重大风险' in text:
            base_score += 40
        elif '中等风险' in text:
            base_score += 20
        elif '低风险' in text:
            base_score -= 10

        return max(0, min(100, base_score))

    def _calculate_industry_score(self, industry_data: Dict) -> float:
        """计算行业评分"""
        base_score = 75.0

        text = industry_data.get('analysis_text', '').lower()
        if '领先' in text or '龙头' in text:
            base_score += 15
        elif '优势' in text:
            base_score += 10
        elif '一般' in text:
            base_score += 0
        elif '落后' in text:
            base_score -= 20

        return max(0, min(100, base_score))

    def _calculate_sentiment_score(self, sentiment_data: Dict) -> float:
        """计算情绪评分"""
        base_score = 60.0

        text = sentiment_data.get('analysis_text', '').lower()
        if '积极' in text or '乐观' in text:
            base_score += 25
        elif '正面' in text:
            base_score += 15
        elif '中性' in text:
            base_score += 0
        elif '消极' in text or '悲观' in text:
            base_score -= 20

        return max(0, min(100, base_score))

    def generate_analysis_summary(self, analysis_result: Dict[str, Any]) -> str:
        """生成分析摘要"""
        scores = self.calculate_analysis_score(analysis_result)

        summary = f"""
分析摘要：
- 基本面评分: {scores['fundamental_score']:.1f}/100
- 风险评分: {scores['risk_score']:.1f}/100
- 行业评分: {scores['industry_score']:.1f}/100
- 市场情绪评分: {scores['sentiment_score']:.1f}/100
- 综合评分: {scores['overall_score']:.1f}/100

投资建议：{self._get_recommendation(scores)}
"""

        return summary

    def _get_recommendation(self, scores: Dict[str, float]) -> str:
        """根据评分给出投资建议"""
        overall = scores['overall_score']
        risk = scores['risk_score']

        if overall >= 80 and risk <= 40:
            return "强烈买入"
        elif overall >= 70 and risk <= 50:
            return "买入"
        elif overall >= 60 and risk <= 60:
            return "增持"
        elif overall >= 50 and risk <= 70:
            return "持有"
        elif overall >= 40 and risk <= 80:
            return "减持"
        else:
            return "卖出"


# 使用示例
if __name__ == "__main__":
    # 创建分析团队实例
    analysis_crew = AnalysisCrew()

    # 执行分析示例
    result = analysis_crew.execute_analysis("苹果公司", "AAPL")
    print("分析结果:", result)

    if result['success']:
        # 计算评分
        scores = analysis_crew.calculate_analysis_score(result['data'])
        print("分析评分:", scores)

        # 生成摘要
        summary = analysis_crew.generate_analysis_summary(result['data'])
        print("分析摘要:", summary)