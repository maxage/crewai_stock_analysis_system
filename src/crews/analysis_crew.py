"""
分析团队
负责基本面分析、风险分析和行业分析
"""
from crewai import Agent, Crew, Process, Task
from typing import List, Dict, Any
import logging
import yaml
import os
import json
from datetime import datetime
from src.tools.fundamental_tools import FundamentalAnalysisTool

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalysisCrew:
    """分析团队"""

    def __init__(self):
        """初始化分析团队"""
        self.agents_config = self._load_config('config/agents.yaml')
        self.tasks_config = self._load_config('config/tasks.yaml')
        self.crew = self._create_crew()

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

    def _create_crew(self) -> Crew:
        """创建Crew实例"""
        agents = [
            self._create_fundamental_analyst(),
            self._create_risk_assessment_specialist(),
            self._create_industry_expert()
        ]

        return Crew(
            agents=agents,
            tasks=[],
            process=Process.sequential,
            verbose=True
        )

    def _create_fundamental_analyst(self) -> Agent:
        """创建基本面分析师"""
        config = self.agents_config.get('fundamental_analyst', {})
        return Agent(
            role=config.get('role', '基本面分析师'),
            goal=config.get('goal', '评估公司基本面'),
            backstory=config.get('backstory', '基本面分析专家'),
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )

    def _create_risk_assessment_specialist(self) -> Agent:
        """创建风险评估专家"""
        config = self.agents_config.get('risk_assessment_specialist', {})
        return Agent(
            role=config.get('role', '风险评估专家'),
            goal=config.get('goal', '评估投资风险'),
            backstory=config.get('backstory', '风险管理专家'),
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )

    def _create_industry_expert(self) -> Agent:
        """创建行业专家"""
        config = self.agents_config.get('industry_expert', {})
        return Agent(
            role=config.get('role', '行业专家'),
            goal=config.get('goal', '分析行业地位'),
            backstory=config.get('backstory', '行业分析专家'),
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )

    def execute_analysis(self, company: str, ticker: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行分析流程"""
        logger.info(f"开始分析 {company} ({ticker})")

        try:
            # 初始化基本面分析工具
            fundamental_tool = FundamentalAnalysisTool()
            
            # 准备分析数据
            analysis_input = {
                'company': company,
                'ticker': ticker,
                'industry': '科技',  # 这里可以根据实际情况设置行业
                'pe_ratio': 28.5,    # 模拟的市盈率
                'industry_pe': 24.3, # 模拟的行业平均市盈率
                'pb_ratio': 6.2,     # 模拟的市净率
                'industry_pb': 4.8   # 模拟的行业平市净率
            }
            
            # 如果有传入数据，使用实际数据
            if data and isinstance(data, dict):
                logger.info(f"使用传入的数据进行分析")
                # 尝试从财务数据中提取关键指标
                financial_data = data.get('financial_data', '')
                if isinstance(financial_data, str) and financial_data.startswith("#"):
                    # 这是通过YFinanceTool获取的格式化报告
                    try:
                        # 提取关键数据点
                        if "市值" in financial_data:
                            market_cap = financial_data.split("市值: ")[1].split("\n")[0]
                            analysis_input['market_cap'] = market_cap
                        if "当前价格" in financial_data:
                            current_price = financial_data.split("当前价格: ")[1].split("\n")[0]
                            analysis_input['current_price'] = current_price
                    except Exception as e:
                        logger.warning(f"从财务数据中提取指标失败: {str(e)}")
            
            # 执行基本面分析
            logger.info(f"执行基本面分析")
            company_data_json = json.dumps(analysis_input)
            fundamental_analysis_result = fundamental_tool._run(company_data_json, analysis_type="comprehensive")
            
            # 构建分析结果
            analysis_result = {
                'success': True,
                'company': company,
                'ticker': ticker,
                'data': {
                    'fundamental_analysis': {
                        'analysis_text': fundamental_analysis_result if fundamental_analysis_result else f'{company}的基本面分析结果',
                        'financial_score': 75.5,
                        'growth_potential': '高'
                    },
                    'risk_assessment': {
                        'analysis_text': f'{ticker}的风险评估结果',
                        'risk_level': '中等',
                        'risk_factors': ['市场风险', '行业风险']
                    },
                    'industry_analysis': {
                        'analysis_text': f'{company}的行业地位分析',
                        'market_position': '领先',
                        'competitiveness': '强'
                    }
                },
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            logger.info(f"分析完成: {company}")
            return analysis_result

        except Exception as e:
            error_msg = f"分析失败: {company}, 错误: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'company': company,
                'ticker': ticker
            }

    def calculate_analysis_score(self, analysis_result: Dict[str, Any]) -> Dict[str, float]:
        """计算分析评分"""
        # 初始化默认分数
        fundamental_score = 75.5
        risk_score = 30.0
        industry_score = 80.0
        
        # 尝试从实际分析结果中提取分数
        if isinstance(analysis_result, dict):
            # 从基本面分析获取分数
            fundamental_analysis = analysis_result.get('fundamental_analysis', {})
            if isinstance(fundamental_analysis, dict) and 'financial_score' in fundamental_analysis:
                fundamental_score = float(fundamental_analysis['financial_score'])
            
            # 从风险评估获取分数
            risk_assessment = analysis_result.get('risk_assessment', {})
            if isinstance(risk_assessment, dict) and 'risk_level' in risk_assessment:
                # 根据风险等级映射分数
                risk_mapping = {
                    '低': 20.0,
                    '中等': 40.0,
                    '高': 60.0,
                    '未知': 50.0
                }
                risk_level = risk_assessment['risk_level']
                risk_score = risk_mapping.get(risk_level, 40.0)
            
            # 从行业分析获取分数
            industry_analysis = analysis_result.get('industry_analysis', {})
            if isinstance(industry_analysis, dict) and 'market_position' in industry_analysis:
                # 根据市场地位映射分数
                position_mapping = {
                    '领先': 85.0,
                    '较强': 75.0,
                    '一般': 60.0,
                    '较弱': 40.0,
                    '未知': 60.0
                }
                market_position = industry_analysis['market_position']
                industry_score = position_mapping.get(market_position, 60.0)
        
        # 计算综合评分（加权平均）
        # 基本面分析占40%，风险评估占30%，行业分析占30%
        overall_score = (fundamental_score * 0.4) + ((100 - risk_score) * 0.3) + (industry_score * 0.3)
        
        scores = {
            'fundamental_score': round(fundamental_score, 1),
            'risk_score': round(risk_score, 1),
            'industry_score': round(industry_score, 1),
            'overall_score': round(overall_score, 1)
        }

        return scores

    def generate_analysis_summary(self, analysis_result: Dict[str, Any]) -> str:
        """生成分析摘要"""
        scores = self.calculate_analysis_score(analysis_result)

        summary = f"""
分析摘要：
- 基本面评分: {scores['fundamental_score']:.1f}/100
- 风险评分: {scores['risk_score']:.1f}/100
- 行业评分: {scores['industry_score']:.1f}/100
- 综合评分: {scores['overall_score']:.1f}/100

投资建议：{self._get_recommendation(scores)}
"""

        return summary

    def _get_recommendation(self, scores: Dict[str, float]) -> str:
        """根据评分给出投资建议"""
        overall = scores['overall_score']

        if overall >= 80:
            return "强烈买入"
        elif overall >= 70:
            return "买入"
        elif overall >= 60:
            return "增持"
        elif overall >= 50:
            return "持有"
        elif overall >= 40:
            return "减持"
        else:
            return "卖出"


# 使用示例
if __name__ == "__main__":
    # 创建分析团队实例
    analysis_crew = AnalysisCrew()

    # 执行分析示例
    result = analysis_crew.execute_analysis("苹果公司", "AAPL")
    print("分析结果:", result)

    if result['success']:
        # 计算评分
        scores = analysis_crew.calculate_analysis_score(result['data'])
        print("分析评分:", scores)

        # 生成摘要
        summary = analysis_crew.generate_analysis_summary(result['data'])
        print("分析摘要:", summary)