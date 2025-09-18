"""
协作系统演示脚本
展示智能体间的通信、任务分配和集体决策功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.communication_tools import (
    global_communication_hub, MessageType, MessagePriority,
    get_communication_tool, generate_communication_summary
)
from src.tasks.dynamic_task_allocation import (
    get_task_allocator, get_decision_maker, AgentCapability, TaskComplexity,
    DecisionType, AgentProfile, DynamicTask
)
from src.tools.collaboration_tools import (
    get_task_orchestration_tool, get_collective_decision_tool,
    CollaborationOptimizer, create_collaborative_analysis_task,
    create_investment_decision_committee
)
from datetime import datetime
import json
import time


def demo_basic_communication():
    """演示基本通信功能"""
    print("=" * 60)
    print("演示1: 基本智能体通信")
    print("=" * 60)

    # 创建智能体通信工具
    market_tool = get_communication_tool("市场研究员")
    financial_tool = get_communication_tool("财务分析师")
    technical_tool = get_communication_tool("技术分析师")

    # 发送消息
    print("1. 市场研究员向财务分析师发送数据请求...")
    result1 = market_tool._run(
        "send_message",
        receiver="财务分析师",
        message_type="information_request",
        subject="请求苹果公司财务数据",
        content={
            "required_data": ["营收", "利润", "毛利率"],
            "time_period": "最近3年",
            "deadline": "2024-01-15"
        },
        priority="high"
    )
    print(f"   结果: {result1}")

    # 委托任务
    print("\n2. 市场研究员向技术分析师委托分析任务...")
    result2 = market_tool._run(
        "delegate_task",
        delegatee="技术分析师",
        original_task="苹果公司市场分析",
        delegated_task="技术指标验证",
        reason="需要技术分析验证市场趋势",
        deadline="2024-01-20"
    )
    print(f"   结果: {result2}")

    # 检查消息
    print("\n3. 财务分析师检查新消息...")
    result3 = financial_tool._run("check_messages")
    print(f"   结果: {result3}")

    # 响应消息
    print("\n4. 财务分析师响应数据请求...")
    response_content = {
        "financial_data": "已获取苹果公司最近3年财务数据",
        "revenue_growth": "年复合增长率8.5%",
        "profit_margin": "平均毛利率42%",
        "data_quality": "优秀"
    }
    result4 = financial_tool._run(
        "respond_to_message",
        message_id="msg_001",  # 简化演示，实际应从消息列表获取
        response_content=response_content,
        response_type="accept"
    )
    print(f"   结果: {result4}")

    # 生成通信报告
    print("\n5. 生成通信报告...")
    report = generate_communication_summary()
    print(f"   总消息数: {report['total_messages']}")
    print(f"   总委托数: {report['total_delegations']}")
    print(f"   通信效率: {report['communication_efficiency']:.2f}")


def demo_task_allocation():
    """演示动态任务分配"""
    print("\n" + "=" * 60)
    print("演示2: 动态任务分配")
    print("=" * 60)

    # 获取任务分配器
    allocator = get_task_allocator()

    # 注册智能体
    print("1. 注册分析智能体...")
    allocator.register_agent(
        "基本面专家",
        [AgentCapability.FUNDAMENTAL_ANALYSIS, AgentCapability.INDUSTRY_ANALYSIS],
        {AgentCapability.FUNDAMENTAL_ANALYSIS: 0.95, AgentCapability.INDUSTRY_ANALYSIS: 0.85},
        max_workload=100.0
    )

    allocator.register_agent(
        "技术专家",
        [AgentCapability.TECHNICAL_ANALYSIS, AgentCapability.QUANTITATIVE_ANALYSIS],
        {AgentCapability.TECHNICAL_ANALYSIS: 0.90, AgentCapability.QUANTITATIVE_ANALYSIS: 0.80},
        max_workload=80.0
    )

    allocator.register_agent(
        "风险评估师",
        [AgentCapability.RISK_ASSESSMENT, AgentCapability.VALIDATION],
        {AgentCapability.RISK_ASSESSMENT: 0.95, AgentCapability.VALIDATION: 0.75},
        max_workload=60.0
    )

    print("   已注册3个智能体")

    # 创建任务
    print("\n2. 创建分析任务...")
    tasks = [
        ("苹果公司基本面深度分析", "对苹果公司进行全面的基本面分析，包括商业模式、竞争优势等",
         [AgentCapability.FUNDAMENTAL_ANALYSIS], TaskComplexity.HIGH, 9),
        ("技术指标计算分析", "计算并分析主要技术指标，识别趋势信号",
         [AgentCapability.TECHNICAL_ANALYSIS], TaskComplexity.MEDIUM, 7),
        ("风险评估报告", "识别和评估苹果公司的各类投资风险",
         [AgentCapability.RISK_ASSESSMENT], TaskComplexity.HIGH, 8),
        ("行业对比分析", "将苹果公司与同行业公司进行对比分析",
         [AgentCapability.INDUSTRY_ANALYSIS], TaskComplexity.MEDIUM, 6),
        ("量化模型验证", "使用统计方法验证分析结果的可靠性",
         [AgentCapability.QUANTITATIVE_ANALYSIS], TaskComplexity.HIGH, 8)
    ]

    task_ids = []
    for name, desc, caps, complexity, priority in tasks:
        task_id = allocator.create_task(
            name=name,
            description=desc,
            required_capabilities=caps,
            complexity=complexity,
            priority=priority
        )
        task_ids.append(task_id)
        print(f"   已创建任务: {name} (ID: {task_id})")

    # 分配任务
    print(f"\n3. 开始任务分配...")
    allocated_tasks = allocator.allocate_tasks()

    print(f"   成功分配 {len(allocated_tasks)} 个任务")
    for task_id in allocated_tasks:
        task = None
        # 查找任务详情
        for t in allocator.active_tasks.values():
            if t.id == task_id:
                task = t
                break
        if task:
            print(f"   - {task.name} -> {task.assigned_agent}")

    # 显示工作负载
    print("\n4. 智能体工作负载:")
    for agent_name in allocator.agent_profiles:
        workload = allocator.get_agent_workload(agent_name)
        print(f"   {agent_name}: {workload['workload_percentage']:.1f}% 负载, "
              f"{workload['active_tasks']} 个活跃任务")

    # 模拟完成任务
    print("\n5. 模拟任务完成...")
    for i, task_id in enumerate(allocated_tasks[:2]):  # 完成前2个任务
        time.sleep(0.5)  # 模拟处理时间
        allocator.complete_task(
            task_id=task_id,
            result={
                "status": "completed",
                "quality_score": 0.85 + i * 0.05,
                "completion_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            success=True
        )
        print(f"   任务 {task_id} 已完成")

    # 统计信息
    print("\n6. 任务分配统计:")
    stats = allocator.get_allocation_statistics()
    print(f"   总任务数: {stats['total_tasks']}")
    print(f"   已完成: {stats['completed_tasks']}")
    print(f"   进行中: {stats['active_tasks']}")
    print(f"   待分配: {stats['pending_tasks']}")


def demo_collective_decision():
    """演示集体决策"""
    print("\n" + "=" * 60)
    print("演示3: 集体投资决策")
    print("=" * 60)

    # 获取决策制定器
    decision_maker = get_decision_maker()

    # 创建投资决策委员会
    print("1. 组建投资决策委员会...")
    voters = [
        "投资委员会主席",
        "风险管理总监",
        "首席投资经理",
        "研究部主管",
        "合规官"
    ]

    # 设置决策权重
    weights = {
        "投资委员会主席": 3.0,
        "风险管理总监": 2.5,
        "首席投资经理": 2.0,
        "研究部主管": 1.5,
        "合规官": 1.0
    }

    vote_id = decision_maker.create_vote(
        topic="苹果公司(AAPL)投资决策",
        options=["强烈买入", "买入", "持有", "卖出", "强烈卖出"],
        voters=voters,
        decision_type=DecisionType.WEIGHTED,
        weights=weights
    )

    print(f"   决策投票已创建 (ID: {vote_id})")
    print(f"   参与者: {', '.join(voters)}")

    # 模拟投票过程
    print("\n2. 开始投票过程...")
    votes = [
        ("投资委员会主席", "买入", "基于强劲的基本面和市场地位"),
        ("风险管理总监", "持有", "考虑到估值偏高和市场波动风险"),
        ("首席投资经理", "买入", "长期增长潜力依然看好"),
        ("研究部主管", "强烈买入", "新产品线将带来显著增长"),
        ("合规官", "持有", "需要进一步评估监管风险")
    ]

    for voter, option, reason in votes:
        time.sleep(0.8)  # 模拟思考时间
        print(f"   {voter} 投票: {option}")
        decision_maker.cast_vote(vote_id, voter, option)

    print("\n3. 投票完成，计算结果...")
    time.sleep(1)

    # 获取投票结果
    vote_status = decision_maker.get_vote_status(vote_id)

    print(f"   最终决策: {vote_status['result']}")
    print(f"   置信度: {vote_status['confidence']:.2f}")

    # 显示投票详情
    print("\n4. 投票详情统计:")
    from collections import Counter
    final_vote = None
    for vote in decision_maker.vote_history:
        if vote.vote_id == vote_id:
            final_vote = vote
            break

    if final_vote:
        vote_counts = Counter(final_vote.votes.values())
        for option, count in vote_counts.items():
            percentage = (count / len(final_vote.votes)) * 100
            print(f"   {option}: {count} 票 ({percentage:.1f}%)")

    # 决策统计
    print("\n5. 决策系统统计:")
    stats = decision_maker.get_decision_statistics()
    print(f"   总投票数: {stats['total_votes']}")
    print(f"   平均置信度: {stats['average_confidence']:.2f}")


def demo_collaboration_optimization():
    """演示协作优化"""
    print("\n" + "=" * 60)
    print("演示4: 协作效率优化")
    print("=" * 60)

    # 获取协作优化器
    optimizer = CollaborationOptimizer()

    # 获取工具
    orchestration_tool = get_task_orchestration_tool("协调员")
    decision_tool = get_collective_decision_tool("决策委员会")

    print("1. 分析当前协作状态...")
    analysis = optimizer.analyze_collaboration_patterns()

    print(f"   协作效率分数: {analysis['collaboration_efficiency']:.2f}")
    print(f"   发现瓶颈: {len(analysis['bottlenecks'])} 个")

    if analysis['bottlenecks']:
        print("   瓶颈详情:")
        for bottleneck in analysis['bottlenecks']:
            print(f"     - {bottleneck}")

    print(f"   优化建议: {len(analysis['recommendations'])} 条")
    for rec in analysis['recommendations'][:3]:  # 显示前3条建议
        print(f"     - {rec}")

    # 运行工作流程优化
    print("\n2. 执行工作流程优化...")
    optimization = optimizer.optimize_workflow()

    print(f"   优化操作: {len(optimization['optimization_actions'])} 项")
    if optimization['optimization_actions']:
        print("   优化措施:")
        for action in optimization['optimization_actions']:
            print(f"     - {action}")
    else:
        print("   暂无优化操作建议")

    # 使用任务编排工具
    print("\n3. 使用任务编排工具...")
    result = orchestration_tool._run(
        "create_task",
        name="协作优化任务",
        description="测试协作优化后的任务分配",
        capabilities=["fundamental_analysis"],
        complexity="medium",
        priority=7
    )
    print(f"   {result}")

    # 分配任务
    result = orchestration_tool._run("allocate_tasks")
    print(f"   {result}")

    # 分析优化效果
    print("\n4. 优化后效果分析...")
    new_analysis = optimizer.analyze_collaboration_patterns()

    efficiency_improvement = new_analysis['collaboration_efficiency'] - analysis['collaboration_efficiency']
    print(f"   效率提升: {efficiency_improvement:+.3f}")


def demo_complex_collaboration():
    """演示复杂协作场景"""
    print("\n" + "=" * 60)
    print("演示5: 复杂协作场景 - 苹果公司投资分析")
    print("=" * 60)

    print("1. 启动多智能体协作分析...")
    # 创建协作分析任务
    task_ids = create_collaborative_analysis_task(
        company="苹果公司",
        ticker="AAPL",
        analysis_types=["fundamental", "technical", "risk", "quantitative", "industry"]
    )

    print(f"   已创建 {len(task_ids)} 个协作分析任务")

    # 创建投资决策委员会
    print("\n2. 组建高级投资决策委员会...")
    committee_id = create_investment_decision_committee("苹果公司", "AAPL")
    print(f"   委员会已组建 (ID: {committee_id})")

    # 获取工具进行协调
    coordinator = get_task_orchestration_tool("项目协调员")

    print("\n3. 项目协调和监控...")
    # 检查工作负载
    workload_result = coordinator._run("get_workload")
    print(f"   {workload_result}")

    # 分析协作状态
    analysis_result = coordinator._run("analyze_collaboration")
    print(f"   {analysis_result}")

    # 模拟决策过程
    print("\n4. 高级决策过程...")
    committee_tool = get_collective_decision_tool("投资委员会")

    # 创建策略投票
    strategy_vote_id = committee_tool._run(
        "create_strategy_vote",
        strategy_name="苹果公司长期投资策略",
        options=["激进增长策略", "稳健增值策略", "收入策略", "价值投资策略"]
    )
    print(f"   {strategy_vote_id}")

    # 获取最终统计
    print("\n5. 最终协作统计...")
    comm_summary = generate_communication_summary()
    allocator = get_task_allocator()
    task_stats = allocator.get_allocation_statistics()
    decision_maker = get_decision_maker()
    decision_stats = decision_maker.get_decision_statistics()

    print(f"   通信活动:")
    print(f"     - 总消息: {comm_summary['total_messages']}")
    print(f"     - 任务委托: {comm_summary['total_delegations']}")
    print(f"     - 协作项目: {comm_summary['active_collaborations']}")

    print(f"   任务执行:")
    print(f"     - 总任务: {task_stats['total_tasks']}")
    print(f"     - 完成率: {task_stats['completed_tasks'] / max(1, task_stats['total_tasks']) * 100:.1f}%")

    print(f"   决策质量:")
    print(f"     - 决策次数: {decision_stats['total_votes']}")
    print(f"     - 平均置信度: {decision_stats['average_confidence']:.2f}")

    print("\n   协作系统演示完成!")


def main():
    """主演示函数"""
    print("CrewAI 协作系统演示")
    print("展示智能体间的通信、任务分配和集体决策功能")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # 演示各个功能模块
        demo_basic_communication()
        demo_task_allocation()
        demo_collective_decision()
        demo_collaboration_optimization()
        demo_complex_collaboration()

        print("\n" + "=" * 60)
        print("所有演示完成!")
        print("=" * 60)
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n本演示展示了:")
        print("✓ 智能体间消息传递和通信")
        print("✓ 任务委托和工作分配")
        print("✓ 动态任务负载均衡")
        print("✓ 集体决策和投票机制")
        print("✓ 协作效率优化分析")
        print("✓ 多智能体协作工作流程")

    except Exception as e:
        print(f"\n演示过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()