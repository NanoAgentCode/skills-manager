"""
技术指标计算工具函数
"""

import pandas as pd
import numpy as np
from typing import Tuple


def calculate_ema(series: pd.Series, period: int) -> pd.Series:
    """
    计算指数移动平均线
    
    Args:
        series: 价格序列
        period: 周期
        
    Returns:
        指数移动平均线序列
    """
    return series.ewm(span=period, adjust=False).mean()


def calculate_rsi(series: pd.Series, period: int) -> pd.Series:
    """
    计算RSI指标
    
    Args:
        series: 价格序列
        period: 周期
        
    Returns:
        RSI指标序列
    """
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def calculate_macd(series: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    计算MACD指标
    
    Args:
        series: 价格序列
        
    Returns:
        (MACD线, 信号线, 柱状图)
    """
    exp1 = series.ewm(span=12, adjust=False).mean()
    exp2 = series.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal
    return macd, signal, hist


def calculate_bollinger_bands(series: pd.Series, period: int, std_dev: float) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    计算布林带
    
    Args:
        series: 价格序列
        period: 周期
        std_dev: 标准差倍数
        
    Returns:
        (上轨, 中轨, 下轨)
    """
    middle = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    return upper, middle, lower


def calculate_atr(df: pd.DataFrame, period: int) -> pd.Series:
    """
    计算ATR指标
    
    Args:
        df: 包含high, low, close的DataFrame
        period: 周期
        
    Returns:
        ATR指标序列
    """
    high = df['high']
    low = df['low']
    close = df['close'].shift(1)

    tr1 = high - low
    tr2 = abs(high - close)
    tr3 = abs(low - close)

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()


def calculate_roc(series: pd.Series, period: int = 10) -> pd.Series:
    """
    计算ROC动量指标
    
    Args:
        series: 价格序列
        period: 周期
        
    Returns:
        ROC指标序列
    """
    return series.pct_change(periods=period) * 100


def calculate_volume_ratio(volume: pd.Series, ma_period: int = 20) -> pd.Series:
    """
    计算成交量比率
    
    Args:
        volume: 成交量序列
        ma_period: 移动平均周期
        
    Returns:
        成交量比率序列
    """
    volume_ma = volume.rolling(window=ma_period).mean()
    return volume / volume_ma


def calculate_volatility(atr: pd.Series, close: pd.Series) -> pd.Series:
    """
    计算波动率
    
    Args:
        atr: ATR指标序列
        close: 收盘价序列
        
    Returns:
        波动率序列
    """
    return atr / close * 100
