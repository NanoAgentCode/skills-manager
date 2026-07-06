"""
配置文件 - 包含所有系统配置参数
"""

# 技术指标参数配置
TECHNICAL_PARAMS = {
    'ma_periods': {'short': 5, 'medium': 20, 'long': 60},
    'rsi_period': 14,
    'bollinger_period': 20,
    'bollinger_std': 2,
    'volume_ma_period': 20,
    'atr_period': 14
}

# 市场类型配置
MARKET_TYPES = {
    'A': {
        'name': '沪深A股',
        'code_length': 6,
        'valid_prefixes': ['0', '3', '6', '688', '8'],
        'description': '中国大陆沪深交易所股票',
        'data_source': 'akshare',
        'currency': 'CNY'
    },
    'HK': {
        'name': '港股',
        'code_length': 4,
        'valid_prefixes': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
        'description': '香港交易所股票',
        'data_source': 'akshare',
        'currency': 'HKD'
    },
    'US': {
        'name': '美股',
        'code_length': None,  # 美股代码长度不固定
        'valid_prefixes': None,  # 美股代码格式多样
        'description': '美国证券交易所股票',
        'data_source': 'akshare_overseas',
        'currency': 'USD'
    },
    'ETF': {
        'name': 'ETF基金',
        'code_length': 6,
        'valid_prefixes': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
        'description': '交易所交易基金',
        'data_source': 'akshare',
        'currency': 'CNY'
    },
    'LOF': {
        'name': 'LOF基金',
        'code_length': 6,
        'valid_prefixes': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
        'description': '上市型开放式基金',
        'data_source': 'akshare',
        'currency': 'CNY'
    }
}

# 数据源配置
DATA_SOURCES = {
    'akshare': {
        'name': 'AKShare',
        'description': '开源金融数据接口包',
        'enabled': True,
        'priority': 1
    },
    'akshare_overseas': {
        'name': 'AKShare海外市场',
        'description': 'AKShare海外股票数据接口',
        'enabled': True,
        'priority': 1
    },
    'tushare': {
        'name': 'Tushare Pro',
        'description': '专业金融数据接口',
        'enabled': False,
        'priority': 3,
        'api_key_required': True,
        'api_key': None
    }
}

# 评分权重配置
SCORE_WEIGHTS = {
    'ma_trend': 30,      # 均线趋势权重
    'rsi': 20,           # RSI指标权重
    'macd': 20,          # MACD指标权重
    'volume': 30         # 成交量权重
}

# 推荐等级配置
RECOMMENDATION_LEVELS = {
    80: '强烈推荐买入',
    60: '建议买入',
    40: '观望',
    20: '建议卖出',
    0: '强烈建议卖出'
}

# 默认时间配置
DEFAULT_TIME_CONFIG = {
    'default_days': 365,  # 默认分析天数
    'min_data_points': 60  # 最少需要的数据点
}

# 验证Token配置
VALID_TOKENS = ["xue123", "xue1234"]

# API配置
API_CONFIG = {
    'title': "股票分析API",
    'description': "基于技术指标的股票分析服务，支持A股、港股、美股",
    'version': "1.0.0",
    'host': "0.0.0.0",
    'port': 8000
}

# 港股配置
HK_CONFIG = {
    'exchange': 'HKEX',
    'market_hours': {
        'open': '09:30',
        'close': '16:00',
        'timezone': 'Asia/Hong_Kong'
    },
    'trading_days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
}

# 数据质量配置
DATA_QUALITY_CONFIG = {
    'min_data_points': 60,
    'max_missing_ratio': 0.1,  # 最大缺失数据比例
    'data_validation': {
        'price_range_check': True,
        'volume_anomaly_check': True,
        'date_continuity_check': True
    }
}
