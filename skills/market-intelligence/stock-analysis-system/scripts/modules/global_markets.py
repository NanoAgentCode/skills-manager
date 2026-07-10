"""
全球市场股票分析模块
专门处理港股的特殊逻辑
"""

import pandas as pd
# import tushare as ts  # Tushare功能已禁用
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging
import numpy as np
from .config import HK_CONFIG, DATA_QUALITY_CONFIG

# 美股配置
US_CONFIG = {
    'exchanges': ['NYSE', 'NASDAQ', 'AMEX'],
    'market_hours': {
        'open': '09:30',
        'close': '16:00',
        'timezone': 'America/New_York'
    },
    'trading_days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
    'pre_market': {
        'open': '04:00',
        'close': '09:30'
    },
    'after_hours': {
        'open': '16:00',
        'close': '20:00'
    }
}

# 数据质量配置

logger = logging.getLogger(__name__)

class GlobalMarketsService:
    """全球市场服务类"""
    
    def __init__(self):
        self.pro = None
        logger.info("Tushare功能已禁用，将使用备用数据源")
    
    def get_hk_stock_list(self, limit: int = 100) -> List[Dict]:
        """获取港股列表"""
        # 返回一些常见的港股代码
        common_hk_stocks = [
            {'code': '0700', 'name': '腾讯控股', 'industry': '科技', 'market': 'HKEX'},
            {'code': '0941', 'name': '中国移动', 'industry': '电信', 'market': 'HKEX'},
            {'code': '0005', 'name': '汇丰控股', 'industry': '金融', 'market': 'HKEX'},
            {'code': '1299', 'name': '友邦保险', 'industry': '保险', 'market': 'HKEX'},
            {'code': '2318', 'name': '中国平安', 'industry': '保险', 'market': 'HKEX'}
        ]
        return common_hk_stocks[:limit]
    
    def get_us_stock_list(self, limit: int = 100) -> List[Dict]:
        """获取美股列表"""
        try:
            # 返回一些常见的美股代码
            common_us_stocks = [
                {'code': 'AAPL', 'name': 'Apple Inc.', 'industry': 'Technology', 'market': 'NASDAQ'},
                {'code': 'MSFT', 'name': 'Microsoft Corporation', 'industry': 'Technology', 'market': 'NASDAQ'},
                {'code': 'GOOGL', 'name': 'Alphabet Inc.', 'industry': 'Technology', 'market': 'NASDAQ'},
                {'code': 'AMZN', 'name': 'Amazon.com Inc.', 'industry': 'Consumer Cyclical', 'market': 'NASDAQ'},
                {'code': 'TSLA', 'name': 'Tesla Inc.', 'industry': 'Automotive', 'market': 'NASDAQ'},
                {'code': 'META', 'name': 'Meta Platforms Inc.', 'industry': 'Technology', 'market': 'NASDAQ'},
                {'code': 'NVDA', 'name': 'NVIDIA Corporation', 'industry': 'Technology', 'market': 'NASDAQ'},
                {'code': 'BRK-A', 'name': 'Berkshire Hathaway Inc.', 'industry': 'Financial Services', 'market': 'NYSE'},
                {'code': 'JNJ', 'name': 'Johnson & Johnson', 'industry': 'Healthcare', 'market': 'NYSE'},
                {'code': 'V', 'name': 'Visa Inc.', 'industry': 'Financial Services', 'market': 'NYSE'}
            ]
            return common_us_stocks[:limit]
        except Exception as e:
            logger.error(f"获取美股列表失败: {e}")
            return []
    
    def get_market_status(self, market_type: str) -> Dict:
        """获取市场状态"""
        now = datetime.now()
        
        if market_type == 'HK':
            # 港股市场状态（简化版）
            hk_time = now.replace(tzinfo=None)  # 简化时区处理
            is_weekday = now.weekday() < 5
            is_market_hours = is_weekday and 9 <= hk_time.hour < 16
            
            return {
                'market': 'HKEX',
                'status': 'OPEN' if is_market_hours else 'CLOSED',
                'current_time': now.strftime('%Y-%m-%d %H:%M:%S'),
                'trading_hours': HK_CONFIG['market_hours'],
                'next_trading_day': self._get_next_trading_day(now, HK_CONFIG['trading_days'])
            }
        elif market_type == 'US':
            # 美股市场状态（简化版）
            us_time = now.replace(tzinfo=None)  # 简化时区处理
            is_weekday = now.weekday() < 5
            is_market_hours = is_weekday and 9 <= us_time.hour < 16
            
            return {
                'market': 'NYSE/NASDAQ',
                'status': 'OPEN' if is_market_hours else 'CLOSED',
                'current_time': now.strftime('%Y-%m-%d %H:%M:%S'),
                'trading_hours': US_CONFIG['market_hours'],
                'pre_market': US_CONFIG['pre_market'],
                'after_hours': US_CONFIG['after_hours'],
                'next_trading_day': self._get_next_trading_day(now, US_CONFIG['trading_days'])
            }
        else:
            return {
                'error': f'不支持的市场类型: {market_type}'
            }
    
    def _get_next_trading_day(self, current_date: datetime, trading_days: List[str]) -> str:
        """获取下一个交易日"""
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        current_weekday = day_names[current_date.weekday()]
        
        if current_weekday in trading_days:
            # 当前是交易日，返回下一个交易日
            next_date = current_date + timedelta(days=1)
            while next_date.weekday() >= 5:  # 跳过周末
                next_date += timedelta(days=1)
        else:
            # 当前不是交易日，找到下一个交易日
            next_date = current_date
            while next_date.weekday() >= 5:  # 跳过周末
                next_date += timedelta(days=1)
        
        return next_date.strftime('%Y-%m-%d')
    
    def get_currency_info(self, market_type: str) -> Dict:
        """获取货币信息"""
        currency_info = {
            'CNY': {
                'name': '人民币',
                'symbol': '¥',
                'exchange_rate': 1.0
            },
            'HKD': {
                'name': '港币',
                'symbol': 'HK$',
                'exchange_rate': 0.88  # 简化的汇率
            },
            'USD': {
                'name': '美元',
                'symbol': '$',
                'exchange_rate': 0.14  # 简化的汇率
            }
        }
        
        if market_type == 'HK':
            return currency_info['HKD']
        elif market_type == 'US':
            return currency_info['USD']
        else:
            return currency_info['CNY']
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict:
        """验证数据质量"""
        if df.empty:
            return {
                'quality_score': 0,
                'issues': ['数据为空'],
                'recommendation': '数据质量极差，建议重新获取'
            }
        
        issues = []
        score = 100
        
        # 检查数据点数量
        if len(df) < DATA_QUALITY_CONFIG['min_data_points']:
            issues.append(f'数据点不足，当前{len(df)}个，需要至少{DATA_QUALITY_CONFIG["min_data_points"]}个')
            score -= 30
        
        # 检查缺失值
        missing_ratio = df.isnull().sum().sum() / (len(df) * len(df.columns))
        if missing_ratio > DATA_QUALITY_CONFIG['max_missing_ratio']:
            issues.append(f'缺失数据过多，缺失率{missing_ratio:.2%}')
            score -= 20
        
        # 检查价格异常
        if DATA_QUALITY_CONFIG['data_validation']['price_range_check']:
            for col in ['open', 'close', 'high', 'low']:
                if col in df.columns:
                    if (df[col] <= 0).any():
                        issues.append(f'{col}列存在非正价格')
                        score -= 15
                        break
        
        # 检查成交量异常
        if DATA_QUALITY_CONFIG['data_validation']['volume_anomaly_check']:
            if 'volume' in df.columns:
                if (df['volume'] < 0).any():
                    issues.append('成交量存在负值')
                    score -= 10
        
        # 生成建议
        if score >= 80:
            recommendation = '数据质量良好'
        elif score >= 60:
            recommendation = '数据质量一般，建议检查'
        elif score >= 40:
            recommendation = '数据质量较差，建议重新获取'
        else:
            recommendation = '数据质量极差，必须重新获取'
        
        return {
            'quality_score': max(0, score),
            'issues': issues,
            'recommendation': recommendation,
            'data_points': len(df),
            'missing_ratio': missing_ratio
        }
    
    def get_market_summary(self, market_type: str) -> Dict:
        """获取市场摘要信息"""
        if market_type == 'HK':
            return {
                'market_name': '香港交易所 (HKEX)',
                'description': '亚洲主要金融中心，提供股票、债券、衍生品等交易',
                'trading_hours': '09:30-16:00 (GMT+8)',
                'currency': '港币 (HKD)',
                'timezone': 'Asia/Hong_Kong',
                'website': 'https://www.hkex.com.hk'
            }
        elif market_type == 'US':
            return {
                'market_name': '美国证券交易所',
                'description': '全球最大的股票市场，包括NYSE、NASDAQ等主要交易所',
                'trading_hours': '09:30-16:00 (EST)',
                'currency': '美元 (USD)',
                'timezone': 'America/New_York',
                'website': 'https://www.nyse.com'
            }
        else:
            return {
                'error': f'不支持的市场类型: {market_type}'
            }
