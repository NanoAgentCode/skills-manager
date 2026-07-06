import json
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel

# 检查必要的依赖库
try:
    import pandas as pd
    import akshare as ak
except ImportError as e:
    raise ImportError(f"缺少必要的依赖库: {e}. 请运行: pip install pandas akshare")

# 验证 akshare 版本
try:
    ak_version = ak.__version__
    print(f"akshare 版本: {ak_version}")
except AttributeError:
    print("警告: 无法获取 akshare 版本信息")

app = FastAPI(title="股票分析API", description="基于技术指标的股票分析服务", version="1.0.0")

# 参数配置
params = {
    'ma_periods': {'short': 5, 'medium': 20, 'long': 60},
    'rsi_period': 14,
    'bollinger_period': 20,
    'bollinger_std': 2,
    'volume_ma_period': 20,
    'atr_period': 14
}


# Token 验证函数
def verify_auth_token(authorization: str = Header(None)):
    """
    验证Authorization Header中的Bearer Token
    """
    print(authorization)
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization scheme")
    # 这里可以添加真实的 Token 验证逻辑
    valid_tokens = ["xue123", "xue1234"]  # 示例有效 Token 列表
    if token not in valid_tokens:
        raise HTTPException(status_code=403, detail="Invalid or Expired Token")
    return token


class StockAnalysisRequest(BaseModel):
    stock_code: str
    market_type: str = 'A'
    start_date: str = None
    end_date: str = None

    class Config:
        # 允许额外字段
        extra = "forbid"

    def __init__(self, **data):
        super().__init__(**data)
        # 验证股票代码不能为空
        if not self.stock_code or not self.stock_code.strip():
            raise ValueError("股票代码不能为空")
        # 清理股票代码
        self.stock_code = self.stock_code.strip()


def calculate_score(df):
    """
    计算评分
    """
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
        print(f"计算技术指标出错: {str(e)}")
        raise


def _truncate_json_for_logging(json_obj, max_length=500):
    """截断JSON对象用于日志记录，避免日志过长"""
    json_str = json.dumps(json_obj, ensure_ascii=False)
    if len(json_str) <= max_length:
        return json_str
    return json_str[:max_length] + f"... [截断, 总长度: {len(json_str)}字符]"


def get_stock_data(stock_code, market_type='A', start_date=None, end_date=None):
    """获取股票基础数据"""
    print(f"get_stock_data 被调用，参数: stock_code='{stock_code}', market_type='{market_type}', start_date='{start_date}', end_date='{end_date}'")
    print(f"stock_code 类型: {type(stock_code)}, 长度: {len(stock_code) if stock_code else 0}")

    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
    if end_date is None:
        end_date = datetime.now().strftime('%Y%m%d')

    try:
        # 验证股票代码格式
        if market_type == 'A':
            # 清理股票代码，移除可能的空格和特殊字符
            stock_code = str(stock_code).strip()

            # 检查长度
            if len(stock_code) != 6:
                raise ValueError(f"股票代码长度必须为6位，当前为{len(stock_code)}位: {stock_code}")

            valid_prefixes = ['0', '3', '6', '688', '8']
            valid_format = False

            for prefix in valid_prefixes:
                if stock_code.startswith(prefix):
                    valid_format = True
                    break

            if not valid_format:
                error_msg = (
                    f"无效的A股股票代码格式: {stock_code}.\n"
                    "A股代码应以0、3、6、688或8开头。\n"
                    "示例: 000001, 300001, 600001, 688001, 800001"
                )
                raise ValueError(error_msg)

            # 检查是否全为数字
            if not stock_code.isdigit():
                raise ValueError(f"股票代码必须全为数字: {stock_code}")

            df = ak.stock_zh_a_hist(
                symbol=stock_code,
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )
        elif market_type == 'HK':
            # 港股代码验证
            if not stock_code.isdigit() or len(stock_code) != 4:
                raise ValueError(f"港股代码必须为4位数字: {stock_code}")

            df = ak.stock_hk_daily(
                symbol=stock_code,
                adjust="qfq"
            )
        elif market_type == 'US':
            # 美股代码验证（简单检查）
            if len(stock_code) < 1:
                raise ValueError(f"美股代码不能为空: {stock_code}")

            # 尝试获取美股数据，添加错误处理
            try:
                df = ak.stock_us_hist(
                    symbol=stock_code,
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq"
                )
                
                # 检查返回的数据
                if df is None or df.empty:
                    # 尝试备用接口
                    print(f"主要接口未获取到数据，尝试备用接口: {stock_code}")
                    df = ak.stock_us_daily(symbol=stock_code)
                    
                    if df is not None and not df.empty:
                        # 过滤日期范围
                        df['date'] = pd.to_datetime(df['date'])
                        start_dt = datetime.strptime(start_date, '%Y%m%d')
                        end_dt = datetime.strptime(end_date, '%Y%m%d')
                        
                        df = df[(df['date'] >= start_dt) & (df['date'] <= end_dt)]
                        
                        if df.empty:
                            raise ValueError(f"备用接口也未获取到指定日期范围的数据")
                    else:
                        raise ValueError(f"备用接口也未获取到数据")
                        
            except Exception as us_error:
                print(f"美股数据获取失败: {us_error}")
                # 提供更友好的错误信息
                if "NoneType" in str(us_error) or "subscriptable" in str(us_error):
                    raise ValueError(f"美股 {stock_code} 数据获取失败，可能的原因：\n1. 股票代码不正确（美股代码通常是4-5位字母，如AAPL、GOOGL）\n2. 网络连接问题\n3. AKShare接口暂时不可用")
                else:
                    raise ValueError(f"美股数据获取失败: {us_error}")
        elif market_type == 'ETF':
            # ETF代码验证
            if not stock_code.isdigit() or len(stock_code) != 6:
                raise ValueError(f"ETF代码必须为6位数字: {stock_code}")

            df = ak.fund_etf_hist_em(
                symbol=stock_code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )
        elif market_type == 'LOF':
            # LOF代码验证
            if not stock_code.isdigit() or len(stock_code) != 6:
                raise ValueError(f"LOF代码必须为6位数字: {stock_code}")

            df = ak.fund_lof_hist_em(
                symbol=stock_code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )
        else:
            raise ValueError(f"不支持的市场类型: {market_type}。支持的类型: A(沪深), HK(港股), US(美股), ETF, LOF")

        # 检查数据是否为空
        if df.empty:
            raise ValueError(f"未获取到股票 {stock_code} 的数据，请检查股票代码是否正确")

        # 重命名列以便后续分析计算
        df = df.rename(columns={
            "日期": "date",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume"
        })

        # 数据类型转换
        numeric_columns = ['open', 'close', 'high', 'low', 'volume']
        df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

        # 删除空值
        df = df.dropna()

        # 再次检查数据是否足够
        if len(df) < 60:  # 需要至少60个交易日数据来计算长期均线
            raise ValueError(f"数据不足，至少需要60个交易日数据，当前只有{len(df)}个交易日")

        return df.sort_values('date')

    except Exception as e:
        raise Exception(f"获取数据失败: {str(e)}")


def calculate_ema(series, period):
    """
    计算指数移动平均线
    """
    return series.ewm(span=period, adjust=False).mean()


def calculate_rsi(series, period):
    """
    计算RSI指标
    """
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def calculate_macd(series):
    """
    计算MACD指标
    """
    exp1 = series.ewm(span=12, adjust=False).mean()
    exp2 = series.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal
    return macd, signal, hist


def calculate_bollinger_bands(series, period, std_dev):
    """
    计算布林带
    """
    middle = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    return upper, middle, lower


def calculate_atr(df, period):
    """
    计算ATR指标
    """
    high = df['high']
    low = df['low']
    close = df['close'].shift(1)

    tr1 = high - low
    tr2 = abs(high - close)
    tr3 = abs(low - close)

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()


def get_recommendation(score):
    """
    根据得分给出建议
    """
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

def calculate_indicators(df):
    """计算技术指标"""
    try:
        # 计算移动平均线
        df['MA5'] = df['close'].rolling(window=params['ma_periods']['short']).mean()
        df['MA20'] = df['close'].rolling(window=params['ma_periods']['medium']).mean()
        df['MA60'] = df['close'].rolling(window=params['ma_periods']['long']).mean()

        # 计算RSI
        df['RSI'] = calculate_rsi(df['close'], params['rsi_period'])

        # 计算MACD
        df['MACD'], df['Signal'], df['MACD_hist'] = calculate_macd(df['close'])

        # 计算布林带
        df['BB_upper'], df['BB_middle'], df['BB_lower'] = calculate_bollinger_bands(
            df['close'],
            params['bollinger_period'],
            params['bollinger_std']
        )

        # 成交量分析
        df['Volume_MA'] = df['volume'].rolling(window=params['volume_ma_period']).mean()
        df['Volume_Ratio'] = df['volume'] / df['Volume_MA']

        # 计算ATR和波动率
        df['ATR'] = calculate_atr(df, params['atr_period'])
        df['Volatility'] = df['ATR'] / df['close'] * 100

        # 动量指标
        df['ROC'] = df['close'].pct_change(periods=10) * 100

        return df

    except Exception as e:
        print(f"计算技术指标出错: {str(e)}")
        raise


@app.post("/analyze-stock/")
async def analyze_stock(request: StockAnalysisRequest, auth_token: str = Depends(verify_auth_token)):
    try:
        print(f"开始分析股票: {request.stock_code}, 市场类型: {request.market_type}")
        print(f"请求体内容: {request.dict()}")
        print(f"股票代码类型: {type(request.stock_code)}, 长度: {len(request.stock_code) if request.stock_code else 0}")

        # 获取股票数据
        stock_data = get_stock_data(
            request.stock_code,
            request.market_type,
            request.start_date,
            request.end_date
        )

        print(f"成功获取股票数据，共 {len(stock_data)} 条记录")

        # 计算技术指标
        stock_data = calculate_indicators(stock_data)
        print("技术指标计算完成")

        # 计算评分
        score = calculate_score(stock_data)
        print(f"评分计算完成: {score}")

        # 获取最新数据
        latest = stock_data.iloc[-1]
        prev = stock_data.iloc[-2]

        # 生成技术指标摘要
        technical_summary = {
            'trend': 'upward' if latest['MA5'] > latest['MA20'] else 'downward',
            'volatility': f"{latest['Volatility']:.2f}%" if not pd.isna(latest['Volatility']) else "N/A",
            'volume_trend': 'increasing' if latest['Volume_Ratio'] > 1 else 'decreasing',
            'rsi_level': round(latest['RSI'], 2) if not pd.isna(latest['RSI']) else None
        }

        # 获取近14天交易数据
        recent_data = stock_data.tail(14).to_dict('records')

        # 生成报告
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
            'recommendation': get_recommendation(score),
            'data_points': len(stock_data)
        }

        print(f"分析完成，返回报告")

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
        print(f"用户输入错误: {str(e)}")
        raise HTTPException(status_code=400, detail=f"输入参数错误: {str(e)}")
    except Exception as e:
        # 系统错误
        error_msg = f"分析过程中发生错误: {str(e)}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


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
            "health_check": "/health",
            "docs": "/docs"
        }
    }

if __name__ == '__main__':
    import uvicorn
    print("=" * 50)
    print("🚀 启动股票分析API服务")
    print("=" * 50)
    print(f"服务地址: http://0.0.0.0:8000")
    print(f"API文档: http://0.0.0.0:8000/docs")
    print(f"健康检查: http://0.0.0.0:8000/health")
    print("=" * 50)

    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("\n🛑 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")