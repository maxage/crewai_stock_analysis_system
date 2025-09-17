"""
实时监控模块
提供股票实时监控、预警和通知功能
"""
import logging
from typing import List, Dict, Any, Optional, Callable
import schedule
import time
import threading
import json
from datetime import datetime, timedelta
import os
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

from src.stock_analysis_system import StockAnalysisSystem

logger = logging.getLogger(__name__)


class StockMonitor:
    """股票实时监控器"""

    def __init__(self, analysis_system: Optional[StockAnalysisSystem] = None):
        """
        初始化监控器

        Args:
            analysis_system: 股票分析系统实例
        """
        self.analysis_system = analysis_system or StockAnalysisSystem()
        self.monitoring_stocks = {}
        self.alert_rules = {}
        self.monitoring = False
        self.monitor_thread = None
        self.alert_callbacks = []
        self.last_check_time = {}
        self.monitoring_interval = 300  # 5分钟

        # 邮件通知配置
        self.email_config = {
            'enabled': False,
            'smtp_server': '',
            'smtp_port': 587,
            'username': '',
            'password': '',
            'from_email': '',
            'to_emails': []
        }

    def add_stock_to_monitor(self, company: str, ticker: str,
                            check_interval: int = 300) -> bool:
        """
        添加股票到监控列表

        Args:
            company: 公司名称
            ticker: 股票代码
            check_interval: 检查间隔（秒）

        Returns:
            是否添加成功
        """
        try:
            self.monitoring_stocks[ticker] = {
                'company': company,
                'ticker': ticker,
                'check_interval': check_interval,
                'last_analysis': None,
                'last_score': 0,
                'last_rating': '',
                'price_history': [],
                'score_history': [],
                'alert_count': 0,
                'added_time': datetime.now()
            }

            logger.info(f"已添加股票到监控列表: {company} ({ticker})")
            return True

        except Exception as e:
            logger.error(f"添加监控股票失败: {str(e)}")
            return False

    def remove_stock_from_monitor(self, ticker: str) -> bool:
        """
        从监控列表移除股票

        Args:
            ticker: 股票代码

        Returns:
            是否移除成功
        """
        try:
            if ticker in self.monitoring_stocks:
                del self.monitoring_stocks[ticker]
                logger.info(f"已从监控列表移除: {ticker}")
                return True
            else:
                logger.warning(f"股票不在监控列表中: {ticker}")
                return False

        except Exception as e:
            logger.error(f"移除监控股票失败: {str(e)}")
            return False

    def add_alert_rule(self, rule_id: str, ticker: str, rule_type: str,
                      condition: str, threshold: float, message: str) -> bool:
        """
        添加预警规则

        Args:
            rule_id: 规则ID
            ticker: 股票代码
            rule_type: 规则类型 (price, score, rating_change, volume)
            condition: 条件 (above, below, equal, change)
            threshold: 阈值
            message: 预警消息

        Returns:
            是否添加成功
        """
        try:
            self.alert_rules[rule_id] = {
                'ticker': ticker,
                'rule_type': rule_type,
                'condition': condition,
                'threshold': threshold,
                'message': message,
                'created_time': datetime.now(),
                'trigger_count': 0,
                'last_triggered': None,
                'enabled': True
            }

            logger.info(f"已添加预警规则: {rule_id}")
            return True

        except Exception as e:
            logger.error(f"添加预警规则失败: {str(e)}")
            return False

    def configure_email_alerts(self, smtp_server: str, smtp_port: int,
                             username: str, password: str,
                             from_email: str, to_emails: List[str]):
        """
        配置邮件预警

        Args:
            smtp_server: SMTP服务器
            smtp_port: SMTP端口
            username: 用户名
            password: 密码
            from_email: 发件邮箱
            to_emails: 收件邮箱列表
        """
        self.email_config = {
            'enabled': True,
            'smtp_server': smtp_server,
            'smtp_port': smtp_port,
            'username': username,
            'password': password,
            'from_email': from_email,
            'to_emails': to_emails
        }

        logger.info("邮件预警配置已启用")

    def add_alert_callback(self, callback: Callable):
        """
        添加预警回调函数

        Args:
            callback: 回调函数，接收alert_data参数
        """
        self.alert_callbacks.append(callback)
        logger.info("预警回调函数已添加")

    def start_monitoring(self, interval: int = 300):
        """
        开始监控

        Args:
            interval: 监控间隔（秒）
        """
        if self.monitoring:
            logger.warning("监控已在运行中")
            return

        self.monitoring_interval = interval
        self.monitoring = True

        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self._monitoring_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        logger.info(f"股票监控已启动，监控间隔: {interval}秒")

    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        logger.info("股票监控已停止")

    def _monitoring_loop(self):
        """监控循环"""
        while self.monitoring:
            try:
                self._check_all_stocks()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"监控循环异常: {str(e)}")
                time.sleep(60)  # 出错后暂停1分钟

    def _check_all_stocks(self):
        """检查所有监控的股票"""
        current_time = datetime.now()

        for ticker, stock_info in self.monitoring_stocks.items():
            try:
                # 检查是否需要更新
                last_check = stock_info.get('last_check_time')
                if (last_check and
                    (current_time - last_check).total_seconds() < stock_info['check_interval']):
                    continue

                # 执行分析
                result = self.analysis_system.analyze_stock(
                    stock_info['company'], ticker, use_cache=False
                )

                if result.get('success', False):
                    # 更新股票信息
                    self._update_stock_info(ticker, result)
                    # 检查预警规则
                    self._check_alert_rules(ticker, result)

                # 更新最后检查时间
                stock_info['last_check_time'] = current_time

            except Exception as e:
                logger.error(f"检查股票 {ticker} 失败: {str(e)}")

    def _update_stock_info(self, ticker: str, result: Dict[str, Any]):
        """更新股票信息"""
        if ticker not in self.monitoring_stocks:
            return

        stock_info = self.monitoring_stocks[ticker]

        # 更新基本信息
        stock_info['last_analysis'] = result
        stock_info['last_score'] = result.get('overall_score', 0)
        stock_info['last_rating'] = result.get('investment_rating', {}).get('rating', '')

        # 更新历史数据
        current_price = self._extract_current_price(result)
        if current_price:
            stock_info['price_history'].append({
                'price': current_price,
                'time': datetime.now()
            })
            # 保持最近100条记录
            if len(stock_info['price_history']) > 100:
                stock_info['price_history'] = stock_info['price_history'][-100:]

        # 更新评分历史
        score = result.get('overall_score', 0)
        stock_info['score_history'].append({
            'score': score,
            'time': datetime.now()
        })
        # 保持最近50条记录
        if len(stock_info['score_history']) > 50:
            stock_info['score_history'] = stock_info['score_history'][-50:]

    def _check_alert_rules(self, ticker: str, result: Dict[str, Any]):
        """检查预警规则"""
        current_price = self._extract_current_price(result)
        current_score = result.get('overall_score', 0)
        current_rating = result.get('investment_rating', {}).get('rating', '')

        for rule_id, rule in self.alert_rules.items():
            if not rule['enabled'] or rule['ticker'] != ticker:
                continue

            triggered = False

            # 检查不同类型的规则
            if rule['rule_type'] == 'price' and current_price:
                triggered = self._check_price_rule(current_price, rule)
            elif rule['rule_type'] == 'score':
                triggered = self._check_score_rule(current_score, rule)
            elif rule['rule_type'] == 'rating_change':
                triggered = self._check_rating_change_rule(current_rating, ticker, rule)

            if triggered:
                self._trigger_alert(rule_id, rule, result)

    def _check_price_rule(self, current_price: float, rule: Dict) -> bool:
        """检查价格预警规则"""
        threshold = rule['threshold']
        condition = rule['condition']

        if condition == 'above':
            return current_price > threshold
        elif condition == 'below':
            return current_price < threshold
        elif condition == 'equal':
            return abs(current_price - threshold) < 0.01

        return False

    def _check_score_rule(self, current_score: float, rule: Dict) -> bool:
        """检查评分预警规则"""
        threshold = rule['threshold']
        condition = rule['condition']

        if condition == 'above':
            return current_score > threshold
        elif condition == 'below':
            return current_score < threshold
        elif condition == 'equal':
            return abs(current_score - threshold) < 0.1

        return False

    def _check_rating_change_rule(self, current_rating: str, ticker: str, rule: Dict) -> bool:
        """检查评级变化预警规则"""
        if ticker not in self.monitoring_stocks:
            return False

        last_rating = self.monitoring_stocks[ticker]['last_rating']
        threshold = rule['threshold']

        # 检查评级变化
        rating_changes = {
            'upgrade': last_rating != current_rating and current_rating in ['强烈买入', '买入'],
            'downgrade': last_rating != current_rating and current_rating in ['卖出', '减持']
        }

        condition = rule['condition']
        if condition in rating_changes:
            return rating_changes[condition]

        return False

    def _trigger_alert(self, rule_id: str, rule: Dict, result: Dict[str, Any]):
        """触发预警"""
        # 更新规则统计
        rule['trigger_count'] += 1
        rule['last_triggered'] = datetime.now()

        # 生成预警数据
        alert_data = {
            'rule_id': rule_id,
            'ticker': rule['ticker'],
            'rule_type': rule['rule_type'],
            'message': rule['message'],
            'triggered_at': datetime.now(),
            'current_data': result,
            'trigger_count': rule['trigger_count']
        }

        # 调用回调函数
        for callback in self.alert_callbacks:
            try:
                callback(alert_data)
            except Exception as e:
                logger.error(f"预警回调失败: {str(e)}")

        # 发送邮件预警
        if self.email_config['enabled']:
            self._send_email_alert(alert_data)

        # 记录预警
        self._log_alert(alert_data)

        logger.info(f"预警已触发: {rule_id} - {rule['ticker']}")

    def _send_email_alert(self, alert_data: Dict[str, Any]):
        """发送邮件预警"""
        try:
            if not self.email_config['enabled']:
                return

            # 创建邮件内容
            subject = f"股票预警: {alert_data['ticker']}"
            body = self._generate_alert_email_body(alert_data)

            # 创建邮件
            msg = MimeMultipart()
            msg['From'] = self.email_config['from_email']
            msg['Subject'] = subject

            # 添加正文
            msg.attach(MimeText(body, 'plain', 'utf-8'))

            # 发送邮件
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])

            for to_email in self.email_config['to_emails']:
                msg['To'] = to_email
                server.send_message(msg)
                del msg['To']

            server.quit()

            logger.info(f"邮件预警已发送: {alert_data['rule_id']}")

        except Exception as e:
            logger.error(f"发送邮件预警失败: {str(e)}")

    def _generate_alert_email_body(self, alert_data: Dict[str, Any]) -> str:
        """生成预警邮件正文"""
        return f"""
股票预警通知

预警规则: {alert_data['rule_id']}
股票代码: {alert_data['ticker']}
预警类型: {alert_data['rule_type']}
触发时间: {alert_data['triggered_at'].strftime('%Y-%m-%d %H:%M:%S')}

预警信息:
{alert_data['message']}

当前数据:
- 投资评级: {alert_data['current_data'].get('investment_rating', {}).get('rating', 'N/A')}
- 综合评分: {alert_data['current_data'].get('overall_score', 0):.1f}/100
- 分析时间: {alert_data['current_data'].get('timestamp', 'N/A')}

请及时关注相关股票动态。

---
此邮件由股票监控系统自动发送
"""

    def _log_alert(self, alert_data: Dict[str, Any]):
        """记录预警日志"""
        log_entry = {
            'timestamp': alert_data['triggered_at'],
            'rule_id': alert_data['rule_id'],
            'ticker': alert_data['ticker'],
            'message': alert_data['message']
        }

        # 写入日志文件
        try:
            os.makedirs('logs', exist_ok=True)
            log_file = 'logs/alerts.log'

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

        except Exception as e:
            logger.error(f"记录预警日志失败: {str(e)}")

    def _extract_current_price(self, result: Dict[str, Any]) -> Optional[float]:
        """从分析结果中提取当前价格"""
        try:
            # 从财务数据中提取价格
            financial_data = result.get('collection_data', {}).get('financial_data', {})
            if isinstance(financial_data, dict):
                current_price = financial_data.get('current_price')
                if current_price:
                    return float(current_price)

            # 从技术分析数据中提取
            technical_data = result.get('collection_data', {}).get('technical_analysis', {})
            if isinstance(technical_data, dict):
                current_price = technical_data.get('current_price')
                if current_price:
                    return float(current_price)

        except (ValueError, TypeError):
            pass

        return None

    def get_monitoring_status(self) -> Dict[str, Any]:
        """获取监控状态"""
        return {
            'monitoring': self.monitoring,
            'monitored_stocks': len(self.monitoring_stocks),
            'alert_rules': len(self.alert_rules),
            'monitoring_interval': self.monitoring_interval,
            'last_check_time': self.last_check_time,
            'monitored_tickers': list(self.monitoring_stocks.keys())
        }

    def get_stock_status(self, ticker: str) -> Optional[Dict[str, Any]]:
        """获取特定股票的监控状态"""
        return self.monitoring_stocks.get(ticker)

    def get_alert_history(self, ticker: Optional[str] = None,
                         limit: int = 100) -> List[Dict[str, Any]]:
        """获取预警历史"""
        alerts = []

        try:
            if os.path.exists('logs/alerts.log'):
                with open('logs/alerts.log', 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            alert = json.loads(line.strip())
                            if ticker is None or alert.get('ticker') == ticker:
                                alerts.append(alert)
                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            logger.error(f"读取预警历史失败: {str(e)}")

        # 按时间排序并限制数量
        alerts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return alerts[:limit]


# 使用示例
if __name__ == "__main__":
    # 创建监控器
    monitor = StockMonitor()

    # 添加监控股票
    monitor.add_stock_to_monitor("苹果公司", "AAPL", check_interval=300)
    monitor.add_stock_to_monitor("微软", "MSFT", check_interval=300)

    # 添加预警规则
    monitor.add_alert_rule(
        "price_alert_aapl",
        "AAPL",
        "price",
        "above",
        180.0,
        "苹果股价突破180美元"
    )

    monitor.add_alert_rule(
        "score_alert_msft",
        "MSFT",
        "score",
        "below",
        60.0,
        "微软评分低于60分"
    )

    # 添加预警回调
    def alert_callback(alert_data):
        print(f"预警触发: {alert_data['ticker']} - {alert_data['message']}")

    monitor.add_alert_callback(alert_callback)

    # 启动监控
    monitor.start_monitoring(interval=60)

    print("监控已启动，按Ctrl+C停止...")

    try:
        while True:
            time.sleep(10)
            status = monitor.get_monitoring_status()
            print(f"监控状态: {status['monitored_stocks']} 只股票, {status['alert_rules']} 个预警规则")

    except KeyboardInterrupt:
        monitor.stop_monitoring()
        print("监控已停止")