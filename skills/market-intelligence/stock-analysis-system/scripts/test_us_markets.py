#!/usr/bin/env python3
"""
测试美股数据获取功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import akshare as ak
    import pandas as pd
    from datetime import datetime, timedelta
    print(f"AKShare版本: {ak.__version__}")
except ImportError as e:
    print(f"导入错误: {e}")
    sys.exit(1)

def test_us_stock_data():
    """测试美股数据获取"""
    print("=" * 50)
    print("测试美股数据获取功能")
    print("=" * 50)
    
    # 测试正确的股票代码
    test_codes = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
    
    for code in test_codes:
        print(f"\n测试股票代码: {code}")
        try:
            # 测试主要接口
            print(f"  尝试主要接口: stock_us_hist")
            df = ak.stock_us_hist(
                symbol=code,
                start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                end_date=datetime.now().strftime('%Y-%m-%d'),
                adjust="qfq"
            )
            
            if df is not None and not df.empty:
                print(f"  ✓ 成功获取数据，共 {len(df)} 条记录")
                print(f"  列名: {list(df.columns)}")
                print(f"  最新价格: {df.iloc[-1]['收盘'] if '收盘' in df.columns else 'N/A'}")
            else:
                print(f"  ✗ 主要接口返回空数据")
                
        except Exception as e:
            print(f"  ✗ 主要接口失败: {e}")
            
            # 尝试备用接口
            try:
                print(f"  尝试备用接口: stock_us_daily")
                df = ak.stock_us_daily(symbol=code)
                
                if df is not None and not df.empty:
                    print(f"  ✓ 备用接口成功，共 {len(df)} 条记录")
                    print(f"  列名: {list(df.columns)}")
                    print(f"  最新价格: {df.iloc[-1]['close'] if 'close' in df.columns else 'N/A'}")
                else:
                    print(f"  ✗ 备用接口也返回空数据")
                    
            except Exception as backup_e:
                print(f"  ✗ 备用接口也失败: {backup_e}")
    
    # 测试错误的股票代码
    print(f"\n测试错误股票代码: APPL (应该是AAPL)")
    try:
        df = ak.stock_us_hist(
            symbol='APPL',
            start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            end_date=datetime.now().strftime('%Y-%m-%d'),
            adjust="qfq"
        )
        
        if df is not None and not df.empty:
            print(f"  ✓ 意外成功获取APPL数据，共 {len(df)} 条记录")
        else:
            print(f"  ✗ APPL返回空数据")
            
    except Exception as e:
        print(f"  ✗ APPL获取失败: {e}")

def test_akshare_availability():
    """测试AKShare可用性"""
    print("\n" + "=" * 50)
    print("测试AKShare基本功能")
    print("=" * 50)
    
    try:
        # 测试A股数据获取
        print("测试A股数据获取...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        df = ak.stock_zh_a_hist(
            symbol='000001',
            start_date=start_date.strftime('%Y%m%d'),
            end_date=end_date.strftime('%Y%m%d'),
            adjust="qfq"
        )
        if df is not None and not df.empty:
            print("✓ A股数据获取正常")
        else:
            print("✗ A股数据获取异常")
    except Exception as e:
        print(f"✗ A股数据获取失败: {e}")

if __name__ == "__main__":
    test_akshare_availability()
    test_us_stock_data()
