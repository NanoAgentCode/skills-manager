"""
股票数据模型定义
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class StockAnalysisRequest(BaseModel):
    """股票分析请求模型"""
    stock_code: str = Field(..., description="股票代码")
    market_type: str = Field(default='A', description="市场类型: A(沪深), HK(港股), US(美股), ETF, LOF")
    start_date: Optional[str] = Field(default=None, description="开始日期 (YYYYMMDD)")
    end_date: Optional[str] = Field(default=None, description="结束日期 (YYYYMMDD)")

    class Config:
        extra = "forbid"

    @validator('stock_code')
    def validate_stock_code(cls, v):
        if not v or not v.strip():
            raise ValueError("股票代码不能为空")
        return v.strip()

    @validator('market_type')
    def validate_market_type(cls, v):
        valid_types = ['A', 'HK', 'US', 'ETF', 'LOF']
        if v not in valid_types:
            raise ValueError(f"不支持的市场类型: {v}。支持的类型: {', '.join(valid_types)}")
        return v

    @validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        if v is None:
            return v
        try:
            datetime.strptime(v, '%Y%m%d')
        except ValueError as exc:
            raise ValueError("日期格式必须为 YYYYMMDD，例如 20260706") from exc
        return v


class TechnicalSummary(BaseModel):
    """技术指标摘要"""
    trend: str = Field(..., description="趋势方向: upward/downward")
    volatility: str = Field(..., description="波动率")
    volume_trend: str = Field(..., description="成交量趋势: increasing/decreasing")
    rsi_level: Optional[float] = Field(None, description="RSI水平")


class StockReport(BaseModel):
    """股票分析报告"""
    stock_code: str = Field(..., description="股票代码")
    market_type: str = Field(..., description="市场类型")
    analysis_date: str = Field(..., description="分析日期")
    score: int = Field(..., description="综合评分")
    price: float = Field(..., description="当前价格")
    price_change: float = Field(..., description="价格变化百分比")
    ma_trend: str = Field(..., description="均线趋势: UP/DOWN")
    rsi: Optional[float] = Field(None, description="RSI值")
    macd_signal: str = Field(..., description="MACD信号: BUY/SELL")
    volume_status: str = Field(..., description="成交量状态: HIGH/NORMAL")
    recommendation: str = Field(..., description="投资建议")
    data_points: int = Field(..., description="数据点数量")
    data_start_date: str = Field(..., description="实际数据开始日期")
    data_end_date: str = Field(..., description="实际数据结束日期")
    latest_data_date: str = Field(..., description="最新行情数据日期")
    data_freshness_days: int = Field(..., description="最新行情数据距分析日的天数")
    data_source: str = Field(..., description="实际行情来源或回退路径")
    data_quality_note: Optional[str] = Field(None, description="数据口径或回退限制")


class AnalysisResponse(BaseModel):
    """分析响应模型"""
    status: str = Field(..., description="响应状态")
    message: str = Field(..., description="响应消息")
    technical_summary: TechnicalSummary = Field(..., description="技术指标摘要")
    recent_data: List[Dict[str, Any]] = Field(..., description="近期交易数据")
    report: StockReport = Field(..., description="分析报告")
