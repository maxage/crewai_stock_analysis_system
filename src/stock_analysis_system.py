"""
股票分析系统主协调器
整合所有Crews和Flows，提供统一的分析接口
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from src.crews.data_collection_crew import DataCollectionCrew
from src.crews.analysis_crew import AnalysisCrew
from src.crews.decision_crew import DecisionCrew

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockAnalysisSystem:
    """股票分析系统主类"""

    def __init__(self):
        """初始化系统"""
        self.data_collection_crew = DataCollectionCrew()
        self.analysis_crew = AnalysisCrew()
        self.decision_crew = DecisionCrew()

        self.analysis_history = []
        self.cache = {}
        self.cache_ttl = 3600  # 1小时缓存

        logger.info("股票分析系统初始化完成")

    def analyze_stock(self, company: str, ticker: str,
                     use_cache: bool = True) -> Dict[str, Any]:
        """
        分析单只股票

        Args:
            company: 公司名称
            ticker: 股票代码
            use_cache: 是否使用缓存

        Returns:
            分析结果字典
        """
        logger.info(f"开始分析股票: {company} ({ticker})")

        # 检查缓存
        if use_cache and self._check_cache(ticker):
            logger.info(f"使用缓存数据: {ticker}")
            return self._get_from_cache(ticker)

        try:
            # 第一阶段：数据收集
            logger.info("第一阶段：数据收集")
            collection_result = self.data_collection_crew.execute_data_collection(
                company, ticker
            )

            if not collection_result['success']:
                return {
                    'success': False,
                    'error': f"数据收集失败: {collection_result['error']}",
                    'company': company,
                    'ticker': ticker
                }

            # 第二阶段：分析
            logger.info("第二阶段：分析")
            analysis_result = self.analysis_crew.execute_analysis(
                company, ticker, collection_result['data']
            )

            if not analysis_result['success']:
                return {
                    'success': False,
                    'error': f"分析失败: {analysis_result['error']}",
                    'company': company,
                    'ticker': ticker
                }

            # 第三阶段：决策
            logger.info("第三阶段：决策")
            decision_result = self.decision_crew.execute_decision_process(
                company, ticker, analysis_result['data']
            )

            if not decision_result['success']:
                return {
                    'success': False,
                    'error': f"决策失败: {decision_result['error']}",
                    'company': company,
                    'ticker': ticker
                }

            # 整合所有结果
            final_result = self._integrate_results(
                company, ticker,
                collection_result['data'],
                analysis_result['data'],
                decision_result['data']
            )

            # 缓存结果
            if use_cache:
                self._save_to_cache(ticker, final_result)

            # 添加到历史记录
            self._add_to_history(final_result)

            logger.info(f"股票分析完成: {company} ({ticker})")
            return final_result

        except Exception as e:
            logger.error(f"股票分析异常: {company} ({ticker}), 错误: {str(e)}")
            return {
                'success': False,
                'error': f"分析过程发生异常: {str(e)}",
                'company': company,
                'ticker': ticker
            }

    def analyze_multiple_stocks(self, stocks: List[Dict[str, str]],
                               max_workers: int = 3) -> List[Dict[str, Any]]:
        """
        批量分析多只股票

        Args:
            stocks: 股票列表，每个元素包含company和ticker
            max_workers: 最大并发数

        Returns:
            分析结果列表
        """
        logger.info(f"开始批量分析 {len(stocks)} 只股票")

        import concurrent.futures
        import threading

        results = []
        lock = threading.Lock()

        def analyze_single_stock(stock_data):
            try:
                result = self.analyze_stock(
                    stock_data['company'],
                    stock_data['ticker'],
                    use_cache=True
                )
                with lock:
                    results.append(result)
            except Exception as e:
                with lock:
                    results.append({
                        'success': False,
                        'error': str(e),
                        'company': stock_data['company'],
                        'ticker': stock_data['ticker']
                    })

        # 使用线程池并行执行
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for stock_data in stocks:
                future = executor.submit(analyze_single_stock, stock_data)
                futures.append(future)

            # 等待所有任务完成
            concurrent.futures.wait(futures)

        logger.info(f"批量分析完成，成功: {len([r for r in results if r['success']])}/{len(stocks)}")
        return results

    def generate_summary_report(self, results: List[Dict[str, Any]]) -> str:
        """
        生成批量分析摘要报告

        Args:
            results: 分析结果列表

        Returns:
            摘要报告
        """
        logger.info("生成批量分析摘要报告")

        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]

        report = f"""
# 批量股票分析报告

**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**总股票数**: {len(results)}
**成功分析**: {len(successful_results)}
**失败分析**: {len(failed_results)}

## 分析摘要

### 成功分析股票

"""

        for result in successful_results:
            rating = result.get('investment_rating', {})
            report += f"- **{result['company']} ({result['ticker']})**: {rating.get('rating', '未评级')}\n"

        if failed_results:
            report += "\n### 失败分析股票\n"
            for result in failed_results:
                report += f"- **{result['company']} ({result['ticker']})**: {result.get('error', '未知错误')}\n"

        # 统计分析
        if successful_results:
            report += "\n## 统计分析\n"

            # 投资评级统计
            rating_stats = {}
            for result in successful_results:
                rating = result.get('investment_rating', {}).get('rating', '未评级')
                rating_stats[rating] = rating_stats.get(rating, 0) + 1

            report += "### 投资评级分布\n"
            for rating, count in rating_stats.items():
                percentage = (count / len(successful_results)) * 100
                report += f"- {rating}: {count} ({percentage:.1f}%)\n"

            # 综合评分统计
            scores = [result.get('overall_score', 0) for result in successful_results]
            if scores:
                avg_score = sum(scores) / len(scores)
                report += f"\n### 综合评分统计\n"
                report += f"- 平均综合评分: {avg_score:.1f}/100\n"
                report += f"- 最高评分: {max(scores):.1f}/100\n"
                report += f"- 最低评分: {min(scores):.1f}/100\n"

        report += "\n---\n*报告由股票分析系统自动生成*\n"

        return report

    def _integrate_results(self, company: str, ticker: str,
                          collection_data: Dict,
                          analysis_data: Dict,
                          decision_data: Dict) -> Dict[str, Any]:
        """整合所有分析结果"""
        # 计算综合评分
        scores = self.analysis_crew.calculate_analysis_score(analysis_data)

        # 获取投资评级
        investment_rating = self.decision_crew.get_investment_rating(decision_data)

        # 生成分析摘要
        analysis_summary = self.analysis_crew.generate_analysis_summary(analysis_data)

        # 生成完整报告
        full_report = self.decision_crew.generate_investment_report(
            company, ticker, {
                **collection_data,
                **analysis_data,
                **decision_data
            }
        )

        # 保存报告和导出数据
        report_path = self.decision_crew.save_report(company, ticker, full_report)
        data_path = self.decision_crew.export_to_json(company, ticker, {
            'company': company,
            'ticker': ticker,
            'collection_data': collection_data,
            'analysis_data': analysis_data,
            'decision_data': decision_data,
            'scores': scores,
            'investment_rating': investment_rating
        })

        return {
            'success': True,
            'company': company,
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'collection_data': collection_data,
            'analysis_data': analysis_data,
            'decision_data': decision_data,
            'scores': scores,
            'investment_rating': investment_rating,
            'analysis_summary': analysis_summary,
            'full_report': full_report,
            'report_path': report_path,
            'data_path': data_path,
            'overall_score': scores['overall_score']
        }

    def _check_cache(self, ticker: str) -> bool:
        """检查缓存"""
        if ticker in self.cache:
            cache_time = self.cache[ticker].get('timestamp', 0)
            current_time = datetime.now().timestamp()
            return (current_time - cache_time) < self.cache_ttl
        return False

    def _get_from_cache(self, ticker: str) -> Dict[str, Any]:
        """从缓存获取数据"""
        return self.cache.get(ticker, {})

    def _save_to_cache(self, ticker: str, data: Dict[str, Any]):
        """保存到缓存"""
        self.cache[ticker] = {
            'data': data,
            'timestamp': datetime.now().timestamp()
        }

    def _add_to_history(self, result: Dict[str, Any]):
        """添加到历史记录"""
        self.analysis_history.append({
            'company': result['company'],
            'ticker': result['ticker'],
            'timestamp': result['timestamp'],
            'success': result['success'],
            'overall_score': result.get('overall_score', 0),
            'investment_rating': result.get('investment_rating', {}).get('rating', '未评级')
        })

        # 保持历史记录在合理范围内
        if len(self.analysis_history) > 1000:
            self.analysis_history = self.analysis_history[-1000:]

    def get_analysis_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取分析历史"""
        return self.analysis_history[-limit:]

    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        return {
            'cache_size': len(self.cache),
            'history_size': len(self.analysis_history),
            'cache_ttl': self.cache_ttl
        }

    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        logger.info("缓存已清空")

    def export_history(self, filepath: str):
        """导出历史记录"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_history, f, ensure_ascii=False, indent=2)
            logger.info(f"历史记录已导出: {filepath}")
        except Exception as e:
            logger.error(f"导出历史记录失败: {str(e)}")


# 使用示例
if __name__ == "__main__":
    # 创建系统实例
    system = StockAnalysisSystem()

    # 单个股票分析示例
    print("=== 单个股票分析 ===")
    result = system.analyze_stock("苹果公司", "AAPL")
    if result['success']:
        print(f"分析成功: {result['company']}")
        print(f"投资评级: {result['investment_rating']['rating']}")
        print(f"综合评分: {result['overall_score']:.1f}/100")
        print(f"报告路径: {result['report_path']}")
    else:
        print(f"分析失败: {result['error']}")

    # 批量分析示例
    print("\n=== 批量股票分析 ===")
    stocks = [
        {'company': '微软', 'ticker': 'MSFT'},
        {'company': '谷歌', 'ticker': 'GOOGL'},
        {'company': '亚马逊', 'ticker': 'AMZN'}
    ]

    batch_results = system.analyze_multiple_stocks(stocks)
    print(f"批量分析完成: {len(batch_results)} 只股票")

    # 生成摘要报告
    summary_report = system.generate_summary_report(batch_results)
    print("\n=== 摘要报告 ===")
    print(summary_report[:500] + "...")

    # 查看缓存统计
    cache_stats = system.get_cache_stats()
    print(f"\n缓存统计: {cache_stats}")