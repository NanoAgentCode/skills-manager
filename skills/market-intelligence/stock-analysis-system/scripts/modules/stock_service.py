"""
股票数据获取和分析服务
"""

import pandas as pd
import akshare as ak
# import tushare as ts  # Tushare功能已禁用
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
import numpy as np
import time

from .config import MARKET_TYPES, DEFAULT_TIME_CONFIG, TECHNICAL_PARAMS
from .indicators import (
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_atr, calculate_roc, calculate_volume_ratio, calculate_volatility
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockService:
    """股票服务类"""
    
    def __init__(self):
        self.min_data_points = DEFAULT_TIME_CONFIG['min_data_points']
        self.params = TECHNICAL_PARAMS
        
        # Tushare Pro功能已禁用
        self.pro = None
        logger.info("Tushare Pro功能已禁用，将使用其他数据源")
    
    def get_stock_data(self, stock_code: str, market_type: str = 'A', 
                       start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取股票基础数据
        
        Args:
            stock_code: 股票代码
            market_type: 市场类型 (A: A股, HK: 港股, ETF: ETF基金, LOF: LOF基金)
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            股票数据DataFrame
        """
        logger.info(f"获取股票数据: {stock_code}, 市场类型: {market_type}")
        
        # 设置默认日期
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=DEFAULT_TIME_CONFIG['default_days'])).strftime('%Y%m%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
            
        try:
            # 验证股票代码
            self._validate_stock_code(stock_code, market_type)
            
            # 根据市场类型获取数据
            df = self._fetch_data_by_market(stock_code, market_type, start_date, end_date)
            
            # 数据预处理
            df = self._preprocess_data(df, market_type)
            df.attrs.setdefault('data_source', f'AKShare {market_type} OHLCV')
            df.attrs.setdefault('data_quality_note', None)
            
            # 验证数据完整性
            self._validate_data_integrity(df)
            
            return df.sort_values('date')
            
        except Exception as e:
            logger.error(f"获取股票数据失败: {str(e)}")
            raise Exception(f"获取数据失败: {str(e)}")
    
    def _validate_stock_code(self, stock_code: str, market_type: str):
        """验证股票代码格式"""
        market_config = MARKET_TYPES.get(market_type)
        if not market_config:
            raise ValueError(f"不支持的市场类型: {market_type}")
        
        stock_code = str(stock_code).strip()
        
        # 检查长度
        if market_config['code_length'] and len(stock_code) != market_config['code_length']:
            raise ValueError(f"{market_config['name']}代码长度必须为{market_config['code_length']}位，当前为{len(stock_code)}位: {stock_code}")
        
        # 检查前缀（仅对A股和ETF/LOF）
        if market_type in ['A', 'ETF', 'LOF'] and market_config['valid_prefixes']:
            valid_prefix = False
            for prefix in market_config['valid_prefixes']:
                if stock_code.startswith(prefix):
                    valid_prefix = True
                    break
            
            if not valid_prefix:
                raise ValueError(f"无效的{market_config['name']}代码格式: {stock_code}")
        
        # 检查是否为数字（港股、ETF、LOF）
        if market_type in ['HK', 'ETF', 'LOF']:
            if not stock_code.isdigit():
                raise ValueError(f"{market_config['name']}代码必须全为数字: {stock_code}")
    
    def _fetch_data_by_market(self, stock_code: str, market_type: str, 
                              start_date: str, end_date: str) -> pd.DataFrame:
        """根据市场类型获取数据"""
        try:
            if market_type == 'A':
                df = self._fetch_a_stock_data(stock_code, start_date, end_date)
            elif market_type == 'HK':
                df = self._fetch_hk_stock_data(stock_code, start_date, end_date)
            elif market_type == 'US':
                df = self._fetch_us_stock_data(stock_code, start_date, end_date)
            elif market_type == 'ETF':
                df = self._fetch_etf_data(stock_code, start_date, end_date)
            elif market_type == 'LOF':
                df = self._fetch_lof_data(stock_code, start_date, end_date)
            else:
                raise ValueError(f"不支持的市场类型: {market_type}")
            
            return df
            
        except Exception as e:
            logger.error(f"从{MARKET_TYPES[market_type]['name']}获取数据失败: {str(e)}")
            raise Exception(f"从{MARKET_TYPES[market_type]['name']}获取数据失败: {str(e)}")

    def _fetch_a_stock_data(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取A股数据，东方财富接口失败时回退到日线接口"""
        try:
            return ak.stock_zh_a_hist(
                symbol=stock_code,
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )
        except Exception as e:
            logger.error(f"AKShare获取A股K线数据失败: {e}")
            logger.info(f"尝试使用AKShare备用日线接口获取A股数据 {stock_code}")

            try:
                if stock_code.startswith('6'):
                    daily_symbol = f"sh{stock_code}"
                elif stock_code.startswith('8'):
                    daily_symbol = f"bj{stock_code}"
                else:
                    daily_symbol = f"sz{stock_code}"

                df = ak.stock_zh_a_daily(
                    symbol=daily_symbol,
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq"
                )

                if df is None or df.empty:
                    raise Exception("备用日线接口未获取到A股数据")

                logger.info(f"AKShare备用日线接口成功获取A股数据 {stock_code}，共 {len(df)} 条记录")
                return df
            except Exception as backup_error:
                logger.error(f"A股备用日线接口也失败: {backup_error}")
                raise Exception(f"无法获取A股数据 {stock_code}: {e}")
    
    def _fetch_hk_stock_data(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取港股数据，使用AKShare接口"""
        # 港股代码需要5位数字格式
        if len(stock_code) == 4:
            stock_code = '0' + stock_code  # 补零到5位
        
        try:
            logger.info(f"使用AKShare获取港股数据 {stock_code}")
            
            # 转换日期格式
            start_dt = datetime.strptime(start_date, '%Y%m%d').strftime('%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y%m%d').strftime('%Y-%m-%d')
            
            df = ak.stock_hk_hist(
                symbol=stock_code, 
                period='daily', 
                start_date=start_dt, 
                end_date=end_dt, 
                adjust='qfq'
            )
            
            if not df.empty:
                logger.info(f"AKShare成功获取港股数据 {stock_code}，共 {len(df)} 条记录")
                return df
            else:
                raise Exception("未获取到港股数据")
                
        except Exception as e:
            logger.error(f"AKShare获取港股数据失败: {e}")
            logger.info(f"尝试使用AKShare备用接口获取港股数据 {stock_code}")
            try:
                df = ak.stock_hk_daily(symbol=stock_code, adjust='qfq')

                if df is None or df.empty:
                    raise Exception("备用接口未获取到港股数据")

                df['date'] = pd.to_datetime(df['date'])
                start_dt = datetime.strptime(start_date, '%Y%m%d')
                end_dt = datetime.strptime(end_date, '%Y%m%d')
                df = df[(df['date'] >= start_dt) & (df['date'] <= end_dt)]

                if df.empty:
                    raise Exception("备用接口日期范围内无港股数据")

                logger.info(f"AKShare备用接口成功获取港股数据 {stock_code}，共 {len(df)} 条记录")
                return df
            except Exception as backup_error:
                logger.error(f"AKShare港股备用接口也失败: {backup_error}")
                raise Exception(f"无法获取港股数据 {stock_code}: {e}")

    def _fetch_lof_data(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取LOF基金数据，K线接口失败时回退到净值走势"""
        try:
            return ak.fund_lof_hist_em(
                symbol=stock_code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )
        except Exception as e:
            logger.error(f"AKShare获取LOF K线数据失败: {e}")
            logger.info(f"尝试使用开放基金净值走势接口获取LOF数据 {stock_code}")

            try:
                return self._fetch_fund_nav_data(stock_code, start_date, end_date)
            except Exception as backup_error:
                logger.error(f"LOF净值走势备用接口也失败: {backup_error}")
                raise Exception(f"无法获取LOF基金数据 {stock_code}: {e}")

    def _fetch_etf_data(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取ETF基金数据，K线接口失败时回退到净值走势"""
        try:
            return ak.fund_etf_hist_em(
                symbol=stock_code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )
        except Exception as e:
            logger.error(f"AKShare获取ETF K线数据失败: {e}")
            logger.info(f"尝试使用开放基金净值走势接口获取ETF数据 {stock_code}")

            try:
                return self._fetch_fund_nav_data(stock_code, start_date, end_date)
            except Exception as backup_error:
                logger.error(f"ETF净值走势备用接口也失败: {backup_error}")
                raise Exception(f"无法获取ETF基金数据 {stock_code}: {e}")

    def _fetch_fund_nav_data(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取基金净值走势，并映射为指标计算需要的OHLC结构"""
        df = ak.fund_open_fund_info_em(symbol=stock_code, indicator='单位净值走势')

        if df is None or df.empty:
            raise Exception("净值走势接口未获取到基金数据")

        df = df.rename(columns={
            '净值日期': 'date',
            '单位净值': 'close'
        })
        df['date'] = pd.to_datetime(df['date'])
        df['close'] = pd.to_numeric(df['close'], errors='coerce')

        start_dt = datetime.strptime(start_date, '%Y%m%d')
        end_dt = datetime.strptime(end_date, '%Y%m%d')
        df = df[(df['date'] >= start_dt) & (df['date'] <= end_dt)]
        df = df.dropna(subset=['date', 'close'])

        if df.empty:
            raise Exception("净值走势接口日期范围内无基金数据")

        df['open'] = df['close']
        df['high'] = df['close']
        df['low'] = df['close']
        df['volume'] = 0
        df.attrs['data_source'] = 'AKShare open-fund NAV fallback'
        df.attrs['data_quality_note'] = 'Fund NAV was mapped to OHLC; volume is synthetic zero and volume-based signals are not comparable.'

        logger.info(f"净值走势接口成功获取基金数据 {stock_code}，共 {len(df)} 条记录")
        return df[['date', 'open', 'close', 'high', 'low', 'volume']]
    
    def _fetch_us_stock_data(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取美股数据，使用AKShare海外市场接口"""
        try:
            logger.info(f"使用AKShare海外市场接口获取美股数据 {stock_code}")
            
            # 转换日期格式
            start_dt = datetime.strptime(start_date, '%Y%m%d').strftime('%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y%m%d').strftime('%Y-%m-%d')
            
            # 使用AKShare海外市场接口
            df = ak.stock_us_hist(
                symbol=stock_code,
                start_date=start_dt,
                end_date=end_dt,
                adjust="qfq"
            )
            
            # 检查返回的数据是否为None
            if df is None:
                logger.warning(f"AKShare返回None，尝试备用接口")
                raise Exception("主要接口返回None")
            
            if not df.empty:
                logger.info(f"AKShare成功获取美股数据 {stock_code}，共 {len(df)} 条记录")
                
                # 确保列名标准化
                if '日期' in df.columns:
                    df = df.rename(columns={'日期': 'date'})
                if '开盘' in df.columns:
                    df = df.rename(columns={'开盘': 'open'})
                if '收盘' in df.columns:
                    df = df.rename(columns={'收盘': 'close'})
                if '最高' in df.columns:
                    df = df.rename(columns={'最高': 'high'})
                if '最低' in df.columns:
                    df = df.rename(columns={'最低': 'low'})
                if '成交量' in df.columns:
                    df = df.rename(columns={'成交量': 'volume'})
                
                return df
            else:
                raise Exception("未获取到美股数据")
                
        except Exception as e:
            logger.error(f"AKShare获取美股数据失败: {e}")
            
            # 尝试使用备用接口：stock_us_daily
            try:
                logger.info(f"尝试使用AKShare备用接口获取美股数据 {stock_code}")
                df = ak.stock_us_daily(symbol=stock_code)
                
                # 检查返回的数据是否为None
                if df is None:
                    logger.error("备用接口也返回None")
                    raise Exception("备用接口返回None")
                
                if not df.empty:
                    # 过滤日期范围
                    df['date'] = pd.to_datetime(df['date'])
                    start_dt = datetime.strptime(start_date, '%Y%m%d')
                    end_dt = datetime.strptime(end_date, '%Y%m%d')
                    
                    df = df[(df['date'] >= start_dt) & (df['date'] <= end_dt)]
                    
                    if not df.empty:
                        logger.info(f"AKShare备用接口成功获取美股数据 {stock_code}，共 {len(df)} 条记录")
                        return df
                
                raise Exception("备用接口也未获取到数据")
                
            except Exception as backup_error:
                logger.error(f"AKShare备用接口也失败: {backup_error}")
                raise Exception(f"所有美股数据源都失败，无法获取 {stock_code} 的数据")
    
    def _preprocess_data(self, df: pd.DataFrame, market_type: str) -> pd.DataFrame:
        """数据预处理"""
        # 重命名列
        column_mapping = {
            "日期": "date",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume"
        }
        
        # 只重命名存在的列
        existing_columns = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(columns=existing_columns)
        
        # 确保date列是datetime类型
        if 'date' in df.columns:
            if df['date'].dtype == 'object':
                df['date'] = pd.to_datetime(df['date'])
        
        # 数据类型转换
        numeric_columns = ['open', 'close', 'high', 'low', 'volume']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 删除空值
        df = df.dropna()
        
        # 港股特殊处理
        if market_type == 'HK':
            # 确保数据按日期排序
            df = df.sort_values('date')
            # 移除重复日期
            df = df.drop_duplicates(subset=['date'])
        
        # 美股特殊处理
        if market_type == 'US':
            # 确保数据按日期排序
            df = df.sort_values('date')
            # 移除重复日期
            df = df.drop_duplicates(subset=['date'])
            # 美股数据可能有不同的列名格式，统一处理
            if 'Date' in df.columns:
                df = df.rename(columns={'Date': 'date'})
            if 'Open' in df.columns:
                df = df.rename(columns={'Open': 'open'})
            if 'Close' in df.columns:
                df = df.rename(columns={'Close': 'close'})
            if 'High' in df.columns:
                df = df.rename(columns={'High': 'high'})
            if 'Low' in df.columns:
                df = df.rename(columns={'Low': 'low'})
            if 'Volume' in df.columns:
                df = df.rename(columns={'Volume': 'volume'})
        
        return df
    
    def _validate_data_integrity(self, df: pd.DataFrame):
        """验证数据完整性"""
        if df.empty:
            raise ValueError("未获取到股票数据，请检查股票代码是否正确")
        
        if len(df) < self.min_data_points:
            raise ValueError(f"数据不足，至少需要{self.min_data_points}个交易日数据，当前只有{len(df)}个交易日")
        
        required_columns = ['date', 'open', 'close', 'high', 'low', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"数据缺少必要列: {missing_columns}")
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算技术指标"""
        try:
            logger.info("开始计算技术指标")
            
            # 计算移动平均线
            df['MA5'] = df['close'].rolling(window=self.params['ma_periods']['short']).mean()
            df['MA20'] = df['close'].rolling(window=self.params['ma_periods']['medium']).mean()
            df['MA60'] = df['close'].rolling(window=self.params['ma_periods']['long']).mean()
            
            # 计算RSI
            df['RSI'] = calculate_rsi(df['close'], self.params['rsi_period'])
            
            # 计算MACD
            df['MACD'], df['Signal'], df['MACD_hist'] = calculate_macd(df['close'])
            
            # 计算布林带
            df['BB_upper'], df['BB_middle'], df['BB_lower'] = calculate_bollinger_bands(
                df['close'],
                self.params['bollinger_period'],
                self.params['bollinger_std']
            )
            
            # 计算成交量指标
            df['Volume_MA'] = df['volume'].rolling(window=self.params['volume_ma_period']).mean()
            df['Volume_Ratio'] = calculate_volume_ratio(df['volume'], self.params['volume_ma_period'])
            
            # 计算波动率指标
            df['ATR'] = calculate_atr(df, self.params['atr_period'])
            df['Volatility'] = calculate_volatility(df['ATR'], df['close'])
            
            # 计算动量指标
            df['ROC'] = calculate_roc(df['close'], period=10)
            
            logger.info("技术指标计算完成")
            return df
            
        except Exception as e:
            logger.error(f"计算技术指标出错: {str(e)}")
            raise
    
    def calculate_score(self, df: pd.DataFrame) -> int:
        """计算综合评分"""
        try:
            score = 0
            latest = df.iloc[-1]
            
            # 均线得分 (30分)
            if latest['MA5'] > latest['MA20']:
                score += 15
            if latest['MA20'] > latest['MA60']:
                score += 15
            
            # RSI得分 (20分)
            if 30 <= latest['RSI'] <= 70:
                score += 20
            elif latest['RSI'] < 30:  # 超卖
                score += 15
            
            # MACD得分 (20分)
            if latest['MACD'] > latest['Signal']:
                score += 20
            
            # 成交量得分 (30分)
            if latest['Volume_Ratio'] > 1.5:
                score += 30
            elif latest['Volume_Ratio'] > 1:
                score += 15
            
            return score
            
        except Exception as e:
            logger.error(f"计算评分出错: {str(e)}")
            raise
    
    def get_recommendation(self, score: int) -> str:
        """根据得分给出建议"""
        if score >= 80:
            return '强烈推荐买入'
        elif score >= 60:
            return '建议买入'
        elif score >= 40:
            return '观望'
        elif score >= 20:
            return '建议卖出'
        else:
            return '强烈建议卖出'
    
    def get_market_info(self, market_type: str) -> dict:
        """获取市场信息"""
        return MARKET_TYPES.get(market_type, {})
    
    def get_supported_markets(self) -> list:
        """获取支持的市场类型"""
        return list(MARKET_TYPES.keys())
    
    def get_stock_info(self, stock_code: str, market_type: str) -> dict:
        """获取股票基本信息"""
        try:
            if market_type == 'HK':
                # 港股基本信息
                return {
                    'symbol': stock_code,
                    'name': f'港股{stock_code}',
                    'market': 'HKEX',
                    'currency': 'HKD'
                }
            elif market_type == 'US':
                # 美股基本信息
                return {
                    'symbol': stock_code,
                    'name': f'美股{stock_code}',
                    'market': 'NYSE/NASDAQ',
                    'currency': 'USD'
                }
            else:
                # A股基本信息
                return {
                    'symbol': stock_code,
                    'name': f'{MARKET_TYPES[market_type]["name"]}{stock_code}',
                    'market': 'SSE/SZSE',
                    'currency': 'CNY'
                }
        except Exception as e:
            logger.error(f"获取股票信息失败: {e}")
            return {
                'symbol': stock_code,
                'name': 'N/A',
                'error': str(e)
            }
