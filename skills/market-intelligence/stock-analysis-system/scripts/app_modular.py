"""
股票分析API - 模块化版本
"""

import uvicorn
import logging
import pandas as pd
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from modules.config import API_CONFIG
from modules.models import StockAnalysisRequest, AnalysisResponse
from modules.stock_service import StockService
from modules.auth import AuthService

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title=API_CONFIG['title'],
    description=API_CONFIG['description'],
    version=API_CONFIG['version']
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
stock_service = StockService()
auth_service = AuthService()


@app.post("/analyze-stock/", response_model=AnalysisResponse)
async def analyze_stock(request: StockAnalysisRequest, auth_token: str = Depends(auth_service.verify_auth_token)):
    """
    分析股票技术指标
    
    Args:
        request: 股票分析请求
        auth_token: 认证token
        
    Returns:
        股票分析结果
    """
    try:
        logger.info(f"开始分析股票: {request.stock_code}, 市场类型: {request.market_type}")
        
        # 获取股票数据
        stock_data = stock_service.get_stock_data(
            request.stock_code,
            request.market_type,
            request.start_date,
            request.end_date
        )
        
        logger.info(f"成功获取股票数据，共 {len(stock_data)} 条记录")
        
        # 计算技术指标
        stock_data = stock_service.calculate_indicators(stock_data)
        logger.info("技术指标计算完成")
        
        # 计算评分
        score = stock_service.calculate_score(stock_data)
        logger.info(f"评分计算完成: {score}")
        
        # 获取最新数据
        latest = stock_data.iloc[-1]
        prev = stock_data.iloc[-2]
        data_start = stock_data['date'].min()
        data_end = stock_data['date'].max()
        latest_data_date = pd.to_datetime(data_end).date()
        data_freshness_days = (datetime.now().date() - latest_data_date).days
        
        # 生成技术指标摘要
        technical_summary = {
            'trend': 'upward' if latest['MA5'] > latest['MA20'] else 'downward',
            'volatility': f"{latest['Volatility']:.2f}%" if not pd.isna(latest['Volatility']) else "N/A",
            'volume_trend': 'increasing' if latest['Volume_Ratio'] > 1 else 'decreasing',
            'rsi_level': round(latest['RSI'], 2) if not pd.isna(latest['RSI']) else None
        }
        
        # 生成分析报告
        report = {
            'stock_code': request.stock_code,
            'market_type': request.market_type,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'score': score,
            'price': round(latest['close'], 2),
            'price_change': round((latest['close'] - prev['close']) / prev['close'] * 100, 2),
            'ma_trend': 'UP' if latest['MA5'] > latest['MA20'] else 'DOWN',
            'rsi': round(latest['RSI'], 2) if not pd.isna(latest['RSI']) else None,
            'macd_signal': 'BUY' if latest['MACD'] > latest['Signal'] else 'SELL',
            'volume_status': 'HIGH' if latest['Volume_Ratio'] > 1.5 else 'NORMAL',
            'recommendation': stock_service.get_recommendation(score),
            'data_points': len(stock_data),
            'data_start_date': pd.to_datetime(data_start).strftime('%Y-%m-%d'),
            'data_end_date': pd.to_datetime(data_end).strftime('%Y-%m-%d'),
            'latest_data_date': latest_data_date.strftime('%Y-%m-%d'),
            'data_freshness_days': data_freshness_days,
            'data_source': stock_data.attrs.get('data_source', 'AKShare'),
            'data_quality_note': stock_data.attrs.get('data_quality_note')
        }
        
        # 获取近14天交易数据
        recent_data = stock_data.tail(14).to_dict('records')
        
        logger.info(f"分析完成，返回报告")
        
        # 返回结果
        return {
            "status": "success",
            "message": "股票分析完成",
            "technical_summary": technical_summary,
            "recent_data": recent_data,
            "report": report
        }
        
    except ValueError as e:
        # 用户输入错误
        logger.warning(f"用户输入错误: {str(e)}")
        raise HTTPException(status_code=400, detail=f"输入参数错误: {str(e)}")
    except Exception as e:
        # 系统错误
        error_msg = f"分析过程中发生错误: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/markets")
async def get_supported_markets():
    """
    获取支持的市场类型信息
    
    Returns:
        支持的市场类型列表
    """
    try:
        markets = {}
        for market_type in stock_service.get_supported_markets():
            markets[market_type] = stock_service.get_market_info(market_type)
        
        return {
            "status": "success",
            "message": "获取市场类型信息成功",
            "markets": markets
        }
    except Exception as e:
        logger.error(f"获取市场类型信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取市场类型信息失败: {str(e)}")


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "股票分析API",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """根端点"""
    return {
        "message": "欢迎使用股票分析API",
        "version": "1.0.0",
        "endpoints": {
            "analyze_stock": "/analyze-stock/",
            "markets": "/markets",
            "health_check": "/health",
            "docs": "/docs"
        }
    }


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 启动股票分析API服务 (模块化版本)")
    print("=" * 60)
    print(f"服务地址: http://{API_CONFIG['host']}:{API_CONFIG['port']}")
    print(f"API文档: http://{API_CONFIG['host']}:{API_CONFIG['port']}/docs")
    print(f"健康检查: http://{API_CONFIG['host']}:{API_CONFIG['port']}/health")
    print(f"支持市场: A股(沪深), HK(港股), US(美股), ETF, LOF")
    print("=" * 60)

    try:
        uvicorn.run(
            app, 
            host=API_CONFIG['host'], 
            port=API_CONFIG['port'], 
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        logger.error(f"服务启动失败: {e}")
