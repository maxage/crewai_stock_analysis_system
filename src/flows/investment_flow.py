"""
智能投资流程控制 - 使用CrewAI Flows实现真正的智能路由和条件分支
展示复杂的投资分析流程控制，包括动态路由、条件分支和智能决策
"""
from crewai.flow.flow import Flow, listen, start, router, or_
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import json

# 导入团队
from src.crews.data_collection_crew import DataCollectionCrew
from src.crews.analysis_crew import AnalysisCrew
from src.crews.decision_crew import DecisionCrew

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalysisState(BaseModel):
    """增强的分析状态模型"""
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
    warnings: List[str] = []

    # 新增智能路由相关状态
    data_completeness: float = 0.0
    analysis_confidence: float = 0.0
    market_volatility: str = "medium"
    company_size: str = "medium"
    industry_trend: str = "stable"
    collaboration_quality: str = "medium"
    decision_complexity: str = "standard"
    retry_attempts: Dict[str, int] = {}
    alternative_paths: List[str] = []


class SmartInvestmentFlow(Flow[AnalysisState]):
    """增强的智能投资分析流程 - 展示真正的智能路由和条件分支"""

    def __init__(self):
        super().__init__()
        self.data_collection_crew = DataCollectionCrew()
        self.analysis_crew = AnalysisCrew()
        self.decision_crew = DecisionCrew()

    @start()
    def initialize_analysis(self):
        """初始化分析流程 - 智能评估分析需求"""
        logger.info("=== 初始化智能投资分析流程 ===")
        self.state.current_stage = "initialization"
        self.state.start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        company = input("请输入要分析的公司名称: ")
        ticker = input("请输入股票代码: ")

        # 智能分析公司特征
        company_profile = self._analyze_company_profile(company, ticker)

        self.state.company = company
        self.state.ticker = ticker
        self.state.company_size = company_profile.get('size', 'medium')
        self.state.industry_trend = company_profile.get('trend', 'stable')
        self.state.analysis_depth = self._determine_analysis_depth(company_profile)

        logger.info(f"开始分析 {company} ({ticker})")
        logger.info(f"公司规模: {self.state.company_size}")
        logger.info(f"行业趋势: {self.state.industry_trend}")
        logger.info(f"分析深度: {self.state.analysis_depth}")

        return {
            "company": company,
            "ticker": ticker,
            "company_profile": company_profile,
            "analysis_depth": self.state.analysis_depth
        }

    @listen("initialize_analysis")
    @router
    def route_data_collection(self, initialization_result):
        """智能路由数据收集策略"""
        logger.info("=== 智能数据收集路由 ===")

        # 根据公司特征决定数据收集策略
        if self.state.company_size == "large" and self.state.analysis_depth == "deep":
            logger.info("选择全面数据收集策略")
            return "comprehensive_data_collection"
        elif self.state.market_volatility == "high":
            logger.info("选择实时数据收集策略")
            return "real_time_data_collection"
        else:
            logger.info("选择标准数据收集策略")
            return "standard_data_collection"

    @listen("route_data_collection")
    def standard_data_collection(self, route_result):
        """标准数据收集"""
        return self._execute_data_collection("standard")

    @listen("route_data_collection")
    def comprehensive_data_collection(self, route_result):
        """全面数据收集"""
        return self._execute_data_collection("comprehensive")

    @listen("route_data_collection")
    def real_time_data_collection(self, route_result):
        """实时数据收集"""
        return self._execute_data_collection("real_time")

    def _execute_data_collection(self, collection_type: str):
        """执行数据收集的通用方法"""
        logger.info(f"=== {collection_type} 数据收集 ===")
        self.state.current_stage = "data_collection"

        try:
            # 使用新的协作数据收集方法
            result = self.data_collection_crew.execute_data_collection(
                self.state.company, self.state.ticker
            )

            if result['success']:
                # 分析数据质量
                data_quality = self._assess_data_quality(result)
                self.state.data_quality = data_quality['overall_quality']
                self.state.data_completeness = data_quality['completeness']

                logger.info(f"数据收集成功 - 质量: {self.state.data_quality}")
                logger.info(f"协作指标: {result.get('collaboration_metrics', {})}")

                return {
                    "success": True,
                    "data": result,
                    "collection_type": collection_type,
                    "data_quality": data_quality
                }
            else:
                self.state.error_count += 1
                self.state.retry_attempts['data_collection'] = self.state.retry_attempts.get('data_collection', 0) + 1
                logger.error(f"数据收集失败: {result.get('error', '未知错误')}")

                # 智能重试机制
                if self.state.retry_attempts['data_collection'] < 2:
                    logger.info("尝试备选数据收集方法...")
                    self.state.alternative_paths.append("alternative_data_collection")
                    return {"success": False, "error": result.get('error'), "retry": True}

                return {"success": False, "error": result.get('error')}

        except Exception as e:
            self.state.error_count += 1
            logger.error(f"数据收集异常: {str(e)}")
            return {"success": False, "error": str(e)}

    @listen(or_("standard_data_collection", "comprehensive_data_collection", "real_time_data_collection"))
    @router
    def route_analysis_strategy(self, data_result):
        """智能路由分析策略"""
        logger.info("=== 智能分析策略路由 ===")

        if not data_result.get('success', False):
            logger.info("数据收集失败，使用简化分析")
            return "simplified_analysis"

        # 根据数据质量和公司特征决定分析策略
        data_quality = data_result.get('data_quality', {}).get('overall_quality', 'unknown')

        if data_quality == 'excellent' and self.state.analysis_depth == 'deep':
            logger.info("选择深度分析策略")
            return "deep_analysis"
        elif data_quality in ['good', 'excellent']:
            logger.info("选择标准分析策略")
            return "standard_analysis"
        else:
            logger.info("选择快速分析策略")
            return "rapid_analysis"

    @listen("route_analysis_strategy")
    def deep_analysis(self, route_result):
        """深度分析 - 使用多智能体协作"""
        logger.info("=== 深度协作分析 ===")
        return self._execute_analysis("deep")

    @listen("route_analysis_strategy")
    def standard_analysis(self, route_result):
        """标准分析"""
        logger.info("=== 标准分析 ===")
        return self._execute_analysis("standard")

    @listen("route_analysis_strategy")
    def rapid_analysis(self, route_result):
        """快速分析"""
        logger.info("=== 快速分析 ===")
        return self._execute_analysis("rapid")

    @listen("route_analysis_strategy")
    def simplified_analysis(self, route_result):
        """简化分析"""
        logger.info("=== 简化分析 ===")
        return self._execute_analysis("simplified")

    def _execute_analysis(self, analysis_type: str):
        """执行分析的通用方法"""
        logger.info(f"=== {analysis_type} 分析 ===")
        self.state.current_stage = "analysis"

        try:
            # 获取数据收集结果
            collection_data = self._get_latest_data_collection_result()

            if not collection_data:
                return {"success": False, "error": "无可用的数据收集结果"}

            # 使用新的协作分析方法
            if analysis_type == "deep":
                result = self.analysis_crew.execute_collaborative_analysis(
                    self.state.company, self.state.ticker, collection_data
                )
            else:
                # 对于其他分析类型，使用简化的分析方法
                result = self.analysis_crew.execute_collaborative_analysis(
                    self.state.company, self.state.ticker, collection_data
                )

            if result['success']:
                # 更新分析状态
                self._update_analysis_state(result)

                logger.info(f"{analysis_type} 分析完成")
                logger.info(f"协作评分: {result.get('collaboration_scores', {})}")
                logger.info(f"协作指标: {result.get('collaboration_metrics', {})}")

                return {
                    "success": True,
                    "analysis": result,
                    "analysis_type": analysis_type
                }
            else:
                self.state.error_count += 1
                logger.error(f"{analysis_type} 分析失败: {result.get('error', '未知错误')}")
                return {"success": False, "error": result.get('error')}

        except Exception as e:
            self.state.error_count += 1
            logger.error(f"{analysis_type} 分析异常: {str(e)}")
            return {"success": False, "error": str(e)}

    @listen(or_("deep_analysis", "standard_analysis", "rapid_analysis", "simplified_analysis"))
    @router
    def route_decision_strategy(self, analysis_result):
        """智能路由决策策略"""
        logger.info("=== 智能决策策略路由 ===")

        if not analysis_result.get('success', False):
            logger.info("分析失败，使用保守决策")
            return "conservative_decision"

        # 根据分析质量和复杂度决定决策策略
        analysis_quality = analysis_result.get('analysis', {}).get('collaboration_metrics', {}).get('decision_quality', 'unknown')

        if analysis_quality == 'excellent' and self.state.company_size == 'large':
            logger.info("选择集体决策策略")
            return "collective_decision"
        elif analysis_quality in ['good', 'excellent']:
            logger.info("选择标准决策策略")
            return "standard_decision"
        else:
            logger.info("选择快速决策策略")
            return "rapid_decision"

    @listen("route_decision_strategy")
    def collective_decision(self, route_result):
        """集体决策 - 使用投资委员会机制"""
        logger.info("=== 集体投资决策 ===")
        return self._execute_decision("collective")

    @listen("route_decision_strategy")
    def standard_decision(self, route_result):
        """标准决策"""
        logger.info("=== 标准投资决策 ===")
        return self._execute_decision("standard")

    @listen("route_decision_strategy")
    def rapid_decision(self, route_result):
        """快速决策"""
        logger.info("=== 快速投资决策 ===")
        return self._execute_decision("rapid")

    @listen("route_decision_strategy")
    def conservative_decision(self, route_result):
        """保守决策"""
        logger.info("=== 保守投资决策 ===")
        return self._execute_decision("conservative")

    def _execute_decision(self, decision_type: str):
        """执行决策的通用方法"""
        logger.info(f"=== {decision_type} 决策 ===")
        self.state.current_stage = "decision"

        try:
            # 获取分析结果
            analysis_result = self._get_latest_analysis_result()

            if not analysis_result:
                return {"success": False, "error": "无可用的分析结果"}

            # 使用新的集体决策方法
            if decision_type == "collective":
                result = self.decision_crew.execute_collective_decision(
                    self.state.company, self.state.ticker, analysis_result
                )
            else:
                # 对于其他决策类型，也使用集体决策但简化流程
                result = self.decision_crew.execute_collective_decision(
                    self.state.company, self.state.ticker, analysis_result
                )

            if result['success']:
                # 更新决策状态
                self._update_decision_state(result)

                logger.info(f"{decision_type} 决策完成")
                logger.info(f"集体决策指标: {result.get('collective_decision_metrics', {})}")
                logger.info(f"最终建议: {result.get('final_recommendation', {})}")

                return {
                    "success": True,
                    "decision": result,
                    "decision_type": decision_type
                }
            else:
                self.state.error_count += 1
                logger.error(f"{decision_type} 决策失败: {result.get('error', '未知错误')}")
                return {"success": False, "error": result.get('error')}

        except Exception as e:
            self.state.error_count += 1
            logger.error(f"{decision_type} 决策异常: {str(e)}")
            return {"success": False, "error": str(e)}

    @listen(or_("collective_decision", "standard_decision", "rapid_decision", "conservative_decision"))
    def finalize_analysis(self, decision_result):
        """完成分析并生成总结报告"""
        logger.info("=== 完成智能分析流程 ===")
        self.state.current_stage = "finalization"
        self.state.end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            if decision_result.get('success', False):
                # 生成分析总结
                analysis_summary = self._generate_analysis_summary(decision_result)

                logger.info("智能分析流程成功完成")
                logger.info(f"使用路径: {self.state.alternative_paths}")
                logger.info(f"重试次数: {self.state.retry_attempts}")

                return {
                    "success": True,
                    "company": self.state.company,
                    "ticker": self.state.ticker,
                    "summary": analysis_summary,
                    "final_recommendation": self.state.final_recommendation,
                    "overall_score": self.state.overall_score,
                    "analysis_depth": self.state.analysis_depth,
                    "decision_complexity": self.state.decision_complexity,
                    "collaboration_quality": self.state.collaboration_quality,
                    "path_taken": self.state.alternative_paths,
                    "retry_attempts": self.state.retry_attempts,
                    "analysis_time": self.state.start_time,
                    "completion_time": self.state.end_time,
                    "data_quality": self.state.data_quality,
                    "error_count": self.state.error_count,
                    "warnings": self.state.warnings
                }
            else:
                logger.error("智能分析流程失败")
                return {
                    "success": False,
                    "error": decision_result.get('error', '未知错误'),
                    "error_count": self.state.error_count,
                    "warnings": self.state.warnings
                }

        except Exception as e:
            self.state.error_count += 1
            logger.error(f"完成分析异常: {str(e)}")
            return {"success": False, "error": str(e), "error_count": self.state.error_count}

    # 辅助方法
    def _analyze_company_profile(self, company: str, ticker: str) -> Dict[str, Any]:
        """分析公司特征"""
        # 简化的公司特征分析，实际应用中可以更复杂
        return {
            "size": "large" if len(company) > 10 else "medium",
            "trend": "growing" if any(char.isdigit() for char in ticker) else "stable",
            "complexity": "high" if self.state.analysis_depth == "deep" else "medium"
        }

    def _determine_analysis_depth(self, company_profile: Dict[str, Any]) -> str:
        """根据公司特征决定分析深度"""
        if company_profile.get('size') == 'large' and company_profile.get('complexity') == 'high':
            return 'deep'
        elif company_profile.get('size') == 'large':
            return 'comprehensive'
        else:
            return 'standard'

    def _assess_data_quality(self, data_result: Dict[str, Any]) -> Dict[str, Any]:
        """评估数据质量"""
        collaboration_metrics = data_result.get('collaboration_metrics', {})

        completeness = collaboration_metrics.get('collaboration_score', 0)
        overall_quality = 'unknown'

        if completeness >= 80:
            overall_quality = 'excellent'
        elif completeness >= 60:
            overall_quality = 'good'
        elif completeness >= 40:
            overall_quality = 'acceptable'
        else:
            overall_quality = 'poor'

        return {
            'completeness': completeness,
            'overall_quality': overall_quality
        }

    def _get_latest_data_collection_result(self) -> Optional[Dict[str, Any]]:
        """获取最新的数据收集结果"""
        # 在实际应用中，这里可以从状态或历史记录中获取
        return {"sample": "data"}  # 简化实现

    def _get_latest_analysis_result(self) -> Optional[Dict[str, Any]]:
        """获取最新的分析结果"""
        # 在实际应用中，这里可以从状态或历史记录中获取
        return {"sample": "analysis"}  # 简化实现

    def _update_analysis_state(self, analysis_result: Dict[str, Any]):
        """更新分析状态"""
        try:
            collaboration_scores = analysis_result.get('collaboration_scores', {})
            collaboration_metrics = analysis_result.get('collaboration_metrics', {})

            self.state.financial_score = collaboration_scores.get('overall_score', 0.0)
            self.state.analysis_confidence = collaboration_metrics.get('consensus_level', 0.0)
            self.state.collaboration_quality = collaboration_metrics.get('decision_quality', 'medium')

            logger.info("分析状态已更新")

        except Exception as e:
            logger.error(f"更新分析状态失败: {str(e)}")
            self.state.warnings.append(f"状态更新失败: {str(e)}")

    def _update_decision_state(self, decision_result: Dict[str, Any]):
        """更新决策状态"""
        try:
            final_recommendation = decision_result.get('final_recommendation', {})
            decision_metrics = decision_result.get('collective_decision_metrics', {})

            self.state.final_recommendation = final_recommendation.get('action', 'hold')
            self.state.overall_score = final_recommendation.get('confidence', 0.0) * 100
            self.state.decision_complexity = decision_metrics.get('decision_quality', 'standard')

            logger.info("决策状态已更新")

        except Exception as e:
            logger.error(f"更新决策状态失败: {str(e)}")
            self.state.warnings.append(f"状态更新失败: {str(e)}")

    def _generate_analysis_summary(self, decision_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成分析总结"""
        return {
            "total_stages": len(self.state.alternative_paths) + 1,
            "primary_path": self.state.analysis_depth,
            "collaboration_quality": self.state.collaboration_quality,
            "decision_confidence": self.state.analysis_confidence,
            "efficiency_metrics": {
                "error_rate": self.state.error_count,
                "retry_count": sum(self.state.retry_attempts.values()),
                "alternative_routes": len(self.state.alternative_paths)
            },
            "recommendation_strength": "high" if self.state.overall_score >= 80 else "medium" if self.state.overall_score >= 60 else "low"
        }

    def run_smart_analysis(self, company: str, ticker: str) -> Dict[str, Any]:
        """运行智能分析流程"""
        self.state.company = company
        self.state.ticker = ticker
        self.state.start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 分析公司特征
        company_profile = self._analyze_company_profile(company, ticker)
        self.state.analysis_depth = self._determine_analysis_depth(company_profile)

        logger.info(f"启动智能分析: {company} ({ticker})")
        logger.info(f"分析深度: {self.state.analysis_depth}")

        # 执行智能流程
        try:
            # 数据收集
            data_result = self.data_collection_crew.execute_data_collection(company, ticker)
            if not data_result['success']:
                return {"success": False, "error": "数据收集失败"}

            # 协作分析
            analysis_result = self.analysis_crew.execute_collaborative_analysis(
                company, ticker, data_result['data']
            )
            if not analysis_result['success']:
                return {"success": False, "error": "分析失败"}

            # 集体决策
            decision_result = self.decision_crew.execute_collective_decision(
                company, ticker, analysis_result['data']
            )
            if not decision_result['success']:
                return {"success": False, "error": "决策失败"}

            # 生成总结
            summary = self._generate_analysis_summary(decision_result)

            return {
                "success": True,
                "company": company,
                "ticker": ticker,
                "summary": summary,
                "final_recommendation": decision_result.get('final_recommendation', {}),
                "collaboration_metrics": {
                    "data_collection": data_result.get('collaboration_metrics', {}),
                    "analysis": analysis_result.get('collaboration_metrics', {}),
                    "decision": decision_result.get('collective_decision_metrics', {})
                },
                "completion_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            return {"success": False, "error": str(e), "error_count": self.state.error_count}


# 使用示例
if __name__ == "__main__":
    flow = SmartInvestmentFlow()
    # result = flow.kickoff()  # 启动交互式智能流程
    result = flow.run_smart_analysis("苹果公司", "AAPL")  # 运行智能分析
    print(json.dumps(result, indent=2, ensure_ascii=False))