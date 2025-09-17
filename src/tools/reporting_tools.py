"""
报告生成工具
用于生成各种分析报告和文档
"""
from crewai_tools import BaseTool
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ReportWritingTool(BaseTool):
    """报告编写工具"""

    name: str = "Report Writing Tool"
    description: str = "生成标准化的投资分析报告和文档"

    def _run(self, report_data: str, report_type: str = "investment_analysis") -> str:
        """
        生成报告

        Args:
            report_data: 报告数据（JSON格式）
            report_type: 报告类型 (investment_analysis, summary, executive_brief, detailed)

        Returns:
            报告内容
        """
        try:
            data = json.loads(report_data)
            logger.info(f"生成报告，类型: {report_type}")

            if report_type == "investment_analysis":
                report = self._generate_investment_analysis_report(data)
            elif report_type == "summary":
                report = self._generate_summary_report(data)
            elif report_type == "executive_brief":
                report = self._generate_executive_brief(data)
            elif report_type == "detailed":
                report = self._generate_detailed_report(data)
            else:
                report = self._generate_generic_report(data)

            logger.info("报告生成完成")
            return report

        except Exception as e:
            error_msg = f"生成报告失败: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def _generate_investment_analysis_report(self, data: Dict) -> str:
        """生成投资分析报告"""
        company = data.get('company', '未知公司')
        ticker = data.get('ticker', 'UNKNOWN')

        report = f"""
# {company} ({ticker}) 投资分析报告

**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**分析师**: AI投资分析系统
**报告类型**: 综合投资分析

---

## 执行摘要

本报告对{company} ({ticker})进行了全面的投资分析，涵盖市场研究、财务分析、技术分析、基本面评估、风险分析等多个维度。通过多维度综合分析，为投资者提供专业的投资建议。

## 公司概况

### 基本信息
- **公司名称**: {company}
- **股票代码**: {ticker}
- **行业**: {data.get('industry', '未知')}
- **市值**: {data.get('market_cap', 'N/A')}
- **当前股价**: ${data.get('current_price', 'N/A')}

### 业务描述
{data.get('business_description', '暂无业务描述')}

---

## 市场分析

### 市场表现
{data.get('market_analysis', '暂无市场分析数据')}

### 行业地位
{data.get('industry_position', '暂无行业地位分析')}

### 竞争优势
{data.get('competitive_advantages', '暂无竞争优势分析')}

---

## 财务分析

### 财务指标
{data.get('financial_metrics', '暂无财务指标数据')}

### 盈利能力
{data.get('profitability_analysis', '暂无盈利能力分析')}

### 财务健康度
{data.get('financial_health', '暂无财务健康度分析')}

---

## 技术分析

### 价格走势
{data.get('price_trend', '暂无价格走势分析')}

### 技术指标
{data.get('technical_indicators', '暂无技术指标分析')}

### 交易信号
{data.get('trading_signals', '暂无交易信号分析')}

---

## 基本面分析

### 估值分析
{data.get('valuation_analysis', '暂无估值分析')}

### 成长性分析
{data.get('growth_analysis', '暂无成长性分析')}

### 质量评估
{data.get('quality_assessment', '暂无质量评估')}

---

## 风险评估

### 主要风险
{data.get('major_risks', '暂无主要风险分析')}

### 风险等级
- **整体风险等级**: {data.get('risk_level', '未知')}
- **市场风险**: {data.get('market_risk', '未知')}
- **财务风险**: {data.get('financial_risk', '未知')}
- **运营风险**: {data.get('operational_risk', '未知')}

### 风险控制建议
{data.get('risk_control_recommendations', '暂无风险控制建议')}

---

## 投资建议

### 投资评级
- **当前评级**: {data.get('investment_rating', '未评级')}
- **目标价位**: ${data.get('target_price', 'N/A')}
- **止损价位**: ${data.get('stop_loss', 'N/A')}

### 投资策略
{data.get('investment_strategy', '暂无投资策略建议')}

### 时间框架
- **短期建议**: {data.get('short_term_outlook', '观望')}
- **中期建议**: {data.get('medium_term_outlook', '观望')}
- **长期建议**: {data.get('long_term_outlook', '观望')}

---

## 关键假设

{data.get('key_assumptions', '暂无关键假设说明')}

---

## 免责声明

本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。

- 本报告基于公开信息编制，可能存在信息滞后或不准确的情况
- 市场存在不确定性，过去表现不代表未来结果
- 投资者应根据自身风险承受能力和投资目标做出独立决策
- 建议投资者在进行投资决策前咨询专业投资顾问

---

**报告由 AI 投资分析系统自动生成**
"""
        return report

    def _generate_summary_report(self, data: Dict) -> str:
        """生成摘要报告"""
        company = data.get('company', '未知公司')
        ticker = data.get('ticker', 'UNKNOWN')

        report = f"""
# {company} ({ticker}) 分析摘要

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 关键信息
- **投资评级**: {data.get('investment_rating', '未评级')}
- **目标价位**: ${data.get('target_price', 'N/A')}
- **风险等级**: {data.get('risk_level', '未知')}
- **综合评分**: {data.get('overall_score', 'N/A')}/100

## 核心观点
{data.get('core_viewpoints', '暂无核心观点')}

## 主要亮点
{data.get('key_highlights', '暂无主要亮点')}

## 主要风险
{data.get('key_risks', '暂无主要风险')}

## 投资建议
{data.get('investment_recommendation', '暂无投资建议')}
"""
        return report

    def _generate_executive_brief(self, data: Dict) -> str:
        """生成执行简报"""
        company = data.get('company', '未知公司')
        ticker = data.get('ticker', 'UNKNOWN')

        report = f"""
# {company} ({ticker}) 执行简报

**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 即时概览
- **当前状态**: {data.get('current_status', '正常')}
- **投资评级**: {data.get('investment_rating', '未评级')}
- **市场情绪**: {data.get('market_sentiment', '中性')}

## 关键指标
{data.get('key_metrics', '暂无关键指标')}

## 重要提醒
{data.get('important_reminders', '暂无重要提醒')}

## 行动建议
{data.get('action_items', '暂无行动建议')}
"""
        return report

    def _generate_detailed_report(self, data: Dict) -> str:
        """生成详细报告"""
        return self._generate_investment_analysis_report(data)

    def _generate_generic_report(self, data: Dict) -> str:
        """生成通用报告"""
        report = f"""
# 分析报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 报告内容
{json.dumps(data, ensure_ascii=False, indent=2)}
"""
        return report


class DataExportTool(BaseTool):
    """数据导出工具"""

    name: str = "Data Export Tool"
    description: str = "将分析数据导出为各种格式"

    def _run(self, export_data: str, export_format: str = "json", filename: str = "") -> str:
        """
        导出数据

        Args:
            export_data: 要导出的数据
            export_format: 导出格式 (json, csv, excel, txt)
            filename: 文件名

        Returns:
            导出文件路径
        """
        try:
            import os
            import json
            import pandas as pd

            data = json.loads(export_data)
            logger.info(f"导出数据，格式: {export_format}")

            # 确保导出目录存在
            os.makedirs('data/exports', exist_ok=True)

            # 生成文件名
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"export_data_{timestamp}.{export_format}"

            filepath = os.path.join('data/exports', filename)

            # 根据格式导出
            if export_format == "json":
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

            elif export_format == "csv":
                df = pd.DataFrame([data])
                df.to_csv(filepath, index=False, encoding='utf-8')

            elif export_format == "excel":
                df = pd.DataFrame([data])
                df.to_excel(filepath, index=False)

            elif export_format == "txt":
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(str(data))

            else:
                raise ValueError(f"不支持的导出格式: {export_format}")

            logger.info(f"数据导出完成: {filepath}")
            return filepath

        except Exception as e:
            error_msg = f"数据导出失败: {str(e)}"
            logger.error(error_msg)
            return error_msg


class ReportTemplateTool(BaseTool):
    """报告模板工具"""

    name: str = "Report Template Tool"
    description: str = "使用预定义模板生成标准化报告"

    def _run(self, template_data: str, template_name: str = "standard") -> str:
        """
        使用模板生成报告

        Args:
            template_data: 模板数据
            template_name: 模板名称

        Returns:
            模板化报告内容
        """
        try:
            data = json.loads(template_data)
            logger.info(f"使用模板生成报告: {template_name}")

            templates = {
                "standard": self._standard_template,
                "professional": self._professional_template,
                "executive": self._executive_template,
                "research": self._research_template
            }

            if template_name not in templates:
                raise ValueError(f"未知模板: {template_name}")

            report = templates[template_name](data)
            logger.info("模板报告生成完成")
            return report

        except Exception as e:
            error_msg = f"模板报告生成失败: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def _standard_template(self, data: Dict) -> str:
        """标准模板"""
        return f"""
{data.get('company', '')} ({data.get('ticker', '')}) 投资分析报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== 摘要 ===
{data.get('summary', '')}

=== 详细分析 ===
{data.get('detailed_analysis', '')}

=== 投资建议 ===
{data.get('recommendation', '')}

=== 风险提示 ===
{data.get('risk_warning', '')}

=== 免责声明 ===
本报告仅供参考，不构成投资建议。
"""

    def _professional_template(self, data: Dict) -> str:
        """专业模板"""
        return f"""
PROFESSIONAL INVESTMENT ANALYSIS REPORT
======================================

Company: {data.get('company', '')}
Ticker: {data.get('ticker', '')}
Date: {datetime.now().strftime('%Y-%m-%d')}

EXECUTIVE SUMMARY
-----------------
{data.get('executive_summary', '')}

COMPANY OVERVIEW
----------------
{data.get('company_overview', '')}

FINANCIAL ANALYSIS
------------------
{data.get('financial_analysis', '')}

MARKET ANALYSIS
----------------
{data.get('market_analysis', '')}

INVESTMENT RECOMMENDATION
--------------------------
{data.get('investment_recommendation', '')}

RISK FACTORS
-------------
{data.get('risk_factors', '')}

DISCLAIMER
----------
This report is for informational purposes only.
"""

    def _executive_template(self, data: Dict) -> str:
        """执行模板"""
        return f"""
EXECUTIVE BRIEFING
=================

Subject: {data.get('company', '')} Investment Analysis
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

KEY TAKEAWAYS
--------------
• {data.get('key_takeaway_1', '')}
• {data.get('key_takeaway_2', '')}
• {data.get('key_takeaway_3', '')}

INVESTMENT THESIS
------------------
{data.get('investment_thesis', '')}

RECOMMENDATION
--------------
{data.get('recommendation', '')}

NEXT STEPS
-----------
{data.get('next_steps', '')}
"""

    def _research_template(self, data: Dict) -> str:
        """研究模板"""
        return f"""
RESEARCH REPORT: {data.get('company', '')} ({data.get('ticker', '')})
===================================================

Publication Date: {datetime.now().strftime('%Y-%m-%d')}
Research Analyst: AI Investment System

ABSTRACT
--------
{data.get('abstract', '')}

1. INTRODUCTION
--------------
{data.get('introduction', '')}

2. METHODOLOGY
--------------
{data.get('methodology', '')}

3. ANALYSIS
----------
{data.get('analysis', '')}

4. FINDINGS
----------
{data.get('findings', '')}

5. CONCLUSIONS
-------------
{data.get('conclusions', '')}

6. REFERENCES
------------
{data.get('references', '')}

DISCLAIMER: This research report is for informational purposes only.
"""


# 使用示例
if __name__ == "__main__":
    # 测试报告编写工具
    report_tool = ReportWritingTool()
    test_data = {
        "company": "苹果公司",
        "ticker": "AAPL",
        "industry": "科技",
        "current_price": "150.00",
        "investment_rating": "买入",
        "risk_level": "中等",
        "overall_score": 75.5,
        "summary": "苹果公司基本面稳健，技术面健康，建议逢低买入。"
    }

    print("=== 测试报告编写工具 ===")
    report = report_tool._run(json.dumps(test_data), "investment_analysis")
    print(report[:1000] + "...")

    # 测试数据导出工具
    export_tool = DataExportTool()
    print("\n=== 测试数据导出工具 ===")
    export_result = export_tool._run(json.dumps(test_data), "json")
    print(f"导出结果: {export_result}")

    # 测试报告模板工具
    template_tool = ReportTemplateTool()
    print("\n=== 测试报告模板工具 ===")
    template_result = template_tool._run(json.dumps(test_data), "professional")
    print(template_result)