"""
批量分析器
提供高效的批量股票分析功能
"""
import logging
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
from datetime import datetime
import json
import os

from src.stock_analysis_system import StockAnalysisSystem

logger = logging.getLogger(__name__)


class BatchStockAnalyzer:
    """批量股票分析器"""

    def __init__(self, max_workers: int = 5, cache_enabled: bool = True):
        """
        初始化批量分析器

        Args:
            max_workers: 最大并发数
            cache_enabled: 是否启用缓存
        """
        self.max_workers = max_workers
        self.cache_enabled = cache_enabled
        self.analysis_system = StockAnalysisSystem()
        self.results = {}
        self.errors = []
        self.progress = {
            'total': 0,
            'completed': 0,
            'failed': 0,
            'in_progress': 0,
            'start_time': None,
            'end_time': None,
            'estimated_remaining_time': None
        }
        self.lock = threading.Lock()
        self.progress_callback: Optional[Callable] = None

    def set_progress_callback(self, callback: Callable):
        """设置进度回调函数"""
        self.progress_callback = callback

    def analyze_multiple_stocks(self, stocks: List[Dict[str, str]],
                               strategy: str = "parallel") -> Dict[str, Any]:
        """
        批量分析多只股票

        Args:
            stocks: 股票列表，每个元素包含company和ticker
            strategy: 分析策略 (parallel, sequential, adaptive)

        Returns:
            分析结果
        """
        logger.info(f"开始批量分析 {len(stocks)} 只股票，策略: {strategy}")

        self.progress['total'] = len(stocks)
        self.progress['start_time'] = datetime.now()
        self.results.clear()
        self.errors.clear()

        if strategy == "parallel":
            return self._parallel_analysis(stocks)
        elif strategy == "sequential":
            return self._sequential_analysis(stocks)
        elif strategy == "adaptive":
            return self._adaptive_analysis(stocks)
        else:
            raise ValueError(f"不支持的策略: {strategy}")

    def _parallel_analysis(self, stocks: List[Dict[str, str]]) -> Dict[str, Any]:
        """并行分析"""
        logger.info(f"使用并行分析，最大并发数: {self.max_workers}")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_stock = {
                executor.submit(self._analyze_single_stock_with_retry, stock): stock
                for stock in stocks
            }

            # 等待所有任务完成
            for future in as_completed(future_to_stock):
                stock = future_to_stock[future]
                try:
                    result = future.result()
                    with self.lock:
                        if result.get('success', False):
                            self.results[stock['ticker']] = result
                            self.progress['completed'] += 1
                        else:
                            self.errors.append({
                                'stock': stock,
                                'error': result.get('error', '未知错误')
                            })
                            self.progress['failed'] += 1

                    self._update_progress()
                    self._notify_progress_callback()

                except Exception as e:
                    with self.lock:
                        self.errors.append({
                            'stock': stock,
                            'error': str(e)
                        })
                        self.progress['failed'] += 1

                    self._update_progress()
                    self._notify_progress_callback()

        return self._generate_batch_result()

    def _sequential_analysis(self, stocks: List[Dict[str, str]]) -> Dict[str, Any]:
        """顺序分析"""
        logger.info("使用顺序分析")

        for stock in stocks:
            try:
                with self.lock:
                    self.progress['in_progress'] += 1

                result = self._analyze_single_stock_with_retry(stock)

                with self.lock:
                    if result.get('success', False):
                        self.results[stock['ticker']] = result
                        self.progress['completed'] += 1
                    else:
                        self.errors.append({
                            'stock': stock,
                            'error': result.get('error', '未知错误')
                        })
                        self.progress['failed'] += 1

                self._update_progress()
                self._notify_progress_callback()

            except Exception as e:
                with self.lock:
                    self.errors.append({
                        'stock': stock,
                        'error': str(e)
                    })
                    self.progress['failed'] += 1

                self._update_progress()
                self._notify_progress_callback()

            finally:
                with self.lock:
                    self.progress['in_progress'] -= 1

        return self._generate_batch_result()

    def _adaptive_analysis(self, stocks: List[Dict[str, str]]) -> Dict[str, Any]:
        """自适应分析"""
        logger.info("使用自适应分析")

        # 根据股票数量自适应选择策略
        if len(stocks) <= 3:
            return self._sequential_analysis(stocks)
        elif len(stocks) <= 10:
            return self._parallel_analysis(stocks)
        else:
            # 分批并行处理
            return self._batch_parallel_analysis(stocks)

    def _batch_parallel_analysis(self, stocks: List[Dict[str, str]]) -> Dict[str, Any]:
        """分批并行分析"""
        logger.info("使用分批并行分析")

        batch_size = min(self.max_workers * 2, 10)  # 每批最多10只股票
        batches = [stocks[i:i + batch_size] for i in range(0, len(stocks), batch_size)]

        all_results = {}

        for i, batch in enumerate(batches):
            logger.info(f"处理批次 {i + 1}/{len(batches)}，包含 {len(batch)} 只股票")

            # 处理当前批次
            batch_result = self._parallel_analysis(batch)

            # 合并结果
            all_results.update(self.results)

            # 批次间暂停，避免API限制
            if i < len(batches) - 1:
                time.sleep(2)

        self.results = all_results
        return self._generate_batch_result()

    def _analyze_single_stock_with_retry(self, stock: Dict[str, str],
                                       max_retries: int = 2) -> Dict[str, Any]:
        """带重试机制的单股票分析"""
        for attempt in range(max_retries + 1):
            try:
                logger.debug(f"分析 {stock['company']} (尝试 {attempt + 1}/{max_retries + 1})")

                result = self.analysis_system.analyze_stock(
                    stock['company'],
                    stock['ticker'],
                    use_cache=self.cache_enabled
                )

                if result.get('success', False):
                    return result
                elif attempt < max_retries:
                    logger.warning(f"分析 {stock['company']} 失败，重试中...")
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    return result

            except Exception as e:
                if attempt < max_retries:
                    logger.warning(f"分析 {stock['company']} 异常，重试中... 错误: {str(e)}")
                    time.sleep(2 ** attempt)
                else:
                    return {
                        'success': False,
                        'error': str(e),
                        'company': stock['company'],
                        'ticker': stock['ticker']
                    }

        return {
            'success': False,
            'error': '重试次数超过限制',
            'company': stock['company'],
            'ticker': stock['ticker']
        }

    def _update_progress(self):
        """更新进度信息"""
        total = self.progress['total']
        completed = self.progress['completed']
        failed = self.progress['failed']

        # 计算完成百分比
        self.progress['percentage'] = ((completed + failed) / total) * 100 if total > 0 else 0

        # 计算剩余时间
        if self.progress['start_time'] and completed > 0:
            elapsed_time = (datetime.now() - self.progress['start_time']).total_seconds()
            avg_time_per_stock = elapsed_time / completed
            remaining_stocks = total - completed - failed
            self.progress['estimated_remaining_time'] = remaining_stocks * avg_time_per_stock

        # 更新结束时间
        if self.progress['percentage'] >= 100:
            self.progress['end_time'] = datetime.now()

    def _notify_progress_callback(self):
        """通知进度回调"""
        if self.progress_callback:
            try:
                self.progress_callback(self.progress.copy())
            except Exception as e:
                logger.error(f"进度回调失败: {str(e)}")

    def _generate_batch_result(self) -> Dict[str, Any]:
        """生成批量分析结果"""
        success_count = len(self.results)
        failed_count = len(self.errors)
        total_count = self.progress['total']

        result = {
            'success': True,
            'total_count': total_count,
            'success_count': success_count,
            'failed_count': failed_count,
            'success_rate': (success_count / total_count) * 100 if total_count > 0 else 0,
            'results': self.results,
            'errors': self.errors,
            'progress': self.progress.copy(),
            'summary': self._generate_summary()
        }

        logger.info(f"批量分析完成: {success_count}/{total_count} 成功")
        return result

    def _generate_summary(self) -> Dict[str, Any]:
        """生成分析摘要"""
        summary = {
            'analysis_time': datetime.now().isoformat(),
            'total_stocks': self.progress['total'],
            'successful_analyses': len(self.results),
            'failed_analyses': len(self.errors),
            'average_score': 0,
            'rating_distribution': {},
            'top_performers': [],
            'bottom_performers': []
        }

        # 计算平均评分
        scores = [result.get('overall_score', 0) for result in self.results.values()]
        if scores:
            summary['average_score'] = sum(scores) / len(scores)

        # 评级分布
        rating_counts = {}
        for result in self.results.values():
            rating = result.get('investment_rating', {}).get('rating', '未评级')
            rating_counts[rating] = rating_counts.get(rating, 0) + 1

        summary['rating_distribution'] = rating_counts

        # 表现最佳和最差的股票
        sorted_results = sorted(
            self.results.items(),
            key=lambda x: x[1].get('overall_score', 0),
            reverse=True
        )

        summary['top_performers'] = [
            {'ticker': ticker, 'score': result.get('overall_score', 0)}
            for ticker, result in sorted_results[:5]
        ]

        summary['bottom_performers'] = [
            {'ticker': ticker, 'score': result.get('overall_score', 0)}
            for ticker, result in sorted_results[-5:]
        ]

        return summary

    def export_results(self, export_format: str = "json", filepath: str = "") -> str:
        """
        导出分析结果

        Args:
            export_format: 导出格式 (json, csv, excel)
            filepath: 文件路径

        Returns:
            导出文件路径
        """
        if not filepath:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f"exports/batch_analysis_{timestamp}.{export_format}"

        # 确保导出目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        try:
            if export_format == "json":
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump({
                        'results': self.results,
                        'errors': self.errors,
                        'summary': self._generate_summary()
                    }, f, ensure_ascii=False, indent=2)

            elif export_format == "csv":
                import pandas as pd
                rows = []
                for ticker, result in self.results.items():
                    rows.append({
                        'ticker': ticker,
                        'company': result.get('company', ''),
                        'overall_score': result.get('overall_score', 0),
                        'rating': result.get('investment_rating', {}).get('rating', ''),
                        'success': result.get('success', False)
                    })

                df = pd.DataFrame(rows)
                df.to_csv(filepath, index=False, encoding='utf-8')

            elif export_format == "excel":
                import pandas as pd
                rows = []
                for ticker, result in self.results.items():
                    rows.append({
                        'ticker': ticker,
                        'company': result.get('company', ''),
                        'overall_score': result.get('overall_score', 0),
                        'rating': result.get('investment_rating', {}).get('rating', ''),
                        'success': result.get('success', False),
                        'analysis_time': result.get('timestamp', '')
                    })

                df = pd.DataFrame(rows)
                df.to_excel(filepath, index=False)

            else:
                raise ValueError(f"不支持的导出格式: {export_format}")

            logger.info(f"结果已导出: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"导出结果失败: {str(e)}")
            raise

    def get_progress(self) -> Dict[str, Any]:
        """获取当前进度"""
        return self.progress.copy()

    def get_results(self) -> Dict[str, Any]:
        """获取分析结果"""
        return self.results.copy()

    def get_errors(self) -> List[Dict[str, Any]]:
        """获取错误信息"""
        return self.errors.copy()

    def clear_results(self):
        """清空结果"""
        self.results.clear()
        self.errors.clear()
        self.progress = {
            'total': 0,
            'completed': 0,
            'failed': 0,
            'in_progress': 0,
            'start_time': None,
            'end_time': None,
            'estimated_remaining_time': None
        }


# 使用示例
if __name__ == "__main__":
    # 创建批量分析器
    analyzer = BatchStockAnalyzer(max_workers=3)

    # 设置进度回调
    def progress_callback(progress):
        print(f"进度: {progress['percentage']:.1f}% ({progress['completed']}/{progress['total']})")

    analyzer.set_progress_callback(progress_callback)

    # 测试股票列表
    test_stocks = [
        {'company': '苹果公司', 'ticker': 'AAPL'},
        {'company': '微软', 'ticker': 'MSFT'},
        {'company': '谷歌', 'ticker': 'GOOGL'},
        {'company': '亚马逊', 'ticker': 'AMZN'},
        {'company': '特斯拉', 'ticker': 'TSLA'}
    ]

    # 执行批量分析
    print("开始批量分析...")
    result = analyzer.analyze_multiple_stocks(test_stocks, strategy="parallel")

    print(f"\n分析结果:")
    print(f"总计: {result['total_count']}")
    print(f"成功: {result['success_count']}")
    print(f"失败: {result['failed_count']}")
    print(f"成功率: {result['success_rate']:.1f}%")

    # 导出结果
    export_path = analyzer.export_results("json")
    print(f"结果已导出: {export_path}")