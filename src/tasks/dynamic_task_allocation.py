"""
动态任务分配和集体决策系统
实现智能体间的动态任务分配、负载均衡和集体决策机制
"""
from typing import Dict, Any, List, Optional, Callable, Tuple
from enum import Enum
import logging
import json
from datetime import datetime
from dataclasses import dataclass, field
import uuid
from collections import defaultdict, Counter
import heapq

# 导入通信工具
from ..tools.communication_tools import AgentCommunicationHub, Message, MessageType, MessagePriority

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskComplexity(Enum):
    """任务复杂度"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class AgentCapability(Enum):
    """智能体能力"""
    FUNDAMENTAL_ANALYSIS = "fundamental_analysis"
    TECHNICAL_ANALYSIS = "technical_analysis"
    MARKET_RESEARCH = "market_research"
    RISK_ASSESSMENT = "risk_assessment"
    DATA_COLLECTION = "data_collection"
    QUANTITATIVE_ANALYSIS = "quantitative_analysis"
    INDUSTRY_ANALYSIS = "industry_analysis"
    DECISION_MAKING = "decision_making"
    VALIDATION = "validation"
    COORDINATION = "coordination"


class DecisionType(Enum):
    """决策类型"""
    UNANIMOUS = "unanimous"  # 一致同意
    MAJORITY = "majority"    # 多数决定
    WEIGHTED = "weighted"    # 加权投票
    HIERARCHICAL = "hierarchical"  # 层级决策
    CONSENSUS = "consensus"  # 共识决策


@dataclass
class AgentProfile:
    """智能体画像 - 包含能力、负载和偏好"""
    name: str
    capabilities: List[AgentCapability] = field(default_factory=list)
    capability_scores: Dict[AgentCapability, float] = field(default_factory=dict)
    current_workload: float = 0.0
    max_workload: float = 100.0
    task_history: List[str] = field(default_factory=list)
    success_rate: float = 0.0
    preferred_tasks: List[str] = field(default_factory=list)
    availability: bool = True
    last_active: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    expertise_level: Dict[AgentCapability, float] = field(default_factory=dict)

    def calculate_fitness(self, required_capabilities: List[AgentCapability],
                         task_complexity: TaskComplexity) -> float:
        """计算智能体对任务的适合度"""
        if not self.availability:
            return 0.0

        # 计算能力匹配度
        capability_match = 0.0
        for cap in required_capabilities:
            if cap in self.capabilities:
                capability_match += self.capability_scores.get(cap, 0.5)

        capability_match /= len(required_capabilities) if required_capabilities else 1

        # 计算负载影响
        workload_factor = 1.0 - (self.current_workload / self.max_workload)

        # 计算复杂度适应性
        complexity_factor = 1.0
        if task_complexity == TaskComplexity.CRITICAL:
            complexity_factor = self.success_rate
        elif task_complexity == TaskComplexity.HIGH:
            complexity_factor = 0.8 + 0.2 * self.success_rate

        # 综合适合度
        fitness = capability_match * workload_factor * complexity_factor
        return max(0.0, min(1.0, fitness))


@dataclass
class DynamicTask:
    """动态任务"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    required_capabilities: List[AgentCapability] = field(default_factory=list)
    complexity: TaskComplexity = TaskComplexity.MEDIUM
    estimated_duration: int = 60  # 预估时间（分钟）
    priority: int = 1  # 优先级 1-10
    dependencies: List[str] = field(default_factory=list)  # 依赖任务ID
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VotingRecord:
    """投票记录"""
    vote_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    topic: str = ""
    decision_type: DecisionType = DecisionType.MAJORITY
    options: List[str] = field(default_factory=list)
    voters: List[str] = field(default_factory=list)
    votes: Dict[str, str] = field(default_factory=dict)  # voter -> option
    weights: Dict[str, float] = field(default_factory=dict)  # voter -> weight
    status: str = "open"  # open, closed, cancelled
    created_at: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    closed_at: Optional[str] = None
    result: Optional[str] = None
    confidence: float = 0.0
    discussion_summary: str = ""


class DynamicTaskAllocator:
    """动态任务分配器"""

    def __init__(self, communication_hub: AgentCommunicationHub):
        self.communication_hub = communication_hub
        self.agent_profiles: Dict[str, AgentProfile] = {}
        self.task_queue: List[DynamicTask] = []
        self.active_tasks: Dict[str, DynamicTask] = {}
        self.completed_tasks: Dict[str, DynamicTask] = {}
        self.allocation_history: List[Dict[str, Any]] = []
        self.load_balancing_enabled = True

    def register_agent(self, agent_name: str, capabilities: List[AgentCapability],
                      capability_scores: Dict[AgentCapability, float] = None,
                      max_workload: float = 100.0) -> AgentProfile:
        """注册智能体"""
        profile = AgentProfile(
            name=agent_name,
            capabilities=capabilities,
            capability_scores=capability_scores or {},
            max_workload=max_workload
        )
        self.agent_profiles[agent_name] = profile
        logger.info(f"智能体已注册: {agent_name}, 能力: {[cap.value for cap in capabilities]}")
        return profile

    def create_task(self, name: str, description: str,
                  required_capabilities: List[AgentCapability],
                  complexity: TaskComplexity = TaskComplexity.MEDIUM,
                  priority: int = 1, dependencies: List[str] = None) -> str:
        """创建新任务"""
        task = DynamicTask(
            name=name,
            description=description,
            required_capabilities=required_capabilities,
            complexity=complexity,
            priority=priority,
            dependencies=dependencies or []
        )

        # 使用优先级队列管理任务
        heapq.heappush(self.task_queue, (-priority, task.id, task))
        logger.info(f"任务已创建: {name} (ID: {task.id})")
        return task.id

    def allocate_tasks(self) -> List[str]:
        """分配待处理任务"""
        allocated_tasks = []

        while self.task_queue:
            _, task_id, task = heapq.heappop(self.task_queue)

            # 检查依赖是否满足
            if not self._check_dependencies(task):
                # 重新放回队列
                heapq.heappush(self.task_queue, (-task.priority, task_id, task))
                continue

            # 选择最佳智能体
            best_agent = self._select_best_agent(task)
            if best_agent:
                self._assign_task(task, best_agent)
                allocated_tasks.append(task.id)
            else:
                # 没有合适的智能体，重新放回队列
                heapq.heappush(self.task_queue, (-task.priority, task_id, task))
                logger.warning(f"没有找到合适的智能体执行任务: {task.name}")
                break

        return allocated_tasks

    def _select_best_agent(self, task: DynamicTask) -> Optional[str]:
        """选择最适合执行任务的智能体"""
        available_agents = []

        for agent_name, profile in self.agent_profiles.items():
            if not profile.availability:
                continue

            fitness = profile.calculate_fitness(task.required_capabilities, task.complexity)
            if fitness > 0:
                available_agents.append((agent_name, fitness))

        if not available_agents:
            return None

        # 按适合度排序
        available_agents.sort(key=lambda x: x[1], reverse=True)

        # 负载均衡：考虑当前工作负载
        if self.load_balancing_enabled and len(available_agents) > 1:
            # 选择前3名中负载最低的
            top_candidates = available_agents[:3]
            best_agent = min(top_candidates,
                           key=lambda x: self.agent_profiles[x[0]].current_workload)
            return best_agent[0]
        else:
            return available_agents[0][0]

    def _assign_task(self, task: DynamicTask, agent_name: str):
        """分配任务给智能体"""
        task.assigned_agent = agent_name
        task.status = TaskStatus.ASSIGNED
        task.started_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 更新智能体负载
        profile = self.agent_profiles[agent_name]
        profile.current_workload += task.estimated_duration
        profile.task_history.append(task.id)

        # 记录分配历史
        self.allocation_history.append({
            'task_id': task.id,
            'task_name': task.name,
            'agent': agent_name,
            'allocated_at': task.started_at,
            'complexity': task.complexity.value,
            'priority': task.priority
        })

        # 发送任务分配通知
        self.communication_hub.send_message(
            sender="TaskAllocator",
            receiver=agent_name,
            message_type=MessageType.TASK_DELEGATION,
            subject=f"新任务分配: {task.name}",
            content={
                'task_id': task.id,
                'task_name': task.name,
                'description': task.description,
                'complexity': task.complexity.value,
                'priority': task.priority,
                'estimated_duration': task.estimated_duration
            },
            priority=MessagePriority.HIGH
        )

        self.active_tasks[task.id] = task
        logger.info(f"任务已分配: {task.name} -> {agent_name}")

    def complete_task(self, task_id: str, result: Dict[str, Any], success: bool = True):
        """完成任务"""
        if task_id not in self.active_tasks:
            logger.error(f"任务不存在或未激活: {task_id}")
            return

        task = self.active_tasks[task_id]
        task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
        task.completed_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        task.result = result

        # 更新智能体负载和成功率
        if task.assigned_agent:
            profile = self.agent_profiles[task.assigned_agent]
            profile.current_workload -= task.estimated_duration
            profile.current_workload = max(0, profile.current_workload)

            # 更新成功率
            if success:
                profile.success_rate = (profile.success_rate * len(profile.task_history) + 1) / (len(profile.task_history) + 1)
            else:
                profile.success_rate = (profile.success_rate * len(profile.task_history)) / (len(profile.task_history) + 1)

        # 移动到已完成任务
        self.completed_tasks[task_id] = task
        del self.active_tasks[task_id]

        logger.info(f"任务已完成: {task.name} ({'成功' if success else '失败'})")

    def _check_dependencies(self, task: DynamicTask) -> bool:
        """检查任务依赖是否满足"""
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                return False
        return True

    def get_agent_workload(self, agent_name: str) -> Dict[str, Any]:
        """获取智能体工作负载"""
        if agent_name not in self.agent_profiles:
            return {}

        profile = self.agent_profiles[agent_name]
        active_task_count = len([t for t in self.active_tasks.values() if t.assigned_agent == agent_name])

        return {
            'current_workload': profile.current_workload,
            'max_workload': profile.max_workload,
            'workload_percentage': (profile.current_workload / profile.max_workload) * 100,
            'active_tasks': active_task_count,
            'success_rate': profile.success_rate,
            'availability': profile.availability,
            'capabilities': [cap.value for cap in profile.capabilities]
        }

    def get_allocation_statistics(self) -> Dict[str, Any]:
        """获取任务分配统计"""
        total_tasks = len(self.completed_tasks) + len(self.active_tasks) + len(self.task_queue)

        if total_tasks == 0:
            return {'total_tasks': 0}

        agent_stats = defaultdict(lambda: {'assigned': 0, 'completed': 0, 'failed': 0})

        for task in self.completed_tasks.values():
            if task.assigned_agent:
                if task.status == TaskStatus.COMPLETED:
                    agent_stats[task.assigned_agent]['completed'] += 1
                else:
                    agent_stats[task.assigned_agent]['failed'] += 1

        for task in self.active_tasks.values():
            if task.assigned_agent:
                agent_stats[task.assigned_agent]['assigned'] += 1

        return {
            'total_tasks': total_tasks,
            'pending_tasks': len(self.task_queue),
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'agent_statistics': dict(agent_stats),
            'average_completion_time': self._calculate_average_completion_time()
        }

    def _calculate_average_completion_time(self) -> float:
        """计算平均任务完成时间"""
        if not self.completed_tasks:
            return 0.0

        total_time = 0
        completed_count = 0

        for task in self.completed_tasks.values():
            if task.started_at and task.completed_at:
                try:
                    start = datetime.strptime(task.started_at, '%Y-%m-%d %H:%M:%S')
                    end = datetime.strptime(task.completed_at, '%Y-%m-%d %H:%M:%S')
                    total_time += (end - start).total_seconds()
                    completed_count += 1
                except:
                    continue

        return total_time / completed_count if completed_count > 0 else 0.0


class CollectiveDecisionMaker:
    """集体决策制定器"""

    def __init__(self, communication_hub: AgentCommunicationHub):
        self.communication_hub = communication_hub
        self.active_votes: Dict[str, VotingRecord] = {}
        self.vote_history: List[VotingRecord] = []
        self.decision_rules: Dict[str, Dict[str, Any]] = {}

    def create_vote(self, topic: str, options: List[str], voters: List[str],
                   decision_type: DecisionType = DecisionType.MAJORITY,
                   weights: Dict[str, float] = None) -> str:
        """创建投票"""
        vote = VotingRecord(
            topic=topic,
            decision_type=decision_type,
            options=options,
            voters=voters,
            weights=weights or {}
        )

        self.active_votes[vote.vote_id] = vote

        # 通知所有投票者
        for voter in voters:
            self.communication_hub.send_message(
                sender="DecisionMaker",
                receiver=voter,
                message_type=MessageType.DECISION_REQUEST,
                subject=f"投票请求: {topic}",
                content={
                    'vote_id': vote.vote_id,
                    'topic': topic,
                    'options': options,
                    'decision_type': decision_type.value,
                    'deadline': vote.created_at
                },
                priority=MessagePriority.NORMAL
            )

        logger.info(f"投票已创建: {topic} (ID: {vote.vote_id})")
        return vote.vote_id

    def cast_vote(self, vote_id: str, voter: str, option: str):
        """投票"""
        if vote_id not in self.active_votes:
            raise ValueError(f"投票不存在: {vote_id}")

        vote = self.active_votes[vote_id]

        if voter not in vote.voters:
            raise ValueError(f"投票者无权限: {voter}")

        if option not in vote.options:
            raise ValueError(f"无效选项: {option}")

        vote.votes[voter] = option

        # 检查是否所有投票者都已投票
        if len(vote.votes) == len(vote.voters):
            self._finalize_vote(vote_id)

    def _finalize_vote(self, vote_id: str):
        """完成投票并计算结果"""
        vote = self.active_votes[vote_id]

        # 根据决策类型计算结果
        if vote.decision_type == DecisionType.UNANIMOUS:
            result = self._unanimous_decision(vote)
        elif vote.decision_type == DecisionType.MAJORITY:
            result = self._majority_decision(vote)
        elif vote.decision_type == DecisionType.WEIGHTED:
            result = self._weighted_decision(vote)
        elif vote.decision_type == DecisionType.HIERARCHICAL:
            result = self._hierarchical_decision(vote)
        elif vote.decision_type == DecisionType.CONSENSUS:
            result = self._consensus_decision(vote)
        else:
            result = self._majority_decision(vote)

        vote.result = result['winner']
        vote.confidence = result['confidence']
        vote.status = "closed"
        vote.closed_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 移动到历史记录
        self.vote_history.append(vote)
        del self.active_votes[vote_id]

        # 通知投票结果
        self._notify_vote_result(vote)

        logger.info(f"投票已完成: {vote.topic}, 结果: {vote.result}")

    def _unanimous_decision(self, vote: VotingRecord) -> Dict[str, Any]:
        """一致同意决策"""
        vote_counts = Counter(vote.votes.values())

        # 检查是否有选项获得所有票数
        for option, count in vote_counts.items():
            if count == len(vote.voters):
                return {'winner': option, 'confidence': 1.0}

        # 没有一致同意
        return {'winner': 'no_consensus', 'confidence': 0.0}

    def _majority_decision(self, vote: VotingRecord) -> Dict[str, Any]:
        """多数决定"""
        vote_counts = Counter(vote.votes.values())
        total_votes = len(vote.votes)

        if not vote_counts:
            return {'winner': 'no_votes', 'confidence': 0.0}

        # 获取得票最多的选项
        winner, max_votes = vote_counts.most_common(1)[0]

        # 计算置信度
        confidence = max_votes / total_votes

        return {'winner': winner, 'confidence': confidence}

    def _weighted_decision(self, vote: VotingRecord) -> Dict[str, Any]:
        """加权投票"""
        option_weights = defaultdict(float)

        for voter, option in vote.votes.items():
            weight = vote.weights.get(voter, 1.0)
            option_weights[option] += weight

        if not option_weights:
            return {'winner': 'no_votes', 'confidence': 0.0}

        # 获取权重最高的选项
        winner = max(option_weights.items(), key=lambda x: x[1])[0]
        total_weight = sum(option_weights.values())
        confidence = option_weights[winner] / total_weight

        return {'winner': winner, 'confidence': confidence}

    def _hierarchical_decision(self, vote: VotingRecord) -> Dict[str, Any]:
        """层级决策"""
        # 简化的层级决策：根据投票者的层级权重
        hierarchy_weights = {
            'decision_moderator': 3.0,
            'investment_committee': 2.0,
            'analyst': 1.0
        }

        return self._weighted_decision_with_weights(vote, hierarchy_weights)

    def _consensus_decision(self, vote: VotingRecord) -> Dict[str, Any]:
        """共识决策"""
        vote_counts = Counter(vote.votes.values())
        total_votes = len(vote.votes)

        if not vote_counts:
            return {'winner': 'no_votes', 'confidence': 0.0}

        # 共识需要超过2/3的票数
        required_consensus = total_votes * 2 / 3

        for option, count in vote_counts.items():
            if count >= required_consensus:
                confidence = count / total_votes
                return {'winner': option, 'confidence': confidence}

        return {'winner': 'no_consensus', 'confidence': 0.0}

    def _weighted_decision_with_weights(self, vote: VotingRecord,
                                      weights: Dict[str, float]) -> Dict[str, Any]:
        """使用指定权重的加权决策"""
        option_weights = defaultdict(float)

        for voter, option in vote.votes.items():
            # 从投票者名称推断层级
            voter_weight = 1.0
            for role, weight in weights.items():
                if role in voter:
                    voter_weight = weight
                    break

            option_weights[option] += voter_weight

        if not option_weights:
            return {'winner': 'no_votes', 'confidence': 0.0}

        winner = max(option_weights.items(), key=lambda x: x[1])[0]
        total_weight = sum(option_weights.values())
        confidence = option_weights[winner] / total_weight

        return {'winner': winner, 'confidence': confidence}

    def _notify_vote_result(self, vote: VotingRecord):
        """通知投票结果"""
        result_message = f"投票结果: {vote.topic}\n"
        result_message += f"获胜选项: {vote.result}\n"
        result_message += f"置信度: {vote.confidence:.2f}\n"
        result_message += f"投票详情: {dict(vote.votes)}"

        for voter in vote.voters:
            self.communication_hub.send_message(
                sender="DecisionMaker",
                receiver=voter,
                message_type=MessageType.STATUS_UPDATE,
                subject=f"投票结果: {vote.topic}",
                content={
                    'vote_id': vote.vote_id,
                    'result': vote.result,
                    'confidence': vote.confidence,
                    'vote_counts': dict(Counter(vote.votes.values())),
                    'summary': result_message
                },
                priority=MessagePriority.NORMAL
            )

    def get_vote_status(self, vote_id: str) -> Dict[str, Any]:
        """获取投票状态"""
        if vote_id in self.active_votes:
            vote = self.active_votes[vote_id]
            return {
                'status': vote.status,
                'topic': vote.topic,
                'options': vote.options,
                'voters': vote.voters,
                'votes_cast': len(vote.votes),
                'total_voters': len(vote.voters),
                'decision_type': vote.decision_type.value
            }
        else:
            # 查找历史投票
            for vote in self.vote_history:
                if vote.vote_id == vote_id:
                    return {
                        'status': vote.status,
                        'topic': vote.topic,
                        'result': vote.result,
                        'confidence': vote.confidence,
                        'closed_at': vote.closed_at
                    }

        return {'error': f"投票不存在: {vote_id}"}

    def get_decision_statistics(self) -> Dict[str, Any]:
        """获取决策统计"""
        total_votes = len(self.vote_history) + len(self.active_votes)

        if total_votes == 0:
            return {'total_votes': 0}

        decision_type_stats = defaultdict(int)
        confidence_scores = []

        for vote in self.vote_history:
            decision_type_stats[vote.decision_type.value] += 1
            confidence_scores.append(vote.confidence)

        return {
            'total_votes': total_votes,
            'active_votes': len(self.active_votes),
            'completed_votes': len(self.vote_history),
            'decision_type_distribution': dict(decision_type_stats),
            'average_confidence': sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        }


# 全局实例
_global_task_allocator = None
_global_decision_maker = None


def get_task_allocator(communication_hub: AgentCommunicationHub = None) -> DynamicTaskAllocator:
    """获取全局任务分配器"""
    global _global_task_allocator
    if _global_task_allocator is None:
        if communication_hub is None:
            from ..tools.communication_tools import global_communication_hub
            communication_hub = global_communication_hub
        _global_task_allocator = DynamicTaskAllocator(communication_hub)
    return _global_task_allocator


def get_decision_maker(communication_hub: AgentCommunicationHub = None) -> CollectiveDecisionMaker:
    """获取全局决策制定器"""
    global _global_decision_maker
    if _global_decision_maker is None:
        if communication_hub is None:
            from ..tools.communication_tools import global_communication_hub
            communication_hub = global_communication_hub
        _global_decision_maker = CollectiveDecisionMaker(communication_hub)
    return _global_decision_maker


# 工具函数
def create_analysis_task(company: str, ticker: str, analysis_type: str) -> str:
    """创建分析任务的便捷函数"""
    allocator = get_task_allocator()

    capabilities = {
        'fundamental': [AgentCapability.FUNDAMENTAL_ANALYSIS],
        'technical': [AgentCapability.TECHNICAL_ANALYSIS],
        'risk': [AgentCapability.RISK_ASSESSMENT],
        'quantitative': [AgentCapability.QUANTITATIVE_ANALYSIS],
        'industry': [AgentCapability.INDUSTRY_ANALYSIS]
    }

    return allocator.create_task(
        name=f"{analysis_type}_analysis_{company}",
        description=f"对{company}({ticker})进行{analysis_type}分析",
        required_capabilities=capabilities.get(analysis_type, [AgentCapability.FUNDAMENTAL_ANALYSIS]),
        complexity=TaskComplexity.HIGH,
        priority=8
    )


def create_investment_decision_vote(company: str, options: List[str]) -> str:
    """创建投资决策投票的便捷函数"""
    decision_maker = get_decision_maker()

    voters = [
        'investment_committee_chairman',
        'risk_management_director',
        'portfolio_manager',
        'fundamental_analyst',
        'technical_analyst'
    ]

    # 设置层级权重
    weights = {
        'investment_committee_chairman': 3.0,
        'risk_management_director': 2.5,
        'portfolio_manager': 2.0,
        'fundamental_analyst': 1.5,
        'technical_analyst': 1.0
    }

    return decision_maker.create_vote(
        topic=f"{company}投资决策",
        options=options,
        voters=voters,
        decision_type=DecisionType.WEIGHTED,
        weights=weights
    )


# 使用示例
if __name__ == "__main__":
    # 初始化系统
    from .communication_tools import global_communication_hub

    allocator = get_task_allocator()
    decision_maker = get_decision_maker()

    # 注册智能体
    allocator.register_agent(
        "fundamental_analyst",
        [AgentCapability.FUNDAMENTAL_ANALYSIS, AgentCapability.INDUSTRY_ANALYSIS],
        {AgentCapability.FUNDAMENTAL_ANALYSIS: 0.9, AgentCapability.INDUSTRY_ANALYSIS: 0.8}
    )

    allocator.register_agent(
        "technical_analyst",
        [AgentCapability.TECHNICAL_ANALYSIS, AgentCapability.QUANTITATIVE_ANALYSIS],
        {AgentCapability.TECHNICAL_ANALYSIS: 0.9, AgentCapability.QUANTITATIVE_ANALYSIS: 0.7}
    )

    # 创建任务
    task_id = allocator.create_task(
        name="苹果公司基本面分析",
        description="对苹果公司进行深度基本面分析",
        required_capabilities=[AgentCapability.FUNDAMENTAL_ANALYSIS],
        complexity=TaskComplexity.HIGH,
        priority=9
    )

    # 分配任务
    allocated = allocator.allocate_tasks()
    print(f"已分配任务: {allocated}")

    # 创建投票
    vote_id = decision_maker.create_vote(
        topic="是否买入AAPL",
        options=["买入", "持有", "卖出"],
        voters=["committee_chairman", "risk_director", "portfolio_manager"],
        decision_type=DecisionType.MAJORITY
    )

    # 模拟投票
    decision_maker.cast_vote(vote_id, "committee_chairman", "买入")
    decision_maker.cast_vote(vote_id, "risk_director", "持有")
    decision_maker.cast_vote(vote_id, "portfolio_manager", "买入")

    # 查看结果
    stats = allocator.get_allocation_statistics()
    print("任务分配统计:", json.dumps(stats, indent=2, ensure_ascii=False))

    decision_stats = decision_maker.get_decision_statistics()
    print("决策统计:", json.dumps(decision_stats, indent=2, ensure_ascii=False))