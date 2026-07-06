#!/usr/bin/env python3
"""
测试A股和港股功能
"""

import requests
import json
import time

def test_markets_api():
    """测试市场API"""
    url = "http://localhost:8000/analyze-stock/"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer xue123"
    }
    
    # 不传 start_date/end_date，使用服务端默认的最近一年滚动窗口，避免测试数据过期。
    test_cases = [
        {
            "name": "A股测试 - 平安银行",
            "data": {
                "stock_code": "000001",
                "market_type": "A"
            }
        },
        {
            "name": "港股测试 - 腾讯控股",
            "data": {
                "stock_code": "0700",
                "market_type": "HK"
            }
        },
        {
            "name": "美股测试 - Apple Inc.",
            "data": {
                "stock_code": "AAPL",
                "market_type": "US"
            }
        },
        {
            "name": "ETF测试 - 黄金ETF",
            "data": {
                "stock_code": "518880",
                "market_type": "ETF"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🚀 {test_case['name']}")
        print(f"请求数据: {json.dumps(test_case['data'], ensure_ascii=False)}")
        
        try:
            response = requests.post(url, headers=headers, json=test_case['data'], timeout=60)
            
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ API调用成功!")
                
                # 提取关键信息
                report = result.get('report', {})
                technical_summary = result.get('technical_summary', {})
                
                print(f"股票代码: {report.get('stock_code')}")
                print(f"市场类型: {report.get('market_type')}")
                print(f"最新价格: {report.get('price')}")
                print(f"综合评分: {report.get('score')}")
                print(f"投资建议: {report.get('recommendation')}")
                print(f"数据点数: {report.get('data_points')}")
                print(f"实际数据区间: {report.get('data_start_date')} ~ {report.get('data_end_date')}")
                print(f"最新行情日期: {report.get('latest_data_date')}")
                print(f"行情距今天数: {report.get('data_freshness_days')}")
                print(f"RSI: {technical_summary.get('rsi_level')}")
                print(f"趋势: {technical_summary.get('trend')}")
                print(f"波动率: {technical_summary.get('volatility')}")
                
            else:
                print(f"❌ API调用失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败: 无法连接到API服务")
            break
        except requests.exceptions.Timeout:
            print("❌ 请求超时")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        
        # 在请求之间添加延迟
        if test_case != test_cases[-1]:
            print("⏳ 等待3秒后继续下一个测试...")
            time.sleep(3)

def test_service_health():
    """测试服务健康状态"""
    try:
        print("🏥 测试服务健康状态...")
        response = requests.get("http://localhost:8000/health", timeout=10)
        
        if response.status_code == 200:
            print("✅ 服务健康检查通过")
            print(f"响应: {response.json()}")
        else:
            print(f"❌ 服务健康检查失败: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")

def test_markets_endpoint():
    """测试市场信息端点"""
    try:
        print("\n🌍 测试市场信息端点...")
        response = requests.get("http://localhost:8000/markets", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 市场信息获取成功")
            markets = result.get('markets', {})
            for market_type, market_info in markets.items():
                print(f"  {market_type}: {market_info.get('name')} - {market_info.get('description')}")
        else:
            print(f"❌ 市场信息获取失败: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务")
    except Exception as e:
        print(f"❌ 市场信息测试失败: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("多市场功能测试")
    print("=" * 50)
    
    # 测试服务健康状态
    test_service_health()
    
    # 测试市场信息端点
    test_markets_endpoint()
    
    # 测试市场API
    test_markets_api()
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)
