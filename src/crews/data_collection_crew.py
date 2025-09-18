"""
简化的数据收集团队
不使用@CrewBase装饰器，直接实现CrewAI功能
"""
import sys
import os
sys.path.append(os.path.abspath('.'))

from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool as CrewAIBaseTool
from typing import Dict, Any, List, Optional
import yaml
import logging
from datetime import datetime

# 导入自定义工具
try:
    from src.tools.custom_tools import AkShareTool, FundamentalAnalysisTool, TechnicalAnalysisTool
    from src.tools.reporting_tools import ReportWritingTool
    CUSTOM_TOOLS_AVAILABLE = True
except ImportError:
    CUSTOM_TOOLS_AVAILABLE = False
    print("警告: 自定义工具不可用，将使用基础功能")

# 尝试导入crewai_tools工具，如果失败则创建模拟工具类
serper_tool = None
scrape_tool = None
try:
    from crewai_tools import SerperDevTool, ScrapeWebsiteTool
    serper_tool = SerperDevTool()
    scrape_tool = ScrapeWebsiteTool()
except ImportError as e:
    logging.warning(f"无法导入crewai_tools工具: {str(e)}")

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCollectionCrew:
    """简化的数据收集团队"""

    def __init__(self):
        """初始化数据收集团队"""
        self.agents_config = self._load_config('config/agents.yaml')
        self.tasks_config = self._load_config('config/tasks.yaml')

        # 如果配置文件加载失败，使用内置的默认配置
        if not self.agents_config:
            logger.warning("使用内置默认agents配置")
            self.agents_config = self._get_default_agents_config()
        if not self.tasks_config:
            logger.warning("使用内置默认tasks配置")
            self.tasks_config = self._get_default_tasks_config()

        logger.info(f"配置加载完成 - agents: {len(self.agents_config)}, tasks: {len(self.tasks_config)}")

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            # 尝试多个可能的配置文件路径
            possible_paths = [
                config_file,  # 直接路径
                os.path.join(os.path.dirname(__file__), config_file),  # 相对于当前文件
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', os.path.basename(config_file)),  # 相对于src目录
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', os.path.basename(config_file)),  # 相对于项目根目录
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        config_data = yaml.safe_load(f)
                        logger.debug(f"成功加载配置文件: {config_file}")
                        return config_data

            logger.warning(f"未找到配置文件: {config_file}")
            return {}

        except Exception as e:
            logger.error(f"加载配置文件 {config_file} 时出错: {str(e)}")
            return {}

    def _get_default_agents_config(self) -> Dict[str, Any]:
        """获取默认的agents配置"""
        return {
            "market_researcher": {
                "role": "高级市场研究分析师",
                "goal": "收集并分析{company}的最新市场数据和行业趋势",
                "backstory": "你是一位拥有10年经验的资深市场分析师，擅长从海量信息中提取关键趋势和数据，为投资决策提供可靠的基础数据支持。"
            },
            "financial_data_expert": {
                "role": "财务数据专家",
                "goal": "获取并分析{company}的财务报表和关键财务指标",
                "backstory": "你是金融数据专家，精通财务数据分析和处理。你能够快速解析复杂的财务报表，提取关键指标，并进行同行业对比分析。"
            },
            "technical_analyst": {
                "role": "技术分析师",
                "goal": "分析{company}的股价走势和技术指标，提供技术面见解",
                "backstory": "你是资深技术分析师，精通各种技术分析方法和指标计算。你能够识别价格趋势、支撑阻力位，并提供专业的技术分析建议。"
            },
            "data_validation_expert": {
                "role": "数据验证专家",
                "goal": "验证所有收集数据的准确性和一致性",
                "backstory": "你是数据质量专家，擅长验证和清洗数据。你具有敏锐的数据洞察力，能够发现数据中的异常和不一致之处。"
            },
            "data_coordination_agent": {
                "role": "数据协调专家",
                "goal": "协调各数据收集智能体的工作，确保数据收集的完整性和一致性",
                "backstory": "你是一位资深的数据协调专家，擅长管理复杂数据收集项目。你能够识别数据收集过程中的冲突和重复，优化工作流程，并确保最终数据质量。"
            }
        }

    def _get_default_tasks_config(self) -> Dict[str, Any]:
        """获取默认的tasks配置"""
        return {
            "market_research_task": {
                "description": "对{company}进行全面的市场研究，包括：1. 最近3-6个月的股价走势分析 2. 行业竞争态势和市场份额分析 3. 相关市场新闻和重大事件梳理 4. 分析师评级和观点汇总 5. 宏观经济环境对该公司的影响",
                "expected_output": "详细的市场研究报告，包含数据来源、关键发现和趋势分析，格式为结构化的Markdown文档，字数不少于800字。"
            },
            "financial_data_collection_task": {
                "description": "分析{company}的财务健康状况：1. 最新季度财报关键指标提取（营收、利润、毛利率等）2. 过去3年的财务趋势分析 3. 负债比率和现金流状况评估 4. 与同行业主要竞争对手的财务对比 5. 财务健康状况综合评分",
                "expected_output": "完整的财务分析报告，包含详细的财务指标对比分析、趋势图表和风险提示，输出为结构化数据格式。"
            },
            "technical_analysis_task": {
                "description": "对{company}进行技术面分析：1. 主要技术指标计算和解读（移动平均线、RSI、MACD等）2. 价格趋势和支撑阻力位分析 3. 交易量分析和资金流向判断 4. 技术面信号汇总和买卖时机建议",
                "expected_output": "专业的技术分析报告，包含技术图表、指标分析和具体的交易建议，输出为Markdown格式。"
            },
            "data_validation_task": {
                "description": "验证所有收集数据的准确性和一致性：1. 检查数据来源的可靠性 2. 验证数据的一致性和完整性 3. 识别和处理异常值 4. 确保数据质量达到分析标准",
                "expected_output": "数据验证报告，包含数据质量评估、异常值处理结果和数据可信度评分。"
            },
            "data_coordination_task": {
                "description": "协调和整合所有数据收集工作：1. 监控各智能体的工作进度 2. 识别和解决数据冲突 3. 整合多源数据 4. 确保最终数据的一致性和完整性",
                "expected_output": "数据协调报告，包含工作进度汇总、数据整合结果和质量评估。"
            }
        }

    def create_agents(self, company: str, ticker: str) -> List[Agent]:
        """创建所有智能体"""
        agents = []

        # 市场研究员
        try:
            market_tools = [tool for tool in [serper_tool, scrape_tool] if tool is not None]
            if CUSTOM_TOOLS_AVAILABLE:
                market_tools.extend([TechnicalAnalysisTool()])

            market_researcher = Agent(
                role="市场研究员",
                goal=f"收集{company}的市场趋势、行业动态和相关新闻",
                backstory="你是一位经验丰富的市场研究员，擅长分析市场趋势和收集行业信息。",
                verbose=True,
                tools=market_tools,
                allow_delegation=True,
                max_iter=5,
                memory=True,
                cache=True,
            )
            agents.append(market_researcher)
            logger.info("✓ 创建市场研究员智能体成功")
        except Exception as e:
            logger.error(f"✗ 创建市场研究员智能体失败: {str(e)}")

        # 财务数据专家
        try:
            financial_tools = []
            if CUSTOM_TOOLS_AVAILABLE:
                financial_tools.extend([AkShareTool(), FundamentalAnalysisTool()])

            financial_expert = Agent(
                role="财务数据专家",
                goal=f"收集和分析{company}的财务数据，包括财务报表和关键财务指标",
                backstory="你是一名经验丰富的财务分析师，擅长收集和分析上市公司的财务数据。",
                verbose=True,
                tools=financial_tools,
                allow_delegation=True,
                max_iter=5,
                memory=True,
                cache=True,
            )
            agents.append(financial_expert)
            logger.info("✓ 创建财务数据专家智能体成功")
        except Exception as e:
            logger.error(f"✗ 创建财务数据专家智能体失败: {str(e)}")

        # 技术分析师
        try:
            technical_tools = []
            if CUSTOM_TOOLS_AVAILABLE:
                technical_tools.append(TechnicalAnalysisTool())

            technical_analyst = Agent(
                role="技术分析师",
                goal=f"分析{company}的股价走势和技术指标",
                backstory="你是一名专业的股票技术分析师，擅长分析股票价格走势和技术指标。",
                verbose=True,
                tools=technical_tools,
                allow_delegation=True,
                max_iter=5,
                memory=True,
                cache=True,
            )
            agents.append(technical_analyst)
            logger.info("✓ 创建技术分析师智能体成功")
        except Exception as e:
            logger.error(f"✗ 创建技术分析师智能体失败: {str(e)}")

        # 数据验证专家
        try:
            validation_tools = []
            if CUSTOM_TOOLS_AVAILABLE:
                validation_tools.append(FundamentalAnalysisTool())

            data_validator = Agent(
                role="数据验证专家",
                goal=f"验证收集的{company}数据的准确性和完整性",
                backstory="你是数据质量专家，擅长数据验证和清洗。",
                verbose=True,
                tools=validation_tools,
                allow_delegation=True,
                max_iter=3,
                memory=True,
                cache=True,
            )
            agents.append(data_validator)
            logger.info("✓ 创建数据验证专家智能体成功")
        except Exception as e:
            logger.error(f"✗ 创建数据验证专家智能体失败: {str(e)}")

        # 数据协调专家
        try:
            coordinator = Agent(
                role="数据协调专家",
                goal=f"协调各智能体的{company}数据收集工作",
                backstory="你是一位优秀的项目经理，擅长协调多个团队的工作。",
                verbose=True,
                allow_delegation=True,
                max_iter=5,
                memory=True,
                cache=True,
            )
            agents.append(coordinator)
            logger.info("✓ 创建数据协调专家智能体成功")
        except Exception as e:
            logger.error(f"✗ 创建数据协调专家智能体失败: {str(e)}")

        return agents

    def create_tasks(self, company: str, ticker: str, agents: List[Agent]) -> List[Task]:
        """创建所有任务"""
        tasks = []

        if len(agents) < 3:
            logger.error("智能体数量不足，无法创建完整的任务链")
            return tasks

        # 市场研究任务
        try:
            market_task = Task(
                description=f"对{company}进行全面的市场研究，包括行业动态、市场趋势和相关新闻",
                expected_output=f"详细的{company}市场研究报告，包含趋势分析和市场洞察",
                agent=agents[0],  # 市场研究员
                context=[],
                async_execution=False,
            )
            tasks.append(market_task)
            logger.info("✓ 创建市场研究任务成功")
        except Exception as e:
            logger.error(f"✗ 创建市场研究任务失败: {str(e)}")

        # 财务数据收集任务
        try:
            financial_task = Task(
                description=f"分析{company}的财务健康状况，包括关键财务指标和趋势分析",
                expected_output=f"完整的{company}财务分析报告，包含详细的财务指标分析",
                agent=agents[1],  # 财务数据专家
                context=[tasks[0]] if tasks else [],
                async_execution=False,
            )
            tasks.append(financial_task)
            logger.info("✓ 创建财务数据收集任务成功")
        except Exception as e:
            logger.error(f"✗ 创建财务数据收集任务失败: {str(e)}")

        # 技术分析任务
        try:
            technical_task = Task(
                description=f"对{company}进行技术面分析，包括价格走势和技术指标分析",
                expected_output=f"专业的{company}技术分析报告，包含技术指标分析",
                agent=agents[2],  # 技术分析师
                context=[tasks[0]] if tasks else [],
                async_execution=False,
            )
            tasks.append(technical_task)
            logger.info("✓ 创建技术分析任务成功")
        except Exception as e:
            logger.error(f"✗ 创建技术分析任务失败: {str(e)}")

        # 数据验证任务
        try:
            validation_task = Task(
                description=f"验证所有收集的{company}数据的准确性和一致性",
                expected_output=f"{company}数据验证报告，包含数据质量评估",
                agent=agents[3] if len(agents) > 3 else agents[0],
                context=tasks[:3] if len(tasks) >= 3 else tasks,
                async_execution=False,
            )
            tasks.append(validation_task)
            logger.info("✓ 创建数据验证任务成功")
        except Exception as e:
            logger.error(f"✗ 创建数据验证任务失败: {str(e)}")

        # 数据协调任务
        try:
            coordinator_idx = min(4, len(agents) - 1)
            coordination_task = Task(
                description=f"协调和整合所有{company}数据收集工作，确保数据的一致性",
                expected_output=f"{company}数据协调报告，包含工作进度汇总和质量评估",
                agent=agents[coordinator_idx],  # 数据协调专家
                context=tasks,
                async_execution=False,
            )
            tasks.append(coordination_task)
            logger.info("✓ 创建数据协调任务成功")
        except Exception as e:
            logger.error(f"✗ 创建数据协调任务失败: {str(e)}")

        return tasks

    def create_crew(self, company: str, ticker: str) -> Optional[Crew]:
        """创建Crew实例"""
        try:
            # 创建智能体
            agents = self.create_agents(company, ticker)
            if not agents:
                logger.error("无法创建任何智能体")
                return None

            # 创建任务
            tasks = self.create_tasks(company, ticker, agents)
            if not tasks:
                logger.error("无法创建任何任务")
                return None

            # 创建Crew
            crew = Crew(
                agents=agents,
                tasks=tasks,
                process=Process.sequential,  # 使用顺序流程，避免manager_llm要求
                verbose=True,
                memory=True,
                cache=True,
                planning=True,
            )

            logger.info(f"✓ 成功创建Crew实例，包含 {len(agents)} 个智能体和 {len(tasks)} 个任务")
            return crew

        except Exception as e:
            logger.error(f"创建Crew实例时出错: {str(e)}")
            return None

    def execute_data_collection(self, company: str, ticker: str) -> Dict[str, Any]:
        """执行数据收集"""
        try:
            logger.info(f"开始执行{company}的数据收集任务")

            # 创建Crew
            crew = self.create_crew(company, ticker)
            if not crew:
                return {
                    "status": "failed",
                    "error": "无法创建Crew实例",
                    "company": company,
                    "ticker": ticker,
                    "timestamp": datetime.now().isoformat()
                }

            # 准备输入参数
            inputs = {
                "company": company,
                "ticker": ticker
            }

            # 执行任务
            logger.info("启动CrewAI多智能体协作...")
            result = crew.kickoff(inputs=inputs)

            # 返回结果
            return {
                "status": "success",
                "result": result,
                "company": company,
                "ticker": ticker,
                "timestamp": datetime.now().isoformat(),
                "agents_count": len(crew.agents),
                "tasks_count": len(crew.tasks)
            }

        except Exception as e:
            logger.error(f"执行数据收集时出错: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "company": company,
                "ticker": ticker,
                "timestamp": datetime.now().isoformat()
            }

    def get_crew_info(self) -> Dict[str, Any]:
        """获取团队信息"""
        return {
            'name': '数据收集团队 (简化版)',
            'agents': [
                '市场研究员',
                '财务数据专家',
                '技术分析师',
                '数据验证专家',
                '数据协调专家'
            ],
            'description': '使用CrewAI进行多智能体协作数据收集',
            'features': [
                '智能体间协作',
                '任务链式执行',
                '上下文共享',
                '层次化流程'
            ],
            'process': 'hierarchical (层次化协作流程)'
        }


# 测试代码
if __name__ == "__main__":
    # 创建数据收集团队
    crew = DataCollectionCrew()

    # 获取团队信息
    info = crew.get_crew_info()
    print(f"团队名称: {info['name']}")
    print(f"智能体数量: {len(info['agents'])}")
    print(f"处理流程: {info['process']}")

    # 测试创建Crew
    test_crew = crew.create_crew("贵州茅台", "600519")
    if test_crew:
        print(f"✓ 成功创建测试Crew，包含 {len(test_crew.agents)} 个智能体")
        print(f"✓ 包含 {len(test_crew.tasks)} 个任务")
    else:
        print("✗ 创建测试Crew失败")