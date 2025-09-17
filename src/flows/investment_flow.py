"""
智能投资流程控制
使用Flows实现复杂的投资分析流程控制
"""
from crewai.flow.flow import Flow, listen, start, router
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
from datetime import datetime

# 导入团队
from src.crews.data_collection_crew import DataCollectionCrew
from src.crews.analysis_crew import AnalysisCrew
from src.crews.decision_crew import DecisionCrew

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalysisState(BaseModel):
    """分析状态模型"""
    company: str = ""
    ticker: str = ""
    market_sentiment: str = "neutral"
    financial_score: float = 0.0
    risk_level: str = "unknown"
    industry_position: str = "unknown"
    analysis_depth: str = "standard"
    final_recommendation: str = "hold"
    overall_score: float = 0.0
    current_stage: str = "initialized"
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    data_quality: str = "unknown"
    error_count: int = 0
    warnings: list = []


class SmartInvestmentFlow(Flow[AnalysisState]):
    """智能投资分析流程"""

    def __init__(self):
        super().__init__()
        self.data_collection_crew = DataCollectionCrew()
        self.analysis_crew = AnalysisCrew()
        self.decision_crew = DecisionCrew()
        self.state = AnalysisState()

    @start()
    def initialize_analysis(self):
        """初始化分析流程"""
        logger.info("=== 初始化投资分析流程 ===")
        self.state.current_stage = "initialization"
        self.state.start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        company = input("请输入要分析的公司名称: ")
        ticker = input("请输入股票代码: ")

        self.state.company = company
        self.state.ticker = ticker

        logger.info(f"开始分析 {company} ({ticker})")
        return {"company": company, "ticker": ticker}

    @listen("initialize_analysis")
    def collect_data(self, company_data):
        """数据收集"""
        logger.info("=== 数据收集阶段 ===")
        self.state.current_stage = "data_collection"

        try:
            result = self.data_collection_crew.execute_data_collection(
                self.state.company, self.state.ticker
            )

            if result['success']:
                logger.info("数据收集成功")
                self.state.data_quality = "good"
                return result
            else:
                self.state.error_count += 1
                logger.error(f"数据收集失败: {result.get('error', '未知错误')}")
                return {"success": False, "error": result.get('error')}

        except Exception as e:
            self.state.error_count += 1
            logger.error(f"数据收集异常: {str(e)}")
            return {"success": False, "error": str(e)}

    @listen("collect_data")
    def analyze_data(self, data_result):
        """数据分析"""
        logger.info("=== 数据分析阶段 ===")
        self.state.current_stage = "analysis"

        try:
            if not data_result.get('success', False):
                return {"success": False, "error": "数据收集失败"}

            analysis_result = self.analysis_crew.execute_analysis(
                self.state.company, self.state.ticker, data_result['data']
            )

            if analysis_result['success']:
                self._update_analysis_scores(analysis_result['data'])
                logger.info("数据分析完成")
                return analysis_result
            else:
                self.state.error_count += 1
                logger.error(f"数据分析失败: {analysis_result.get('error', '未知错误')}")
                return {"success": False, "error": analysis_result.get('error')}

        except Exception as e:
            self.state.error_count += 1
            logger.error(f"数据分析异常: {str(e)}")
            return {"success": False, "error": str(e)}

    @listen("analyze_data")
    def make_decision(self, analysis_result):
        """投资决策"""
        logger.info("=== 投资决策阶段 ===")
        self.state.current_stage = "decision"

        try:
            if not analysis_result.get('success', False):
                return {"success": False, "error": "分析失败"}

            decision_result = self.decision_crew.execute_decision_process(
                self.state.company, self.state.ticker, analysis_result['data']
            )

            if decision_result['success']:
                self.state.final_recommendation = decision_result['data'].get('recommendation', 'hold')
                self.state.overall_score = decision_result['data'].get('overall_score', 0.0)
                logger.info("投资决策完成")
                return decision_result
            else:
                self.state.error_count += 1
                logger.error(f"投资决策失败: {decision_result.get('error', '未知错误')}")
                return {"success": False, "error": decision_result.get('error')}

        except Exception as e:
            self.state.error_count += 1
            logger.error(f"投资决策异常: {str(e)}")
            return {"success": False, "error": str(e)}

    @listen("make_decision")
    def finalize_analysis(self, decision_result):
        """完成分析"""
        logger.info("=== 完成分析流程 ===")
        self.state.current_stage = "finalization"
        self.state.end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            if decision_result.get('success', False):
                logger.info("分析流程成功完成")
                return {
                    "success": True,
                    "company": self.state.company,
                    "ticker": self.state.ticker,
                    "recommendation": self.state.final_recommendation,
                    "overall_score": self.state.overall_score,
                    "analysis_time": self.state.start_time,
                    "completion_time": self.state.end_time,
                    "data_quality": self.state.data_quality,
                    "error_count": self.state.error_count
                }
            else:
                logger.error("分析流程失败")
                return {
                    "success": False,
                    "error": decision_result.get('error', '未知错误'),
                    "error_count": self.state.error_count
                }

        except Exception as e:
            self.state.error_count += 1
            logger.error(f"完成分析异常: {str(e)}")
            return {"success": False, "error": str(e), "error_count": self.state.error_count}

    def _update_analysis_scores(self, analysis_data):
        """更新分析评分"""
        try:
            # 更新财务评分
            if 'financial_score' in analysis_data:
                self.state.financial_score = analysis_data['financial_score']

            # 更新风险评估
            if 'risk_level' in analysis_data:
                self.state.risk_level = analysis_data['risk_level']

            # 更新行业地位
            if 'industry_position' in analysis_data:
                self.state.industry_position = analysis_data['industry_position']

            # 更新市场情绪
            if 'market_sentiment' in analysis_data:
                self.state.market_sentiment = analysis_data['market_sentiment']

            logger.info("分析评分已更新")

        except Exception as e:
            logger.error(f"更新分析评分失败: {str(e)}")
            self.state.warnings.append(f"评分更新失败: {str(e)}")

    def run_analysis(self, company: str, ticker: str) -> Dict[str, Any]:
        """运行分析流程"""
        self.state.company = company
        self.state.ticker = ticker
        self.state.start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 手动执行流程
        try:
            # 数据收集
            data_result = self.data_collection_crew.execute_data_collection(company, ticker)
            if not data_result['success']:
                return {"success": False, "error": "数据收集失败"}

            # 数据分析
            analysis_result = self.analysis_crew.execute_analysis(company, ticker, data_result['data'])
            if not analysis_result['success']:
                return {"success": False, "error": "数据分析失败"}

            # 投资决策
            decision_result = self.decision_crew.execute_decision_process(company, ticker, analysis_result['data'])
            if not decision_result['success']:
                return {"success": False, "error": "投资决策失败"}

            # 返回结果
            return {
                "success": True,
                "company": company,
                "ticker": ticker,
                "recommendation": decision_result['data'].get('recommendation', 'hold'),
                "overall_score": decision_result['data'].get('overall_score', 0.0),
                "analysis_time": self.state.start_time,
                "completion_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "data_quality": "good",
                "error_count": 0
            }

        except Exception as e:
            return {"success": False, "error": str(e), "error_count": self.state.error_count}


# 使用示例
if __name__ == "__main__":
    flow = SmartInvestmentFlow()
    # result = flow.kickoff()  # 启动交互式流程
    result = flow.run_analysis("苹果公司", "AAPL")  # 直接运行
    print(result)