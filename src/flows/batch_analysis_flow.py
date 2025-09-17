"""
批量分析流程控制
使用Flows实现高效的批量股票分析
"""
from crewai.flow.flow import Flow, listen, start, router
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import time
import concurrent.futures

# 导入系统和团队
from src.stock_analysis_system import StockAnalysisSystem

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BatchAnalysisState(BaseModel):
    """批量分析状态模型"""
    stocks: List[Dict[str, str]] = []
    completed_stocks: List[Dict[str, Any]] = []
    failed_stocks: List[Dict[str, Any]] = []
    in_progress: List[str] = []
    current_batch: List[Dict[str, str]] = []
    batch_size: int = 3
    max_workers: int = 3
    total_stocks: int = 0
    completed_count: int = 0
    failed_count: int = 0
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    current_stage: str = "initialized"
    progress_percentage: float = 0.0
    average_analysis_time: float = 0.0
    estimated_remaining_time: Optional[float] = None
    errors: List[str] = []
    warnings: List[str] = []


class BatchAnalysisFlow(Flow[BatchAnalysisState]):
    """批量分析流程"""

    def __init__(self):
        super().__init__()
        self.stock_analysis_system = StockAnalysisSystem()
        self.state = BatchAnalysisState()

    @start()
    def initialize_batch_analysis(self):
        """初始化批量分析"""
        logger.info("=== 初始化批量分析流程 ===")
        self.state.start_time = datetime.now().isoformat()
        self.state.current_stage = "initialized"

        # 获取批量分析参数
        print("=== 批量分析配置 ===")

        # 股票列表输入方式
        input_method = input("选择输入方式 (1:手动输入 2:文件导入): ")

        if input_method == "1":
            stocks = self._get_manual_input()
        else:
            stocks = self._get_file_input()

        if not stocks:
            logger.error("没有提供股票列表")
            return {"success": False, "error": "股票列表为空"}

        self.state.stocks = stocks
        self.state.total_stocks = len(stocks)

        # 获取批量配置
        self.state.batch_size = int(input("请输入批次大小 (建议3-5): ") or "3")
        self.state.max_workers = int(input("请输入最大并发数 (建议2-4): ") or "3")

        logger.info(f"开始批量分析 {len(stocks)} 只股票")
        return {
            "stocks": stocks,
            "batch_size": self.state.batch_size,
            "max_workers": self.state.max_workers
        }

    @listen("initialize_batch_analysis")
    def validate_stock_list(self, batch_config):
        """验证股票列表"""
        logger.info("=== 验证股票列表 ===")
        self.state.current_stage = "validation"

        try:
            # 基本验证
            valid_stocks = []
            invalid_stocks = []

            for stock in batch_config['stocks']:
                if self._validate_stock_format(stock):
                    valid_stocks.append(stock)
                else:
                    invalid_stocks.append(stock)

            if invalid_stocks:
                warning_msg = f"发现 {len(invalid_stocks)} 个无效股票格式"
                self.state.warnings.append(warning_msg)
                logger.warning(warning_msg)

            logger.info(f"验证完成: {len(valid_stocks)} 个有效股票")
            return {
                "success": True,
                "valid_stocks": valid_stocks,
                "invalid_stocks": invalid_stocks
            }

        except Exception as e:
            error_msg = f"股票列表验证失败: {str(e)}"
            self.state.errors.append(error_msg)
            logger.error(error_msg)
            return {"success": False, "error": str(e)}

    @router(validate_stock_list)
    def determine_batch_strategy(self):
        """确定批次策略"""
        logger.info("=== 确定批次策略 ===")

        total_stocks = len(self.state.stocks)
        batch_size = self.state.batch_size
        max_workers = self.state.max_workers

        if total_stocks <= batch_size:
            logger.info("股票数量较少，使用单批次分析")
            return "single_batch"
        elif total_stocks <= batch_size * 3:
            logger.info("股票数量适中，使用多批次顺序分析")
            return "sequential_batches"
        else:
            logger.info("股票数量较多，使用并行批次分析")
            return "parallel_batches"

    @listen("single_batch")
    def process_single_batch(self):
        """处理单批次"""
        logger.info("=== 处理单批次 ===")
        self.state.current_stage = "single_batch_processing"

        try:
            self.state.current_batch = self.state.stocks.copy()
            results = self._process_batch(self.state.current_batch)

            self._update_batch_results(results)
            logger.info("单批次处理完成")
            return results

        except Exception as e:
            error_msg = f"单批次处理失败: {str(e)}"
            self.state.errors.append(error_msg)
            logger.error(error_msg)
            return {"success": False, "error": str(e)}

    @listen("sequential_batches")
    def process_sequential_batches(self):
        """顺序处理多批次"""
        logger.info("=== 顺序处理多批次 ===")
        self.state.current_stage = "sequential_batch_processing"

        try:
            all_results = []
            stocks = self.state.stocks.copy()
            batch_size = self.state.batch_size

            # 分批处理
            for i in range(0, len(stocks), batch_size):
                batch = stocks[i:i + batch_size]
                self.state.current_batch = batch

                logger.info(f"处理批次 {i//batch_size + 1}/{(len(stocks) + batch_size - 1)//batch_size}")
                batch_results = self._process_batch(batch)
                all_results.extend(batch_results)

                self._update_batch_results(batch_results)

                # 批次间暂停，避免API限制
                if i + batch_size < len(stocks):
                    time.sleep(2)

            logger.info("顺序批次处理完成")
            return all_results

        except Exception as e:
            error_msg = f"顺序批次处理失败: {str(e)}"
            self.state.errors.append(error_msg)
            logger.error(error_msg)
            return {"success": False, "error": str(e)}

    @listen("parallel_batches")
    def process_parallel_batches(self):
        """并行处理多批次"""
        logger.info("=== 并行处理多批次 ===")
        self.state.current_stage = "parallel_batch_processing"

        try:
            stocks = self.state.stocks.copy()
            batch_size = self.state.batch_size
            max_workers = min(self.state.max_workers, (len(stocks) + batch_size - 1) // batch_size)

            # 分批次
            batches = [stocks[i:i + batch_size] for i in range(0, len(stocks), batch_size)]

            logger.info(f"总共 {len(batches)} 个批次，最大并发 {max_workers}")

            all_results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有批次任务
                future_to_batch = {
                    executor.submit(self._process_batch_with_delay, batch, i): i
                    for i, batch in enumerate(batches)
                }

                # 等待所有批次完成
                for future in concurrent.futures.as_completed(future_to_batch):
                    batch_index = future_to_batch[future]
                    try:
                        batch_results = future.result()
                        all_results.extend(batch_results)
                        self._update_batch_results(batch_results)

                        progress = (self.state.completed_count + self.state.failed_count) / len(stocks) * 100
                        logger.info(f"批次 {batch_index + 1}/{len(batches)} 完成，总进度: {progress:.1f}%")

                    except Exception as e:
                        error_msg = f"批次 {batch_index + 1} 处理失败: {str(e)}"
                        self.state.errors.append(error_msg)
                        logger.error(error_msg)

            logger.info("并行批次处理完成")
            return all_results

        except Exception as e:
            error_msg = f"并行批次处理失败: {str(e)}"
            self.state.errors.append(error_msg)
            logger.error(error_msg)
            return {"success": False, "error": str(e)}

    @listen(["process_single_batch", "process_sequential_batches", "process_parallel_batches"])
    def generate_batch_summary(self, all_results):
        """生成批量分析摘要"""
        logger.info("=== 生成批量分析摘要 ===")
        self.state.current_stage = "summary_generation"
        self.state.end_time = datetime.now().isoformat()

        try:
            summary = self.stock_analysis_system.generate_summary_report(all_results)

            # 保存摘要报告
            summary_path = self._save_summary_report(summary)

            logger.info("批量分析摘要生成完成")
            return {
                "success": True,
                "summary": summary,
                "summary_path": summary_path,
                "total_stocks": self.state.total_stocks,
                "completed_count": self.state.completed_count,
                "failed_count": self.state.failed_count,
                "success_rate": (self.state.completed_count / self.state.total_stocks * 100) if self.state.total_stocks > 0 else 0
            }

        except Exception as e:
            error_msg = f"生成摘要失败: {str(e)}"
            self.state.errors.append(error_msg)
            logger.error(error_msg)
            return {"success": False, "error": str(e)}

    # 辅助方法
    def _get_manual_input(self):
        """获取手动输入的股票列表"""
        stocks = []
        print("请输入股票列表（格式：公司名称,股票代码），输入 'done' 结束：")

        while True:
            user_input = input("> ").strip()
            if user_input.lower() == 'done':
                break

            try:
                parts = user_input.split(',')
                if len(parts) == 2:
                    company = parts[0].strip()
                    ticker = parts[1].strip()
                    stocks.append({'company': company, 'ticker': ticker})
                    print(f"已添加: {company} ({ticker})")
                else:
                    print("格式错误，请使用：公司名称,股票代码")
            except Exception as e:
                print(f"输入错误: {e}")

        return stocks

    def _get_file_input(self):
        """从文件导入股票列表"""
        stocks = []
        filepath = input("请输入股票列表文件路径: ").strip()

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split(',')
                        if len(parts) == 2:
                            company = parts[0].strip()
                            ticker = parts[1].strip()
                            stocks.append({'company': company, 'ticker': ticker})
                        else:
                            logger.warning(f"文件第 {line_num} 行格式错误: {line}")

            logger.info(f"从文件导入 {len(stocks)} 只股票")
            return stocks

        except FileNotFoundError:
            logger.error(f"文件不存在: {filepath}")
            return []
        except Exception as e:
            logger.error(f"读取文件失败: {str(e)}")
            return []

    def _validate_stock_format(self, stock):
        """验证股票格式"""
        if not isinstance(stock, dict):
            return False
        if 'company' not in stock or 'ticker' not in stock:
            return False
        if not stock['company'] or not stock['ticker']:
            return False
        return True

    def _process_batch(self, batch):
        """处理单个批次"""
        logger.info(f"开始处理批次: {len(batch)} 只股票")
        return self.stock_analysis_system.analyze_multiple_stocks(batch)

    def _process_batch_with_delay(self, batch, batch_index):
        """带延迟的批次处理（用于并行）"""
        # 随机延迟，避免同时请求
        import random
        delay = random.uniform(0, 2)
        time.sleep(delay)

        logger.info(f"开始处理批次 {batch_index + 1}: {len(batch)} 只股票")
        return self._process_batch(batch)

    def _update_batch_results(self, results):
        """更新批次结果"""
        for result in results:
            if result.get('success', False):
                self.state.completed_stocks.append(result)
                self.state.completed_count += 1
            else:
                self.state.failed_stocks.append(result)
                self.state.failed_count += 1

        # 更新进度
        total_processed = self.state.completed_count + self.state.failed_count
        self.state.progress_percentage = (total_processed / self.state.total_stocks) * 100

        # 更新平均分析时间
        if total_processed > 0:
            elapsed_time = (datetime.now().timestamp() - datetime.fromisoformat(self.state.start_time).timestamp())
            self.state.average_analysis_time = elapsed_time / total_processed

            # 估算剩余时间
            remaining_stocks = self.state.total_stocks - total_processed
            self.state.estimated_remaining_time = remaining_stocks * self.state.average_analysis_time

    def _save_summary_report(self, summary):
        """保存摘要报告"""
        import os
        os.makedirs('reports', exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"batch_analysis_summary_{timestamp}.md"
        filepath = os.path.join('reports', filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(summary)
            logger.info(f"摘要报告已保存: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"保存摘要报告失败: {str(e)}")
            return ""

    def get_batch_status(self):
        """获取批量分析状态"""
        return {
            "total_stocks": self.state.total_stocks,
            "completed_count": self.state.completed_count,
            "failed_count": self.state.failed_count,
            "progress_percentage": self.state.progress_percentage,
            "current_stage": self.state.current_stage,
            "average_analysis_time": self.state.average_analysis_time,
            "estimated_remaining_time": self.state.estimated_remaining_time,
            "errors_count": len(self.state.errors),
            "warnings_count": len(self.state.warnings)
        }

    def get_detailed_results(self):
        """获取详细结果"""
        return {
            "completed_stocks": self.state.completed_stocks,
            "failed_stocks": self.state.failed_stocks,
            "errors": self.state.errors,
            "warnings": self.state.warnings,
            "start_time": self.state.start_time,
            "end_time": self.state.end_time
        }


# 使用示例
if __name__ == "__main__":
    # 创建批量分析流程
    flow = BatchAnalysisFlow()

    print("=== 启动批量分析流程 ===")
    print("系统将智能选择最佳的批量处理策略")
    print("请按照提示配置批量分析参数\n")

    # 启动流程
    result = flow.kickoff()

    print("\n=== 批量分析流程完成 ===")

    if result.get('success', False):
        print(f"总股票数: {result['total_stocks']}")
        print(f"成功分析: {result['completed_count']}")
        print(f"失败分析: {result['failed_count']}")
        print(f"成功率: {result['success_rate']:.1f}%")
        print(f"摘要报告: {result['summary_path']}")

        # 显示状态
        status = flow.get_batch_status()
        print(f"\n=== 批量分析状态 ===")
        for key, value in status.items():
            if isinstance(value, float):
                print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")

    else:
        print(f"批量分析失败: {result.get('error', '未知错误')}")

    # 显示详细错误信息
    detailed_results = flow.get_detailed_results()
    if detailed_results['errors']:
        print(f"\n=== 错误详情 ===")
        for error in detailed_results['errors']:
            print(f"- {error}")

    if detailed_results['warnings']:
        print(f"\n=== 警告信息 ===")
        for warning in detailed_results['warnings']:
            print(f"- {warning}")