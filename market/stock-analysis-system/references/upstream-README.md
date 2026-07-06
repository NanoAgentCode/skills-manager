# 股票分析系统 (Stock Analysis System)

一个基于Python的股票数据分析系统，支持A股、港股、美股等多个市场的技术分析和投资建议。

## 🚀 功能特性

### 支持的市场
- **A股市场** (沪深交易所)
- **港股市场** (香港交易所)
- **美股市场** (NYSE、NASDAQ、AMEX)
- **ETF基金**
- **LOF基金**

### 技术分析指标
- **移动平均线**: MA5、MA20、MA60
- **RSI指标**: 相对强弱指数
- **MACD指标**: 指数平滑移动平均线
- **布林带**: 价格通道分析
- **成交量分析**: 成交量比率、成交量移动平均
- **波动率指标**: ATR、价格波动率
- **动量指标**: ROC变化率

### 智能评分系统
- 综合技术指标评分 (0-100分)
- 自动投资建议生成
- 数据质量验证

## 📋 系统要求

- Python 3.8+
- Windows 10/11 (已测试)
- 网络连接 (用于获取实时股票数据)

## 🛠️ 安装说明

### 1. 克隆项目
```bash
git clone <repository-url>
cd stock
```

### 2. 创建虚拟环境
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置环境变量
复制 `config.env.example` 为 `config.env` 并配置：
```bash
cp config.env.example config.env
```

编辑 `config.env` 文件，设置必要的API密钥：
```env
TUSHARE_TOKEN=your_tushare_token_here
```

## 🚀 使用方法

### 启动服务
```bash
python app_modular.py
```

服务将在 `http://localhost:8000` 启动

### API接口

#### 1. 股票分析接口
```http
POST /analyze-stock/
Authorization: Bearer xue123
Content-Type: application/json

{
    "stock_code": "AAPL",
    "market_type": "US",
    "start_date": "20240101",
    "end_date": "20241201"
}
```

#### 2. 市场状态查询
```http
GET /markets
```

#### 3. 健康检查
```http
GET /health
```

### 测试脚本

#### 测试美股功能
```bash
python test_us_markets.py
```

#### 测试市场功能
```bash
python test_markets.py
```

## 📊 数据源

- **A股数据**: AKShare (东方财富)
- **港股数据**: Tushare Pro (优先) + AKShare (备用)
- **美股数据**: AKShare 海外市场接口
- **ETF/LOF数据**: AKShare 基金接口

## 🔧 配置说明

### 市场配置
- 支持自定义市场类型和参数
- 可配置数据质量要求
- 支持时区设置

### 技术指标参数
- 移动平均线周期: 5、20、60
- RSI周期: 14
- 布林带参数: 20周期，2倍标准差
- 成交量分析: 20周期移动平均

## 📈 使用示例

### 分析苹果股票
```python
import requests

url = "http://localhost:8000/analyze-stock/"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer xue123"
}

data = {
    "stock_code": "AAPL",
    "market_type": "US",
    "start_date": "20240101",
    "end_date": "20241201"
}

response = requests.post(url, headers=headers, json=data)
result = response.json()
print(f"综合评分: {result['report']['score']}")
print(f"投资建议: {result['report']['recommendation']}")
```

## 🐛 故障排除

### 常见问题

1. **美股数据获取失败**
   - 检查网络连接
   - 验证股票代码格式
   - 确认数据源服务状态

2. **港股数据获取失败**
   - 检查Tushare Token配置
   - 验证港股代码格式 (4位数字)
   - 确认市场交易时间

3. **服务启动失败**
   - 检查端口占用情况
   - 验证依赖库安装
   - 检查环境变量配置

### 日志查看
服务运行时会输出详细的日志信息，包括：
- 数据获取过程
- 技术指标计算
- 错误和警告信息

## 📝 开发说明

### 项目结构
```
stock/
├── main_back.py          # 主服务文件
├── app_modular.py        # 模块化应用
├── modules/              # 功能模块
│   ├── auth.py          # 认证模块
│   ├── config.py        # 配置管理
│   ├── global_markets.py # 全球市场服务
│   ├── indicators.py    # 技术指标计算
│   ├── models.py        # 数据模型
│   └── stock_service.py # 股票服务
├── test_markets.py      # 市场测试
├── test_us_markets.py   # 美股测试
└── config.env           # 环境配置
```

### 扩展开发
- 添加新的技术指标
- 支持更多市场类型
- 集成其他数据源
- 优化算法性能

## 📄 许可证

本项目采用 MIT 许可证

## 🤝 贡献

欢迎提交 Issue 和 Pull Request

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 GitHub Issue
- 发送邮件至项目维护者

---

**注意**: 本系统仅供学习和研究使用，不构成投资建议。投资有风险，入市需谨慎。
