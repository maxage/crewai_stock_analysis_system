"""
智能体协作工具集
提供智能体间的高级协作功能，包括任务分配、集体决策和协作优化
"""
from typing import Dict, Any, List, Optional, Tuple
import logging
import json
from datetime import datetime

from .communication_tools import global_communication_hub, Message, MessageType, MessagePriority
from ..tasks.dynamic_task_allocation import (
    get_task_allocator, get_decision_maker, AgentCapability, TaskComplexity,
    DecisionType, DynamicTask, AgentProfile
)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CollaborationOptimizer:
    """协作优化器 - 优化智能体间的协作效率和任务分配"""

    def __init__(self):
        self.task_allocator = get_task_allocator()
        self.decision_maker = get_decision_maker()
        self.collaboration_history: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, Dict[str, float]] = {}

    def analyze_collaboration_patterns(self) -> Dict[str, Any]:
        """分析协作模式和效率"""
        # 获取通信统计
        comm_report = global_communication_hub.generate_communication_report()

        # 获取任务分配统计
        task_stats = self.task_allocator.get_allocation_statistics()

        # 获取决策统计
        decision_stats = self.decision_maker.get_decision_statistics()

        # 分析协作效率
        collaboration_efficiency = self._calculate_collaboration_efficiency(comm_report, task_stats)

        # 识别协作瓶颈
        bottlenecks = self._identify_collaboration_bottlenecks(comm_report, task_stats)

        # 生成优化建议
        recommendations = self._generate_optimization_recommendations(
            comm_report, task_stats, decision_stats, bottlenecks
        )

        return {
            'collaboration_efficiency': collaboration_efficiency,
            'bottlenecks': bottlenecks,
            'recommendations': recommendations,
            'communication_metrics': comm_report,
            'task_metrics': task_stats,
            'decision_metrics': decision_stats,
            'analysis_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def _calculate_collaboration_efficiency(self, comm_report: Dict[str, Any],
                                         task_stats: Dict[str, Any]) -> float:
        """计算协作效率分数"""
        efficiency_score = 0.0

        # 通信效率权重 (30%)
        comm_efficiency = comm_report.get('communication_efficiency', 0.5)
        efficiency_score += comm_efficiency * 0.3

        # 任务完成效率权重 (40%)
        if task_stats.get('total_tasks', 0) > 0:
            completion_rate = task_stats.get('completed_tasks', 0) / task_stats['total_tasks']
            efficiency_score += completion_rate * 0.4

        # 决策效率权重 (30%)
        decision_stats = self.decision_maker.get_decision_statistics()
        if decision_stats.get('total_votes', 0) > 0:
            avg_confidence = decision_stats.get('average_confidence', 0.5)
            efficiency_score += avg_confidence * 0.3

        return min(1.0, max(0.0, efficiency_score))

    def _identify_collaboration_bottlenecks(self, comm_report: Dict[str, Any],
                                          task_stats: Dict[str, Any]) -> List[str]:
        """识别协作瓶颈"""
        bottlenecks = []

        # 检查通信瓶颈
        if comm_report.get('communication_efficiency', 1.0) < 0.5:
            bottlenecks.append("通信效率较低，响应时间过长")

        # 检查任务分配瓶颈
        if task_stats.get('pending_tasks', 0) > 5:
            bottlenecks.append("待处理任务积压，任务分配不及时")

        # 检查智能体负载不均衡
        agent_stats = task_stats.get('agent_statistics', {})
        if agent_stats:
            workloads = [stats.get('assigned', 0) for stats in agent_stats.values()]
            if max(workloads) - min(workloads) > 3:
                bottlenecks.append("智能体负载不均衡")

        return bottlenecks

    def _generate_optimization_recommendations(self, comm_report: Dict[str, Any],
                                             task_stats: Dict[str, Any],
                                             decision_stats: Dict[str, Any],
                                             bottlenecks: List[str]) -> List[str]:
        """生成优化建议"""
        recommendations = []

        # 基于瓶颈生成建议
        for bottleneck in bottlenecks:
            if "通信效率" in bottleneck:
                recommendations.append("优化消息路由机制，减少通信延迟")
                recommendations.append("增加智能体并行处理能力")
            elif "任务积压" in bottleneck:
                recommendations.append("增加任务分配频率")
                recommendations.append("优化任务优先级算法")
            elif "负载不均衡" in bottleneck:
                recommendations.append("启用动态负载均衡")
                recommendations.append("调整智能体能力权重")

        # 基于统计数据的建议
        if task_stats.get('average_completion_time', 0) > 3600:  # 超过1小时
            recommendations.append("任务完成时间过长，考虑任务分解")

        if decision_stats.get('average_confidence', 0) < 0.7:
            recommendations.append("决策置信度较低，改进决策机制")

        return recommendations

    def optimize_task_allocation(self) -> Dict[str, Any]:
        """优化任务分配策略"""
        optimization_actions = []

        # 分析当前分配情况
        task_stats = self.task_allocator.get_allocation_statistics()
        agent_stats = task_stats.get('agent_statistics', {})

        # 识别过载智能体
        overloaded_agents = []
        underutilized_agents = []

        for agent_name, stats in agent_stats.items():
            workload = self.task_allocator.get_agent_workload(agent_name)
            workload_percentage = workload.get('workload_percentage', 0)

            if workload_percentage > 80:
                overloaded_agents.append(agent_name)
            elif workload_percentage < 30:
                underutilized_agents.append(agent_name)

        # 实施负载均衡
        if overloaded_agents and underutilized_agents:
            optimization_actions.append(
                f"负载均衡: 从{overloaded_agents}重新分配任务到{underutilized_agents}"
            )

        # 调整分配策略
        if len(overloaded_agents) > len(underutilized_agents):
            self.task_allocator.load_balancing_enabled = True
            optimization_actions.append("启用负载均衡模式")

        return {
            'optimization_actions': optimization_actions,
            'overloaded_agents': overloaded_agents,
            'underutilized_agents': underutilized_agents,
            'optimization_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


class TaskOrchestrationTool:
    """任务编排工具 - 为智能体提供高级任务编排功能"""

    name: str = "Task Orchestration Tool"
    description: str = "提供智能体任务编排、协作优化和集体决策功能"

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.task_allocator = get_task_allocator()
        self.decision_maker = get_decision_maker()
        self.optimizer = CollaborationOptimizer()

    def _run(self, action: str, **kwargs) -> str:
        """执行任务编排操作"""
        try:
            if action == "create_task":
                return self._create_task(**kwargs)
            elif action == "allocate_tasks":
                return self._allocate_tasks()
            elif action == "complete_task":
                return self._complete_task(**kwargs)
            elif action == "create_vote":
                return self._create_vote(**kwargs)
            elif action == "cast_vote":
                return self._cast_vote(**kwargs)
            elif action == "analyze_collaboration":
                return self._analyze_collaboration()
            elif action == "optimize_workflow":
                return self._optimize_workflow()
            elif action == "get_workload":
                return self._get_workload()
            else:
                return f"未知操作: {action}"

        except Exception as e:
            logger.error(f"任务编排操作失败: {str(e)}")
            return f"错误: {str(e)}"

    def _create_task(self, name: str, description: str, capabilities: List[str],
                    complexity: str = "medium", priority: int = 1) -> str:
        """创建任务"""
        # 转换能力字符串为枚举
        capability_enums = []
        for cap_str in capabilities:
            try:
                capability_enums.append(AgentCapability(cap_str))
            except ValueError:
                logger.warning(f"未知能力: {cap_str}")

        # 转换复杂度字符串为枚举
        try:
            complexity_enum = TaskComplexity(complexity)
        except ValueError:
            complexity_enum = TaskComplexity.MEDIUM

        task_id = self.task_allocator.create_task(
            name=name,
            description=description,
            required_capabilities=capability_enums,
            complexity=complexity_enum,
            priority=priority
        )

        return f"任务已创建 (ID: {task_id})"

    def _allocate_tasks(self) -> str:
        """分配待处理任务"""
        allocated_tasks = self.task_allocator.allocate_tasks()

        if not allocated_tasks:
            return "没有可分配的任务"

        return f"已分配 {len(allocated_tasks)} 个任务: {', '.join(allocated_tasks)}"

    def _complete_task(self, task_id: str, result: Dict[str, Any], success: bool = True) -> str:
        """完成任务"""
        self.task_allocator.complete_task(task_id, result, success)
        return f"任务 {task_id} 已标记为完成"

    def _create_vote(self, topic: str, options: List[str], voters: List[str],
                    decision_type: str = "majority") -> str:
        """创建投票"""
        try:
            decision_enum = DecisionType(decision_type)
        except ValueError:
            decision_enum = DecisionType.MAJORITY

        vote_id = self.decision_maker.create_vote(
            topic=topic,
            options=options,
            voters=voters,
            decision_type=decision_enum
        )

        return f"投票已创建 (ID: {vote_id})"

    def _cast_vote(self, vote_id: str, option: str) -> str:
        """投票"""
        self.decision_maker.cast_vote(vote_id, self.agent_name, option)
        return f"投票已提交: {option}"

    def _analyze_collaboration(self) -> str:
        """分析协作效率"""
        analysis = self.optimizer.analyze_collaboration_patterns()

        result = f"协作效率分析:\n"
        result += f"- 效率分数: {analysis['collaboration_efficiency']:.2f}\n"
        result += f"- 瓶颈数量: {len(analysis['bottlenecks'])}\n"
        result += f"- 优化建议: {len(analysis['recommendations'])}条\n"

        if analysis['bottlenecks']:
            result += f"\n发现的瓶颈:\n"
            for bottleneck in analysis['bottlenecks']:
                result += f"- {bottleneck}\n"

        if analysis['recommendations']:
            result += f"\n优化建议:\n"
            for rec in analysis['recommendations']:
                result += f"- {rec}\n"

        return result

    def _optimize_workflow(self) -> str:
        """优化工作流程"""
        optimization = self.optimizer.optimize_task_allocation()

        result = f"工作流程优化:\n"
        result += f"- 优化操作: {len(optimization['optimization_actions'])}条\n"
        result += f"- 过载智能体: {len(optimization['overloaded_agents'])}个\n"
        result += f"- 低利用智能体: {len(optimization['underutilized_agents'])}个\n"

        if optimization['optimization_actions']:
            result += f"\n优化操作:\n"
            for action in optimization['optimization_actions']:
                result += f"- {action}\n"

        return result

    def _get_workload(self) -> str:
        """获取工作负载"""
        workload = self.task_allocator.get_agent_workload(self.agent_name)

        if not workload:
            return f"智能体 {self.agent_name} 的工作负载信息不可用"

        result = f"智能体 {self.agent_name} 的工作负载:\n"
        result += f"- 当前负载: {workload['current_workload']:.1f}/{workload['max_workload']:.1f}\n"
        result += f"- 负载百分比: {workload['workload_percentage']:.1f}%\n"
        result += f"- 活跃任务: {workload['active_tasks']}\n"
        result += f"- 成功率: {workload['success_rate']:.2f}\n"
        result += f"- 可用性: {'可用' if workload['availability'] else '不可用'}\n"
        result += f"- 能力: {', '.join(workload['capabilities'])}"

        return result


class CollectiveDecisionTool:
    """集体决策工具 - 为智能体提供集体决策功能"""

    name: str = "Collective Decision Tool"
    description: str = "提供智能体集体决策、投票和共识形成功能"

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.decision_maker = get_decision_maker()

    def _run(self, action: str, **kwargs) -> str:
        """执行集体决策操作"""
        try:
            if action == "create_investment_vote":
                return self._create_investment_vote(**kwargs)
            elif action == "create_risk_assessment_vote":
                return self._create_risk_assessment_vote(**kwargs)
            elif action == "create_strategy_vote":
                return self._create_strategy_vote(**kwargs)
            elif action == "get_vote_status":
                return self._get_vote_status(**kwargs)
            elif action == "get_decision_stats":
                return self._get_decision_stats()
            else:
                return f"未知操作: {action}"

        except Exception as e:
            logger.error(f"集体决策操作失败: {str(e)}")
            return f"错误: {str(e)}"

    def _create_investment_vote(self, company: str, ticker: str, options: List[str] = None) -> str:
        """创建投资决策投票"""
        if options is None:
            options = ["强烈买入", "买入", "持有", "卖出", "强烈卖出"]

        voters = [
            f"{self.agent_name}_committee",
            f"{self.agent_name}_risk_director",
            f"{self.agent_name}_portfolio_manager",
            f"{self.agent_name}_analyst"
        ]

        # 设置权重
        weights = {
            f"{self.agent_name}_committee": 3.0,
            f"{self.agent_name}_risk_director": 2.5,
            f"{self.agent_name}_portfolio_manager": 2.0,
            f"{self.agent_name}_analyst": 1.0
        }

        vote_id = self.decision_maker.create_vote(
            topic=f"{company}({ticker})投资决策",
            options=options,
            voters=voters,
            decision_type=DecisionType.WEIGHTED,
            weights=weights
        )

        return f"投资决策投票已创建 (ID: {vote_id})"

    def _create_risk_assessment_vote(self, risk_type: str, options: List[str] = None) -> str:
        """创建风险评估投票"""
        if options is None:
            options = ["低风险", "中等风险", "高风险", "极高风险"]

        voters = [
            f"{self.agent_name}_risk_expert",
            f"{self.agent_name}_analyst",
            f"{self.agent_name}_manager"
        ]

        vote_id = self.decision_maker.create_vote(
            topic=f"{risk_type}风险评估",
            options=options,
            voters=voters,
            decision_type=DecisionType.MAJORITY
        )

        return f"风险评估投票已创建 (ID: {vote_id})"

    def _create_strategy_vote(self, strategy_name: str, options: List[str]) -> str:
        """创建策略投票"""
        voters = [
            f"{self.agent_name}_strategist",
            f"{self.agent_name}_analyst",
            f"{self.agent_name}_manager"
        ]

        vote_id = self.decision_maker.create_vote(
            topic=f"{strategy_name}策略选择",
            options=options,
            voters=voters,
            decision_type=DecisionType.CONSENSUS
        )

        return f"策略投票已创建 (ID: {vote_id})"

    def _get_vote_status(self, vote_id: str) -> str:
        """获取投票状态"""
        status = self.decision_maker.get_vote_status(vote_id)

        if 'error' in status:
            return status['error']

        result = f"投票状态 (ID: {vote_id}):\n"
        result += f"- 状态: {status['status']}\n"
        result += f"- 主题: {status['topic']}\n"
        result += f"- 选项: {', '.join(status['options'])}\n"

        if 'votes_cast' in status:
            result += f"- 已投票: {status['votes_cast']}/{status['total_voters']}\n"

        if 'result' in status:
            result += f"- 结果: {status['result']}\n"
            result += f"- 置信度: {status.get('confidence', 0):.2f}\n"

        return result

    def _get_decision_stats(self) -> str:
        """获取决策统计"""
        stats = self.decision_maker.get_decision_statistics()

        result = f"决策统计:\n"
        result += f"- 总投票数: {stats['total_votes']}\n"
        result += f"- 活跃投票: {stats['active_votes']}\n"
        result += f"- 完成投票: {stats['completed_votes']}\n"
        result += f"- 平均置信度: {stats['average_confidence']:.2f}\n"

        if 'decision_type_distribution' in stats:
            result += f"\n决策类型分布:\n"
            for decision_type, count in stats['decision_type_distribution'].items():
                result += f"- {decision_type}: {count}\n"

        return result


# 工厂函数
def get_task_orchestration_tool(agent_name: str) -> TaskOrchestrationTool:
    """获取任务编排工具"""
    return TaskOrchestrationTool(agent_name)


def get_collective_decision_tool(agent_name: str) -> CollectiveDecisionTool:
    """获取集体决策工具"""
    return CollectiveDecisionTool(agent_name)


# 便捷函数
def create_collaborative_analysis_task(company: str, ticker: str,
                                     analysis_types: List[str]) -> List[str]:
    """创建协作分析任务的便捷函数"""
    allocator = get_task_allocator()
    task_ids = []

    capability_mapping = {
        'fundamental': [AgentCapability.FUNDAMENTAL_ANALYSIS],
        'technical': [AgentCapability.TECHNICAL_ANALYSIS],
        'risk': [AgentCapability.RISK_ASSESSMENT],
        'quantitative': [AgentCapability.QUANTITATIVE_ANALYSIS],
        'industry': [AgentCapability.INDUSTRY_ANALYSIS]
    }

    for analysis_type in analysis_types:
        if analysis_type in capability_mapping:
            task_id = allocator.create_task(
                name=f"{analysis_type}_analysis_{company}",
                description=f"对{company}({ticker})进行{analysis_type}分析",
                required_capabilities=capability_mapping[analysis_type],
                complexity=TaskComplexity.HIGH,
                priority=8
            )
            task_ids.append(task_id)

    # 分配任务
    allocator.allocate_tasks()

    return task_ids


def create_investment_decision_committee(company: str, ticker: str) -> str:
    """创建投资决策委员会的便捷函数"""
    decision_maker = get_decision_maker()

    options = ["强烈买入", "买入", "持有", "卖出", "强烈卖出"]
    voters = [
        "investment_committee_chairman",
        "risk_management_director",
        "portfolio_manager",
        "chief_analyst",
        "compliance_officer"
    ]

    weights = {
        "investment_committee_chairman": 3.0,
        "risk_management_director": 2.5,
        "portfolio_manager": 2.0,
        "chief_analyst": 1.5,
        "compliance_officer": 1.0
    }

    return decision_maker.create_vote(
        topic=f"{company}({ticker})投资决策委员会投票",
        options=options,
        voters=voters,
        decision_type=DecisionType.WEIGHTED,
        weights=weights
    )


# 使用示例
if __name__ == "__main__":
    # 初始化工具
    orchestration_tool = get_task_orchestration_tool("test_agent")
    decision_tool = get_collective_decision_tool("test_agent")

    # 创建任务
    task_result = orchestration_tool._run(
        "create_task",
        name="测试任务",
        description="这是一个测试任务",
        capabilities=["fundamental_analysis"],
        complexity="high",
        priority=9
    )
    print(task_result)

    # 分配任务
    alloc_result = orchestration_tool._run("allocate_tasks")
    print(alloc_result)

    # 创建投票
    vote_result = decision_tool._run(
        "create_investment_vote",
        company="苹果公司",
        ticker="AAPL",
        options=["买入", "持有", "卖出"]
    )
    print(vote_result)

    # 分析协作
    analysis_result = orchestration_tool._run("analyze_collaboration")
    print(analysis_result)