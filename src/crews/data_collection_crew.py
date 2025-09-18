"""
数据收集团队 - 使用CrewAI真正的多智能体协作
负责收集市场数据、财务数据和技术数据，展示智能体间的协作与通信
"""
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from typing import List, Dict, Any, Optional
import logging
import yaml
import os
from datetime import datetime
from src.tools.akshare_tools import AkShareTool
from src.tools.fundamental_tools import FundamentalAnalysisTool
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@CrewBase
class DataCollectionCrew:
    """数据收集团队 - 展示真正的智能体协作"""

    def __init__(self):
        """初始化数据收集团队"""
        self.agents_config = self._load_config('config/agents.yaml')
        self.tasks_config = self._load_config('config/tasks.yaml')

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            # 获取项目根目录
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            config_path = os.path.join(current_dir, config_file)

            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"加载配置文件失败: {config_file}, 错误: {str(e)}")
            return {}

    @agent
    def market_researcher(self) -> Agent:
        """市场研究员 - 负责收集市场趋势和新闻"""
        config = self.agents_config.get('market_researcher', {})
        return Agent(
            config=self.agents_config['market_researcher'],
            verbose=True,
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
            allow_delegation=True,  # 允许委托任务给其他智能体
            max_iter=5,
            memory=True,  # 启用记忆功能
            cache=True,   # 启用缓存
        )

    @agent
    def financial_data_expert(self) -> Agent:
        """财务数据专家 - 负责收集和分析财务数据"""
        config = self.agents_config.get('financial_data_expert', {})
        return Agent(
            config=self.agents_config['financial_data_expert'],
            verbose=True,
            tools=[AkShareTool(), FundamentalAnalysisTool()],
            allow_delegation=True,
            max_iter=5,
            memory=True,
            cache=True,
        )

    @agent
    def technical_analyst(self) -> Agent:
        """技术分析师 - 负责收集技术指标数据"""
        config = self.agents_config.get('technical_analyst', {})
        return Agent(
            config=self.agents_config['technical_analyst'],
            verbose=True,
            tools=[AkShareTool()],
            allow_delegation=True,
            max_iter=5,
            memory=True,
            cache=True,
        )

    @agent
    def data_validation_expert(self) -> Agent:
        """数据验证专家 - 负责验证数据质量和一致性"""
        config = self.agents_config.get('data_validation_expert', {})
        return Agent(
            config=self.agents_config['data_validation_expert'],
            verbose=True,
            allow_delegation=False,  # 验证专家不委托任务
            max_iter=3,
            memory=True,
            cache=True,
        )

    @agent
    def data_coordination_agent(self) -> Agent:
        """数据协调智能体 - 负责协调各智能体的工作，解决冲突"""
        return Agent(
            role='数据协调专家',
            goal='协调各数据收集智能体的工作，确保数据收集的完整性和一致性',
            backstory="""你是一位资深的数据协调专家，擅长管理复杂数据收集项目。
            你能够识别数据收集过程中的冲突和重复，优化工作流程，并确保最终数据质量。
            你具有很强的沟通能力和问题解决能力，能够在智能体之间建立有效的协作机制。""",
            verbose=True,
            allow_delegation=True,
            max_iter=5,
            memory=True,
            cache=True,
        )

    @task
    def market_research_task(self) -> Task:
        """市场研究任务 - 收集市场趋势和新闻"""
        return Task(
            config=self.tasks_config['market_research_task'],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
            context=[],  # 将在执行时动态设置
            human_input=False,  # 不需要人工输入
            output_file='market_research_report.md',
        )

    @task
    def financial_data_collection_task(self) -> Task:
        """财务数据收集任务 - 收集财务报表和指标"""
        return Task(
            config=self.tasks_config['financial_data_collection_task'],
            tools=[AkShareTool(), FundamentalAnalysisTool()],
            context=[],  # 将在执行时动态设置
            human_input=False,
            output_file='financial_data_report.md',
        )

    @task
    def technical_data_collection_task(self) -> Task:
        """技术数据收集任务 - 收集技术指标"""
        return Task(
            config=self.tasks_config['technical_data_collection_task'],
            tools=[AkShareTool()],
            context=[],  # 将在执行时动态设置
            human_input=False,
            output_file='technical_data_report.md',
        )

    @task
    def data_validation_task(self) -> Task:
        """数据验证任务 - 验证所有收集的数据"""
        return Task(
            config=self.tasks_config['data_validation_task'],
            context=[],  # 将在执行时动态设置所有前置任务
            human_input=False,
            output_file='data_validation_report.md',
        )

    @task
    def data_coordination_task(self) -> Task:
        """数据协调任务 - 协调各智能体工作并整合结果"""
        return Task(
            description="""
            协调市场研究、财务数据收集和技术数据收集的工作：

            1. 检查各智能体的工作进展和结果
            2. 识别数据重复或冲突的地方
            3. 协调解决数据收集中的问题
            4. 确保数据的完整性和一致性
            5. 生成最终的数据收集报告

            公司: {company}
            股票代码: {ticker}
            """,
            expected_output="""
            完整的数据收集协调报告，包括：
            - 各智能体的工作总结
            - 数据质量评估
            - 发现的问题和解决方案
            - 最终的数据收集建议
            """,
            tools=[],  # 协调智能体主要使用沟通和推理能力
            context=[],  # 将在执行时动态设置所有前置任务
            human_input=False,
            output_file='data_coordination_report.md',
        )

    @crew
    def crew(self) -> Crew:
        """创建Crew实例 - 配置智能体协作"""
        return Crew(
            agents=self.agents,  # 所有智能体
            tasks=self.tasks,    # 所有任务
            process=Process.hierarchical,  # 使用层次化流程，让智能体自主协作
            verbose=True,
            memory=True,  # 启用团队记忆
            cache=True,   # 启用缓存
            planning=True,  # 启用规划功能
            planning_llm='gpt-4o-mini',  # 使用专门的LLM进行规划
        )

    def execute_data_collection(self, company: str, ticker: str) -> Dict[str, Any]:
        """执行真正的多智能体协作数据收集"""
        try:
            logger.info(f"启动多智能体协作数据收集: {company} ({ticker})")

            # 准备输入参数
            inputs = {
                'company': company,
                'ticker': ticker
            }

            # 动态设置任务上下文，实现智能体间的协作
            self._setup_task_contexts()

            # 执行团队任务
            logger.info("开始执行多智能体协作任务...")
            result = self.crew().kickoff(inputs=inputs)

            # 收集各智能体的输出
            outputs = self._collect_agent_outputs()

            # 验证数据质量
            validation_result = self._validate_data_quality(outputs)

            logger.info(f"多智能体协作数据收集完成: {company}")

            return {
                'success': True,
                'company': company,
                'ticker': ticker,
                'result': result,
                'agent_outputs': outputs,
                'validation_result': validation_result,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'collaboration_metrics': self._calculate_collaboration_metrics(outputs)
            }

        except Exception as e:
            error_msg = f"多智能体协作数据收集失败: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'company': company,
                'ticker': ticker,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

    def _setup_task_contexts(self):
        """设置任务间的上下文关系，实现智能体协作"""
        # 获取任务实例
        market_task = self.market_research_task()
        financial_task = self.financial_data_collection_task()
        technical_task = self.technical_data_collection_task()
        validation_task = self.data_validation_task()
        coordination_task = self.data_coordination_task()

        # 设置任务依赖关系
        # 验证任务依赖于所有数据收集任务
        validation_task.context = [market_task, financial_task, technical_task]

        # 协调任务依赖于所有其他任务
        coordination_task.context = [market_task, financial_task, technical_task, validation_task]

    def _collect_agent_outputs(self) -> Dict[str, Any]:
        """收集各智能体的输出"""
        outputs = {}

        # 从生成的文件中读取结果
        report_files = [
            'market_research_report.md',
            'financial_data_report.md',
            'technical_data_report.md',
            'data_validation_report.md',
            'data_coordination_report.md'
        ]

        for file_name in report_files:
            try:
                if os.path.exists(file_name):
                    with open(file_name, 'r', encoding='utf-8') as f:
                        outputs[file_name] = f.read()
                else:
                    outputs[file_name] = f"文件 {file_name} 未生成"
            except Exception as e:
                outputs[file_name] = f"读取文件失败: {str(e)}"

        return outputs

    def _validate_data_quality(self, outputs: Dict[str, Any]) -> Dict[str, Any]:
        """验证数据质量"""
        validation_result = {
            'overall_quality': 'unknown',
            'data_completeness': 0,
            'issues_found': [],
            'recommendations': []
        }

        try:
            # 检查各报告的完整性
            completeness_score = 0
            total_files = len(outputs)

            for file_name, content in outputs.items():
                if content and "未生成" not in content and "失败" not in content:
                    completeness_score += 1
                else:
                    validation_result['issues_found'].append(f"{file_name} 生成失败")

            validation_result['data_completeness'] = (completeness_score / total_files) * 100

            # 根据完整性评分确定整体质量
            if validation_result['data_completeness'] >= 80:
                validation_result['overall_quality'] = 'excellent'
                validation_result['recommendations'].append("数据质量优秀，可以进入分析阶段")
            elif validation_result['data_completeness'] >= 60:
                validation_result['overall_quality'] = 'good'
                validation_result['recommendations'].append("数据质量良好，建议补充缺失数据")
            else:
                validation_result['overall_quality'] = 'poor'
                validation_result['recommendations'].append("数据质量较差，需要重新收集")

        except Exception as e:
            validation_result['overall_quality'] = 'error'
            validation_result['issues_found'].append(f"验证过程出错: {str(e)}")

        return validation_result

    def _calculate_collaboration_metrics(self, outputs: Dict[str, Any]) -> Dict[str, Any]:
        """计算智能体协作指标"""
        metrics = {
            'total_agents': 5,
            'active_agents': 0,
            'collaboration_score': 0,
            'communication_events': 0,
            'delegation_events': 0
        }

        try:
            # 分析输出文件，计算协作指标
            active_count = 0
            for file_name, content in outputs.items():
                if content and "未生成" not in content and "失败" not in content:
                    active_count += 1

                    # 检查内容中是否有协作迹象
                    if "协作" in content or "协调" in content or "沟通" in content:
                        metrics['communication_events'] += 1
                    if "委托" in content or "协助" in content:
                        metrics['delegation_events'] += 1

            metrics['active_agents'] = active_count
            metrics['collaboration_score'] = (active_count / metrics['total_agents']) * 100

        except Exception as e:
            logger.error(f"计算协作指标时出错: {str(e)}")

        return metrics

    def get_crew_info(self) -> Dict[str, Any]:
        """获取团队信息"""
        return {
            'name': '数据收集团队 (多智能体协作版)',
            'agents': [
                '市场研究员',
                '财务数据专家',
                '技术分析师',
                '数据验证专家',
                '数据协调专家'
            ],
            'description': '使用CrewAI真正的多智能体协作机制收集和验证股票分析数据',
            'features': [
                '智能体间自主协作',
                '任务委托机制',
                '动态上下文共享',
                '层次化决策流程',
                '团队记忆和缓存'
            ],
            'process': 'hierarchical (层次化协作流程)'
        }