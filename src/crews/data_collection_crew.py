"""
数据收集团队
负责收集市场数据、财务数据和技术数据
"""
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from typing import List, Dict, Any
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@CrewBase
class DataCollectionCrew:
    """数据收集团队"""

    @agent
    def market_researcher(self) -> Agent:
        """市场研究员"""
        return Agent(
            config=self.agents_config['market_researcher'],
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )

    @agent
    def financial_data_expert(self) -> Agent:
        """财务数据专家"""
        return Agent(
            config=self.agents_config['financial_data_expert'],
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )

    @agent
    def technical_analyst(self) -> Agent:
        """技术分析师"""
        return Agent(
            config=self.agents_config['technical_analyst'],
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )

    @agent
    def data_validator(self) -> Agent:
        """数据验证专家"""
        return Agent(
            config=self.agents_config['data_validator'],
            verbose=True,
            allow_delegation=False,
            max_iter=2
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
    def market_research_task(self) -> Task:
        """市场研究任务"""
        return Task(
            config=self.tasks_config['market_research_task'],
            async_execution=False
        )

    @task
    def financial_data_task(self) -> Task:
        """财务数据任务"""
        return Task(
            config=self.tasks_config['financial_data_task'],
            async_execution=False
        )

    @task
    def technical_analysis_task(self) -> Task:
        """技术分析任务"""
        return Task(
            config=self.tasks_config['technical_analysis_task'],
            async_execution=False
        )

    @task
    def data_validation_task(self) -> Task:
        """数据验证任务"""
        return Task(
            config=self.tasks_config['data_validation_task'],
            async_execution=False
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
        """数据收集团队"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
            cache=True,
            planning=True
        )

    def execute_data_collection(self, company: str, ticker: str) -> Dict[str, Any]:
        """执行数据收集流程"""
        logger.info(f"开始收集 {company} ({ticker}) 的数据")

        inputs = {
            'company': company,
            'ticker': ticker
        }

        try:
            result = self.crew().kickoff(inputs=inputs)
            logger.info(f"数据收集完成: {company}")
            return {
                'success': True,
                'data': result,
                'company': company,
                'ticker': ticker
            }
        except Exception as e:
            logger.error(f"数据收集失败: {company}, 错误: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'company': company,
                'ticker': ticker
            }

    def execute_parallel_collection(self, companies: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """并行收集多家公司数据"""
        import concurrent.futures
        import threading

        results = []
        lock = threading.Lock()

        def collect_single_company(company_data):
            result = self.execute_data_collection(
                company_data['company'],
                company_data['ticker']
            )
            with lock:
                results.append(result)

        # 使用线程池并行执行
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for company_data in companies:
                future = executor.submit(collect_single_company, company_data)
                futures.append(future)

            # 等待所有任务完成
            concurrent.futures.wait(futures)

        return results


# 使用示例
if __name__ == "__main__":
    # 创建数据收集团队实例
    data_crew = DataCollectionCrew()

    # 单个公司分析示例
    result = data_crew.execute_data_collection("苹果公司", "AAPL")
    print("单个公司分析结果:", result)

    # 多个公司并行分析示例
    companies = [
        {'company': '苹果公司', 'ticker': 'AAPL'},
        {'company': '微软', 'ticker': 'MSFT'},
        {'company': '谷歌', 'ticker': 'GOOGL'}
    ]

    parallel_results = data_crew.execute_parallel_collection(companies)
    print("并行分析结果:", parallel_results)