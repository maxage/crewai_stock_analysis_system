# 股票分析系统

基于CrewAI框架构建的智能股票分析系统，利用多Agent协作和智能流程控制，提供全面的股票投资分析服务。

## 🚀 特性

### 核心功能
- **智能股票分析**: 基于AI的多维度股票分析
- **批量处理**: 高效的批量股票分析
- **实时监控**: 股票价格和指标实时监控
- **预警系统**: 智能预警和通知
- **Web界面**: 直观的Web管理界面

### 技术亮点
- **多Agent协作**: 专业化Agent团队协作
- **智能流程控制**: 基于Flows的动态流程控制
- **自定义工具**: 丰富的金融分析工具
- **缓存机制**: 智能缓存提高效率
- **扩展性**: 模块化设计，易于扩展

## 📋 系统架构

### Agent团队
1. **数据收集团队**
   - 市场研究员
   - 财务数据专家
   - 技术分析师
   - 数据验证专家

2. **分析团队**
   - 基本面分析师
   - 风险评估师
   - 行业专家

3. **决策团队**
   - 投资策略顾问
   - 报告生成器
   - 质量监控员

### 流程控制
- **Crews模式**: Agent自主协作
- **Flows模式**: 精确流程控制
- **混合架构**: 根据需求动态调整

## 🛠️ 安装和配置

### 1. 环境要求
- Python 3.8+
- OpenAI API Key
- Serper API Key (可选，用于网络搜索)

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 环境配置
复制并配置环境变量文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件：
```
OPENAI_API_KEY=your-openai-key-here
SERPER_API_KEY=your-serper-key-here
OPENAI_MODEL_NAME=gpt-4-turbo-preview
```

## 📖 使用指南

### 命令行界面

#### 单股票分析
```bash
python main.py single --company "苹果公司" --ticker "AAPL"
```

#### 批量分析
```bash
python main.py batch
```

#### 交互式流程
```bash
python main.py interactive
```

#### 批量分析流程
```bash
python main.py batch-flow
```

### Web界面
```bash
python src/web_app.py
```

访问 `http://localhost:5000` 使用Web界面。

### 编程接口

```python
from src.stock_analysis_system import StockAnalysisSystem

# 创建系统实例
system = StockAnalysisSystem()

# 分析单只股票
result = system.analyze_stock("苹果公司", "AAPL")

# 批量分析
stocks = [
    {'company': '微软', 'ticker': 'MSFT'},
    {'company': '谷歌', 'ticker': 'GOOGL'}
]
results = system.analyze_multiple_stocks(stocks)

# 生成摘要报告
summary = system.generate_summary_report(results)
print(summary)
```

## 📊 分析报告示例

系统会生成包含以下维度的综合分析报告：

### 市场分析
- 行业竞争态势
- 市场情绪分析
- 宏观环境影响

### 财务分析
- 财务指标评估
- 盈利能力分析
- 财务健康度

### 技术分析
- 价格趋势分析
- 技术指标计算
- 交易信号识别

### 基本面分析
- 公司价值评估
- 竞争优势分析
- 成长性预测

### 风险评估
- 风险识别
- 风险量化
- 风险控制建议

### 投资建议
- 投资评级
- 目标价位
- 策略建议

## 🔧 高级功能

### 实时监控
```python
from src.utils.monitor import StockMonitor

# 创建监控器
monitor = StockMonitor()

# 添加监控股票
monitor.add_stock_to_monitor("苹果公司", "AAPL", interval=300)

# 添加预警规则
monitor.add_alert_rule(
    "price_alert",
    "AAPL",
    "price",
    "above",
    180.0,
    "苹果股价突破180美元"
)

# 启动监控
monitor.start_monitoring()
```

### 批量分析器
```python
from src.utils.batch_analyzer import BatchStockAnalyzer

# 创建批量分析器
analyzer = BatchStockAnalyzer(max_workers=5)

# 设置进度回调
def progress_callback(progress):
    print(f"进度: {progress['percentage']:.1f}%")

analyzer.set_progress_callback(progress_callback)

# 执行批量分析
stocks = [
    {'company': '苹果公司', 'ticker': 'AAPL'},
    {'company': '微软', 'ticker': 'MSFT'},
    # ... 更多股票
]
result = analyzer.analyze_multiple_stocks(stocks, strategy="parallel")
```

## 📈 性能优化

### 缓存机制
- 智能缓存分析结果
- 可配置缓存时间
- 自动清理过期缓存

### 并发处理
- 多线程并行分析
- 可配置并发数
- 智能负载均衡

### 错误处理
- 自动重试机制
- 优雅降级策略
- 详细的错误日志

## 🧪 测试

运行测试套件：
```bash
python -m pytest tests/
```

运行特定测试：
```bash
python -m pytest tests/test_stock_analysis_system.py -v
```

## 📝 配置文件

### Agents配置 (`config/agents.yaml`)
定义各个Agent的角色、目标和背景故事。

### Tasks配置 (`config/tasks.yaml`)
定义各个任务的详细描述和预期输出。

### Tools配置 (`config/tools.yaml`)
配置各种分析工具和参数。

## 🔒 安全考虑

### API密钥管理
- 使用环境变量存储密钥
- 不在代码中硬编码密钥
- 定期轮换API密钥

### 数据安全
- 敏感数据加密存储
- 安全的文件权限
- 访问日志记录

## 🚨 注意事项

1. **API限制**: 注意OpenAI API的调用限制和费用
2. **数据准确性**: 系统基于公开数据，投资决策需谨慎
3. **免责声明**: 本系统仅供研究参考，不构成投资建议
4. **合规性**: 使用时需遵守相关法律法规

## 🤝 贡献

欢迎贡献代码和改进建议！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [CrewAI](https://github.com/joaomdmoura/crewAI) - 多Agent框架
- [OpenAI](https://openai.com/) - AI模型支持
- [yfinance](https://github.com/ranaroussi/yfinance) - 金融数据获取

## 📞 支持

如有问题或建议，请通过以下方式联系：

- 创建 Issue
- 发送邮件
- 查看文档

---

**免责声明**: 本系统提供的分析结果仅供参考，不构成投资建议。投资有风险，决策需谨慎。