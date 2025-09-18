"""
智能体通信和任务委托工具
实现CrewAI智能体间的通信、消息传递和任务委托机制
"""
from crewai import Agent, Task
from typing import Dict, Any, List, Optional, Callable
import logging
import json
import asyncio
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageType(Enum):
    """消息类型枚举"""
    TASK_DELEGATION = "task_delegation"
    INFORMATION_REQUEST = "information_request"
    INFORMATION_SHARE = "information_share"
    COLLABORATION_INVITE = "collaboration_invite"
    STATUS_UPDATE = "status_update"
    ERROR_REPORT = "error_report"
    DECISION_REQUEST = "decision_request"
    FEEDBACK = "feedback"


class MessagePriority(Enum):
    """消息优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class Message:
    """智能体间通信消息"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    receiver: str = ""
    message_type: MessageType = MessageType.INFORMATION_SHARE
    priority: MessagePriority = MessagePriority.NORMAL
    subject: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    requires_response: bool = False
    response_deadline: Optional[str] = None
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'id': self.id,
            'sender': self.sender,
            'receiver': self.receiver,
            'message_type': self.message_type.value,
            'priority': self.priority.value,
            'subject': self.subject,
            'content': self.content,
            'timestamp': self.timestamp,
            'requires_response': self.requires_response,
            'response_deadline': self.response_deadline,
            'attachments': self.attachments,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """从字典创建消息"""
        return cls(
            id=data['id'],
            sender=data['sender'],
            receiver=data['receiver'],
            message_type=MessageType(data['message_type']),
            priority=MessagePriority(data['priority']),
            subject=data['subject'],
            content=data['content'],
            timestamp=data['timestamp'],
            requires_response=data['requires_response'],
            response_deadline=data.get('response_deadline'),
            attachments=data.get('attachments', []),
            metadata=data.get('metadata', {})
        )


@dataclass
class TaskDelegation:
    """任务委托记录"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    delegator: str = ""
    delegatee: str = ""
    original_task: str = ""
    delegated_task: str = ""
    reason: str = ""
    deadline: Optional[str] = None
    status: str = "pending"  # pending, accepted, rejected, completed, failed
    progress: float = 0.0
    feedback: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    updated_at: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


class AgentCommunicationHub:
    """智能体通信中心 - 管理智能体间的通信和任务委托"""

    def __init__(self):
        self.message_queue: List[Message] = []
        self.delegation_records: List[TaskDelegation] = []
        self.agent_status: Dict[str, Dict[str, Any]] = {}
        self.communication_history: List[Message] = []
        self.active_collaborations: Dict[str, List[str]] = {}  # collaboration_id -> [agent_names]

    def send_message(self, sender: str, receiver: str, message_type: MessageType,
                   subject: str, content: Dict[str, Any],
                   priority: MessagePriority = MessagePriority.NORMAL,
                   requires_response: bool = False,
                   attachments: List[Dict[str, Any]] = None) -> str:
        """发送消息到指定智能体"""
        message = Message(
            sender=sender,
            receiver=receiver,
            message_type=message_type,
            priority=priority,
            subject=subject,
            content=content,
            requires_response=requires_response,
            attachments=attachments or []
        )

        self.message_queue.append(message)
        self.communication_history.append(message)

        logger.info(f"消息已发送: {sender} -> {receiver} ({message_type.value}): {subject}")
        return message.id

    def delegate_task(self, delegator: str, delegatee: str, original_task: str,
                    delegated_task: str, reason: str, deadline: str = None) -> str:
        """委托任务给另一个智能体"""
        delegation = TaskDelegation(
            delegator=delegator,
            delegatee=delegatee,
            original_task=original_task,
            delegated_task=delegated_task,
            reason=reason,
            deadline=deadline
        )

        self.delegation_records.append(delegation)

        # 发送委托消息
        self.send_message(
            sender=delegator,
            receiver=delegatee,
            message_type=MessageType.TASK_DELEGATION,
            subject=f"任务委托: {original_task}",
            content={
                'delegation_id': delegation.id,
                'original_task': original_task,
                'delegated_task': delegated_task,
                'reason': reason,
                'deadline': deadline
            },
            priority=MessagePriority.HIGH,
            requires_response=True
        )

        logger.info(f"任务已委托: {delegator} -> {delegatee}: {original_task}")
        return delegation.id

    def get_messages_for_agent(self, agent_name: str, unread_only: bool = True) -> List[Message]:
        """获取指定智能体的消息"""
        return [msg for msg in self.message_queue
                if msg.receiver == agent_name and (not unread_only or msg not in self.agent_status.get(agent_name, {}).get('read_messages', []))]

    def respond_to_message(self, message_id: str, response_content: Dict[str, Any],
                         response_type: str = "accept") -> str:
        """响应消息"""
        # 找到原消息
        original_message = None
        for msg in self.message_queue:
            if msg.id == message_id:
                original_message = msg
                break

        if not original_message:
            raise ValueError(f"消息未找到: {message_id}")

        # 创建响应消息
        response = Message(
            sender=original_message.receiver,
            receiver=original_message.sender,
            message_type=MessageType.FEEDBACK,
            subject=f"回复: {original_message.subject}",
            content={
                'original_message_id': message_id,
                'response_type': response_type,
                'response_content': response_content
            },
            priority=MessagePriority.NORMAL
        )

        self.message_queue.append(response)
        self.communication_history.append(response)

        # 标记原消息为已读
        if original_message.receiver not in self.agent_status:
            self.agent_status[original_message.receiver] = {'read_messages': []}
        self.agent_status[original_message.receiver]['read_messages'].append(original_message)

        logger.info(f"响应已发送: {response.sender} -> {response.receiver} ({response_type})")
        return response.id

    def update_delegation_status(self, delegation_id: str, status: str,
                                progress: float = None, feedback: str = None):
        """更新委托任务状态"""
        for delegation in self.delegation_records:
            if delegation.id == delegation_id:
                delegation.status = status
                delegation.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                if progress is not None:
                    delegation.progress = progress
                if feedback:
                    delegation.feedback.append(feedback)

                logger.info(f"委托状态已更新: {delegation_id} -> {status}")
                return

        raise ValueError(f"委托记录未找到: {delegation_id}")

    def start_collaboration(self, initiator: str, participants: List[str],
                           collaboration_topic: str) -> str:
        """启动智能体协作"""
        collaboration_id = str(uuid.uuid4())
        self.active_collaborations[collaboration_id] = [initiator] + participants

        # 向所有参与者发送协作邀请
        for participant in participants:
            self.send_message(
                sender=initiator,
                receiver=participant,
                message_type=MessageType.COLLABORATION_INVITE,
                subject=f"协作邀请: {collaboration_topic}",
                content={
                    'collaboration_id': collaboration_id,
                    'topic': collaboration_topic,
                    'initiator': initiator,
                    'participants': self.active_collaborations[collaboration_id]
                },
                priority=MessagePriority.NORMAL,
                requires_response=True
            )

        logger.info(f"协作已启动: {collaboration_topic} (ID: {collaboration_id})")
        return collaboration_id

    def get_agent_workload(self, agent_name: str) -> Dict[str, Any]:
        """获取智能体工作负载"""
        active_delegations = [d for d in self.delegation_records
                             if d.delegatee == agent_name and d.status in ['pending', 'accepted']]

        pending_messages = len(self.get_messages_for_agent(agent_name))

        return {
            'active_delegations': len(active_delegations),
            'pending_messages': pending_messages,
            'collaboration_count': len([c for c in self.active_collaborations.values() if agent_name in c])
        }

    def generate_communication_report(self) -> Dict[str, Any]:
        """生成通信报告"""
        total_messages = len(self.communication_history)
        total_delegations = len(self.delegation_records)
        active_collaborations = len(self.active_collaborations)

        # 消息类型统计
        message_types = {}
        for msg in self.communication_history:
            msg_type = msg.message_type.value
            message_types[msg_type] = message_types.get(msg_type, 0) + 1

        # 委托状态统计
        delegation_status = {}
        for delegation in self.delegation_records:
            status = delegation.status
            delegation_status[status] = delegation_status.get(status, 0) + 1

        return {
            'total_messages': total_messages,
            'total_delegations': total_delegations,
            'active_collaborations': active_collaborations,
            'message_type_distribution': message_types,
            'delegation_status_distribution': delegation_status,
            'most_active_agents': self._get_most_active_agents(),
            'communication_efficiency': self._calculate_communication_efficiency()
        }

    def _get_most_active_agents(self) -> List[str]:
        """获取最活跃的智能体"""
        agent_activity = {}
        for msg in self.communication_history:
            agent_activity[msg.sender] = agent_activity.get(msg.sender, 0) + 1
            agent_activity[msg.receiver] = agent_activity.get(msg.receiver, 0) + 1

        return sorted(agent_activity.items(), key=lambda x: x[1], reverse=True)[:5]

    def _calculate_communication_efficiency(self) -> float:
        """计算通信效率"""
        if not self.communication_history:
            return 0.0

        # 计算平均响应时间
        response_times = []
        for i, msg in enumerate(self.communication_history):
            if msg.message_type == MessageType.FEEDBACK:
                # 找到对应的原消息
                for j in range(i):
                    prev_msg = self.communication_history[j]
                    if (prev_msg.id == msg.content.get('original_message_id') and
                        prev_msg.requires_response):
                        try:
                            time_diff = (datetime.strptime(msg.timestamp, '%Y-%m-%d %H:%M:%S') -
                                       datetime.strptime(prev_msg.timestamp, '%Y-%m-%d %H:%M:%S'))
                            response_times.append(time_diff.total_seconds())
                        except:
                            pass
                        break

        if not response_times:
            return 0.5  # 默认中等效率

        avg_response_time = sum(response_times) / len(response_times)

        # 响应时间越短，效率越高 (假设300秒为基准)
        efficiency = max(0, min(1, 300 / avg_response_time))
        return round(efficiency, 2)


class CommunicationTool:
    """智能体通信工具 - 为智能体提供通信能力"""

    name: str = "Agent Communication Tool"
    description: str = "提供智能体间通信、任务委托和协作功能"

    def __init__(self, agent_name: str, communication_hub: AgentCommunicationHub):
        self.agent_name = agent_name
        self.hub = communication_hub

    def _run(self, action: str, **kwargs) -> str:
        """执行通信操作"""
        try:
            if action == "send_message":
                return self._send_message(**kwargs)
            elif action == "delegate_task":
                return self._delegate_task(**kwargs)
            elif action == "respond_to_message":
                return self._respond_to_message(**kwargs)
            elif action == "start_collaboration":
                return self._start_collaboration(**kwargs)
            elif action == "check_messages":
                return self._check_messages(**kwargs)
            elif action == "get_workload":
                return self._get_workload()
            else:
                return f"未知操作: {action}"

        except Exception as e:
            logger.error(f"通信操作失败: {str(e)}")
            return f"错误: {str(e)}"

    def _send_message(self, receiver: str, message_type: str, subject: str,
                     content: Dict[str, Any], priority: str = "normal") -> str:
        """发送消息"""
        msg_type = MessageType(message_type)
        priority_level = MessagePriority[priority.upper()]

        message_id = self.hub.send_message(
            sender=self.agent_name,
            receiver=receiver,
            message_type=msg_type,
            subject=subject,
            content=content,
            priority=priority_level
        )

        return f"消息已发送 (ID: {message_id})"

    def _delegate_task(self, delegatee: str, original_task: str, delegated_task: str,
                       reason: str, deadline: str = None) -> str:
        """委托任务"""
        delegation_id = self.hub.delegate_task(
            delegator=self.agent_name,
            delegatee=delegatee,
            original_task=original_task,
            delegated_task=delegated_task,
            reason=reason,
            deadline=deadline
        )

        return f"任务已委托 (ID: {delegation_id})"

    def _respond_to_message(self, message_id: str, response_content: Dict[str, Any],
                           response_type: str = "accept") -> str:
        """响应消息"""
        response_id = self.hub.respond_to_message(
            message_id=message_id,
            response_content=response_content,
            response_type=response_type
        )

        return f"响应已发送 (ID: {response_id})"

    def _start_collaboration(self, participants: List[str], collaboration_topic: str) -> str:
        """启动协作"""
        collaboration_id = self.hub.start_collaboration(
            initiator=self.agent_name,
            participants=participants,
            collaboration_topic=collaboration_topic
        )

        return f"协作已启动 (ID: {collaboration_id})"

    def _check_messages(self, unread_only: bool = True) -> str:
        """检查消息"""
        messages = self.hub.get_messages_for_agent(self.agent_name, unread_only)

        if not messages:
            return "无新消息"

        message_list = []
        for msg in messages:
            message_list.append(f"- {msg.timestamp}: {msg.sender} -> {msg.subject} ({msg.message_type.value})")

        return f"收到 {len(messages)} 条消息:\n" + "\n".join(message_list)

    def _get_workload(self) -> str:
        """获取工作负载"""
        workload = self.hub.get_agent_workload(self.agent_name)

        return f"""
当前工作负载:
- 活跃委托任务: {workload['active_delegations']}
- 待处理消息: {workload['pending_messages']}
- 参与协作: {workload['collaboration_count']}
        """.strip()


# 全局通信中心实例
global_communication_hub = AgentCommunicationHub()


def get_communication_tool(agent_name: str) -> CommunicationTool:
    """获取智能体的通信工具"""
    return CommunicationTool(agent_name, global_communication_hub)


def generate_communication_summary() -> Dict[str, Any]:
    """生成全局通信摘要"""
    return global_communication_hub.generate_communication_report()


# 使用示例
if __name__ == "__main__":
    # 创建智能体通信工具
    tool1 = get_communication_tool("市场研究员")
    tool2 = get_communication_tool("财务分析师")

    # 发送消息
    result1 = tool1._run("send_message",
                         receiver="财务分析师",
                         message_type="information_request",
                         subject="请求财务数据",
                         content={"required_data": ["营收", "利润"], "deadline": "2024-01-15"})
    print(result1)

    # 委托任务
    result2 = tool1._run("delegate_task",
                         delegatee="财务分析师",
                         original_task="市场趋势分析",
                         delegated_task="财务指标验证",
                         reason="需要专业知识验证财务假设")
    print(result2)

    # 检查消息
    result3 = tool2._run("check_messages")
    print(result3)

    # 生成报告
    report = generate_communication_summary()
    print("\n通信报告:")
    print(json.dumps(report, indent=2, ensure_ascii=False))