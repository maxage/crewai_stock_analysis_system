"""
协作功能测试用例
验证智能体间的通信、任务分配和集体决策功能
"""
import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.communication_tools import (
    global_communication_hub, MessageType, MessagePriority, Message,
    get_communication_tool, generate_communication_summary
)
from src.tasks.dynamic_task_allocation import (
    get_task_allocator, get_decision_maker, AgentCapability, TaskComplexity,
    DecisionType, create_analysis_task, create_investment_decision_vote
)
from src.tools.collaboration_tools import (
    get_task_orchestration_tool, get_collective_decision_tool,
    create_collaborative_analysis_task, create_investment_decision_committee
)
from datetime import datetime
import json


class TestCommunicationTools(unittest.TestCase):
    """测试通信工具"""

    def setUp(self):
        """测试前准备"""
        self.hub = global_communication_hub
        self.tool1 = get_communication_tool("市场研究员")
        self.tool2 = get_communication_tool("财务分析师")

    def test_send_message(self):
        """测试发送消息"""
        message_id = self.hub.send_message(
            sender="市场研究员",
            receiver="财务分析师",
            message_type=MessageType.INFORMATION_REQUEST,
            subject="请求财务数据",
            content={"required_data": ["营收", "利润"], "deadline": "2024-01-15"},
            priority=MessagePriority.HIGH
        )

        self.assertIsNotNone(message_id)
        self.assertEqual(len(self.hub.message_queue), 1)
        self.assertEqual(len(self.hub.communication_history), 1)

    def test_task_delegation(self):
        """测试任务委托"""
        delegation_id = self.hub.delegate_task(
            delegator="市场研究员",
            delegatee="财务分析师",
            original_task="市场趋势分析",
            delegated_task="财务指标验证",
            reason="需要专业知识验证财务假设",
            deadline="2024-01-20"
        )

        self.assertIsNotNone(delegation_id)
        self.assertEqual(len(self.hub.delegation_records), 1)
        self.assertEqual(len(self.hub.message_queue), 1)

    def test_get_messages_for_agent(self):
        """测试获取智能体消息"""
        # 发送测试消息
        self.hub.send_message(
            sender="市场研究员",
            receiver="财务分析师",
            message_type=MessageType.INFORMATION_REQUEST,
            subject="测试消息",
            content={"test": True}
        )

        messages = self.hub.get_messages_for_agent("财务分析师")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].subject, "测试消息")

    def test_respond_to_message(self):
        """测试响应消息"""
        # 发送原始消息
        message_id = self.hub.send_message(
            sender="市场研究员",
            receiver="财务分析师",
            message_type=MessageType.INFORMATION_REQUEST,
            subject="请求信息",
            content={"query": "测试"},
            requires_response=True
        )

        # 响应消息
        response_id = self.hub.respond_to_message(
            message_id=message_id,
            response_content={"answer": "测试答案"},
            response_type="accept"
        )

        self.assertIsNotNone(response_id)
        self.assertEqual(len(self.hub.message_queue), 2)

    def test_collaboration_management(self):
        """测试协作管理"""
        collaboration_id = self.hub.start_collaboration(
            initiator="市场研究员",
            participants=["财务分析师", "技术分析师"],
            collaboration_topic="跨部门分析项目"
        )

        self.assertIsNotNone(collaboration_id)
        self.assertIn(collaboration_id, self.hub.active_collaborations)
        self.assertEqual(len(self.hub.active_collaborations[collaboration_id]), 3)

    def test_communication_report(self):
        """测试通信报告生成"""
        # 发送一些消息
        self.hub.send_message(
            sender="市场研究员",
            receiver="财务分析师",
            message_type=MessageType.INFORMATION_REQUEST,
            subject="报告测试"
        )

        self.hub.delegate_task(
            delegator="市场研究员",
            delegatee="技术分析师",
            original_task="测试任务",
            delegated_task="子任务"
        )

        report = generate_communication_summary()
        self.assertIn('total_messages', report)
        self.assertIn('total_delegations', report)
        self.assertIn('active_collaborations', report)
        self.assertGreater(report['total_messages'], 0)


class TestDynamicTaskAllocation(unittest.TestCase):
    """测试动态任务分配"""

    def setUp(self):
        """测试前准备"""
        self.allocator = get_task_allocator()
        self.decision_maker = get_decision_maker()

        # 注册测试智能体
        self.allocator.register_agent(
            "fundamental_analyst",
            [AgentCapability.FUNDAMENTAL_ANALYSIS, AgentCapability.INDUSTRY_ANALYSIS],
            {AgentCapability.FUNDAMENTAL_ANALYSIS: 0.9, AgentCapability.INDUSTRY_ANALYSIS: 0.8}
        )

        self.allocator.register_agent(
            "technical_analyst",
            [AgentCapability.TECHNICAL_ANALYSIS, AgentCapability.QUANTITATIVE_ANALYSIS],
            {AgentCapability.TECHNICAL_ANALYSIS: 0.9, AgentCapability.QUANTITATIVE_ANALYSIS: 0.7}
        )

    def test_agent_registration(self):
        """测试智能体注册"""
        self.assertEqual(len(self.allocator.agent_profiles), 2)
        self.assertIn("fundamental_analyst", self.allocator.agent_profiles)
        self.assertIn("technical_analyst", self.allocator.agent_profiles)

    def test_task_creation(self):
        """测试任务创建"""
        task_id = self.allocator.create_task(
            name="苹果公司基本面分析",
            description="对苹果公司进行深度基本面分析",
            required_capabilities=[AgentCapability.FUNDAMENTAL_ANALYSIS],
            complexity=TaskComplexity.HIGH,
            priority=9
        )

        self.assertIsNotNone(task_id)
        self.assertEqual(len(self.allocator.task_queue), 1)

    def test_task_allocation(self):
        """测试任务分配"""
        # 创建任务
        task_id = self.allocator.create_task(
            name="技术分析任务",
            description="技术分析测试",
            required_capabilities=[AgentCapability.TECHNICAL_ANALYSIS],
            complexity=TaskComplexity.MEDIUM,
            priority=5
        )

        # 分配任务
        allocated_tasks = self.allocator.allocate_tasks()

        self.assertEqual(len(allocated_tasks), 1)
        self.assertIn(task_id, allocated_tasks)

    def test_agent_fitness_calculation(self):
        """测试智能体适合度计算"""
        profile = self.allocator.agent_profiles["fundamental_analyst"]

        fitness = profile.calculate_fitness(
            required_capabilities=[AgentCapability.FUNDAMENTAL_ANALYSIS],
            task_complexity=TaskComplexity.HIGH
        )

        self.assertGreater(fitness, 0.0)
        self.assertLessEqual(fitness, 1.0)

    def test_task_completion(self):
        """测试任务完成"""
        # 创建并分配任务
        task_id = self.allocator.create_task(
            name="测试任务",
            description="测试任务完成流程",
            required_capabilities=[AgentCapability.FUNDAMENTAL_ANALYSIS],
            complexity=TaskComplexity.LOW
        )

        self.allocator.allocate_tasks()
        self.allocator.complete_task(
            task_id=task_id,
            result={"analysis": "测试结果"},
            success=True
        )

        # 验证任务已移到已完成列表
        self.assertIn(task_id, self.allocator.completed_tasks)
        self.assertNotIn(task_id, self.allocator.active_tasks)

    def test_workload_management(self):
        """测试工作负载管理"""
        profile = self.allocator.agent_profiles["fundamental_analyst"]
        initial_workload = profile.current_workload

        # 创建一个持续时间为60分钟的任务
        task_id = self.allocator.create_task(
            name="负载测试任务",
            description="测试工作负载管理",
            required_capabilities=[AgentCapability.FUNDAMENTAL_ANALYSIS],
            estimated_duration=60
        )

        self.allocator.allocate_tasks()
        self.allocator.complete_task(task_id, {"result": "完成"})

        # 验证工作负载已更新
        final_workload = profile.current_workload
        self.assertEqual(final_workload, initial_workload)


class TestCollectiveDecision(unittest.TestCase):
    """测试集体决策"""

    def setUp(self):
        """测试前准备"""
        self.decision_maker = get_decision_maker()

    def test_vote_creation(self):
        """测试投票创建"""
        vote_id = self.decision_maker.create_vote(
            topic="是否买入AAPL",
            options=["买入", "持有", "卖出"],
            voters=["委员会主席", "风险总监", "投资经理"],
            decision_type=DecisionType.MAJORITY
        )

        self.assertIsNotNone(vote_id)
        self.assertIn(vote_id, self.decision_maker.active_votes)

    def test_voting_process(self):
        """测试投票过程"""
        # 创建投票
        vote_id = self.decision_maker.create_vote(
            topic="测试投票",
            options=["选项A", "选项B"],
            voters=["投票者1", "投票者2", "投票者3"],
            decision_type=DecisionType.MAJORITY
        )

        # 投票
        self.decision_maker.cast_vote(vote_id, "投票者1", "选项A")
        self.decision_maker.cast_vote(vote_id, "投票者2", "选项A")
        self.decision_maker.cast_vote(vote_id, "投票者3", "选项B")

        # 验证投票已完成
        self.assertNotIn(vote_id, self.decision_maker.active_votes)
        self.assertTrue(any(v.vote_id == vote_id for v in self.decision_maker.vote_history))

    def test_weighted_voting(self):
        """测试加权投票"""
        weights = {"专家1": 3.0, "专家2": 1.0, "专家3": 1.0}

        vote_id = self.decision_maker.create_vote(
            topic="加权投票测试",
            options=["方案A", "方案B"],
            voters=["专家1", "专家2", "专家3"],
            decision_type=DecisionType.WEIGHTED,
            weights=weights
        )

        # 投票（专家1和专家2支持方案A，专家3支持方案B）
        self.decision_maker.cast_vote(vote_id, "专家1", "方案A")
        self.decision_maker.cast_vote(vote_id, "专家2", "方案A")
        self.decision_maker.cast_vote(vote_id, "专家3", "方案B")

        # 查找投票结果
        result_vote = None
        for vote in self.decision_maker.vote_history:
            if vote.vote_id == vote_id:
                result_vote = vote
                break

        self.assertIsNotNone(result_vote)
        self.assertEqual(result_vote.result, "方案A")  # 方案A应获胜（权重4:1）

    def test_unanimous_decision(self):
        """测试一致同意决策"""
        vote_id = self.decision_maker.create_vote(
            topic="一致同意测试",
            options=["同意", "不同意"],
            voters=["成员1", "成员2", "成员3"],
            decision_type=DecisionType.UNANIMOUS
        )

        # 所有人都同意
        self.decision_maker.cast_vote(vote_id, "成员1", "同意")
        self.decision_maker.cast_vote(vote_id, "成员2", "同意")
        self.decision_maker.cast_vote(vote_id, "成员3", "同意")

        # 查找投票结果
        result_vote = None
        for vote in self.decision_maker.vote_history:
            if vote.vote_id == vote_id:
                result_vote = vote
                break

        self.assertIsNotNone(result_vote)
        self.assertEqual(result_vote.result, "同意")
        self.assertEqual(result_vote.confidence, 1.0)

    def test_vote_status(self):
        """测试投票状态查询"""
        vote_id = self.decision_maker.create_vote(
            topic="状态查询测试",
            options=["选项1", "选项2"],
            voters=["测试者"]
        )

        status = self.decision_maker.get_vote_status(vote_id)
        self.assertIn('status', status)
        self.assertIn('topic', status)
        self.assertEqual(status['topic'], "状态查询测试")


class TestCollaborationTools(unittest.TestCase):
    """测试协作工具"""

    def setUp(self):
        """测试前准备"""
        self.orchestration_tool = get_task_orchestration_tool("测试智能体")
        self.decision_tool = get_collective_decision_tool("测试智能体")

    def test_task_orchestration(self):
        """测试任务编排"""
        result = self.orchestration_tool._run(
            "create_task",
            name="编排测试任务",
            description="测试任务编排功能",
            capabilities=["fundamental_analysis"],
            complexity="high",
            priority=8
        )

        self.assertIn("任务已创建", result)

    def test_collaboration_analysis(self):
        """测试协作分析"""
        result = self.orchestration_tool._run("analyze_collaboration")

        self.assertIn("协作效率分析", result)
        self.assertIn("效率分数", result)

    def test_investment_vote_creation(self):
        """测试投资决策投票创建"""
        result = self.decision_tool._run(
            "create_investment_vote",
            company="苹果公司",
            ticker="AAPL",
            options=["买入", "持有", "卖出"]
        )

        self.assertIn("投资决策投票已创建", result)

    def test_decision_statistics(self):
        """测试决策统计"""
        result = self.decision_tool._run("get_decision_stats")

        self.assertIn("决策统计", result)
        self.assertIn("总投票数", result)


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def setUp(self):
        """测试前准备"""
        # 清理全局状态
        from src.tools.communication_tools import global_communication_hub
        global_communication_hub.message_queue.clear()
        global_communication_hub.communication_history.clear()
        global_communication_hub.delegation_records.clear()

    def test_end_to_end_collaboration(self):
        """测试端到端协作流程"""
        # 1. 创建协作任务
        task_ids = create_collaborative_analysis_task(
            company="苹果公司",
            ticker="AAPL",
            analysis_types=["fundamental", "technical", "risk"]
        )

        self.assertEqual(len(task_ids), 3)

        # 2. 创建投资决策委员会
        committee_id = create_investment_decision_committee("苹果公司", "AAPL")
        self.assertIsNotNone(committee_id)

        # 3. 验证通信记录
        comm_summary = generate_communication_summary()
        self.assertGreater(comm_summary['total_messages'], 0)

    def test_complex_workflow(self):
        """测试复杂工作流程"""
        # 1. 获取工具
        allocator = get_task_allocator()
        decision_maker = get_decision_maker()

        # 2. 注册智能体
        allocator.register_agent(
            "multi_role_agent",
            [AgentCapability.FUNDAMENTAL_ANALYSIS, AgentCapability.TECHNICAL_ANALYSIS,
             AgentCapability.RISK_ASSESSMENT, AgentCapability.DECISION_MAKING],
            {cap: 0.8 for cap in [AgentCapability.FUNDAMENTAL_ANALYSIS, AgentCapability.TECHNICAL_ANALYSIS,
                                 AgentCapability.RISK_ASSESSMENT, AgentCapability.DECISION_MAKING]}
        )

        # 3. 创建多个任务
        task_ids = []
        for i in range(5):
            task_id = allocator.create_task(
                name=f"复杂任务{i}",
                description=f"测试复杂工作流程中的任务{i}",
                required_capabilities=[AgentCapability.FUNDAMENTAL_ANALYSIS],
                complexity=TaskComplexity.MEDIUM,
                priority=5 + i
            )
            task_ids.append(task_id)

        # 4. 分配任务
        allocated = allocator.allocate_tasks()
        self.assertEqual(len(allocated), 5)

        # 5. 完成部分任务
        for task_id in task_ids[:3]:
            allocator.complete_task(task_id, {"status": "completed"}, success=True)

        # 6. 创建关于项目进展的投票
        vote_id = decision_maker.create_vote(
            topic="项目进展评估",
            options=["优秀", "良好", "一般", "需要改进"],
            voters=["项目经理", "技术负责人", "质量保证"],
            decision_type=DecisionType.WEIGHTED,
            weights={"项目经理": 2.0, "技术负责人": 2.0, "质量保证": 1.0}
        )

        # 7. 进行投票
        decision_maker.cast_vote(vote_id, "项目经理", "良好")
        decision_maker.cast_vote(vote_id, "技术负责人", "优秀")
        decision_maker.cast_vote(vote_id, "质量保证", "良好")

        # 8. 验证结果
        stats = allocator.get_allocation_statistics()
        self.assertGreaterEqual(stats['completed_tasks'], 3)

        decision_stats = decision_maker.get_decision_statistics()
        self.assertGreaterEqual(decision_stats['completed_votes'], 1)


def run_collaboration_tests():
    """运行所有协作功能测试"""
    print("=" * 60)
    print("开始协作功能测试")
    print("=" * 60)

    # 创建测试套件
    test_suite = unittest.TestSuite()

    # 添加测试类
    test_classes = [
        TestCommunicationTools,
        TestDynamicTaskAllocation,
        TestCollectiveDecision,
        TestCollaborationTools,
        TestIntegration
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # 输出结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要")
    print("=" * 60)
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")

    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")

    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun
    print(f"\n成功率: {success_rate:.2%}")

    return result.wasSuccessful()


if __name__ == "__main__":
    run_collaboration_tests()