#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
只清空投资记录和持仓信息，保留策略、产品等其他数据
"""

import requests
import json
from datetime import datetime

# Supabase配置
SUPABASE_URL = "https://vnaqasemczklpiborssf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZuYXFhc2VtY3prbHBpYm9yc3NmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjY2MTkxOCwiZXhwIjoyMDcyMjM3OTE4fQ.zudOn4Tf8o_6M8c3nnOyaKG8ZaU244wcI5kPMjkQrzo"

def clear_investments_only():
    """只清空投资记录，保留其他数据"""
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    # 只清空投资相关的表
    tables_to_clear = [
        "investments",      # 投资记录
        "product_strategy_weights",  # 产品策略权重（因为会影响持仓计算）
    ]
    
    print("🗑️  开始清空投资记录和持仓信息...")
    print(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        for table in tables_to_clear:
            print(f"\n🔄 正在清空表: {table}")
            
            try:
                # 先查看表中有多少数据
                url = f"{SUPABASE_URL}/rest/v1/{table}?select=*"
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    count = len(data)
                    print(f"   发现 {count} 条记录")
                    
                    if count > 0:
                        # 删除所有数据
                        delete_url = f"{SUPABASE_URL}/rest/v1/{table}"
                        delete_response = requests.delete(delete_url, headers=headers, params={"id": "gte.0"})
                        
                        if delete_response.status_code in [200, 204]:
                            print(f"✅ 已清空表: {table}")
                        else:
                            print(f"❌ 清空失败: {delete_response.status_code}")
                            print(f"   响应: {delete_response.text}")
                    else:
                        print(f"ℹ️  表 {table} 已经是空的")
                else:
                    print(f"❌ 无法查询表 {table}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ 处理表 {table} 时出错: {e}")
        
        print("\n🔍 验证清空结果...")
        verify_investments_cleared()
        
        print("\n📊 保留的数据:")
        verify_remaining_data()
        
    except Exception as e:
        print(f"❌ 清空失败: {e}")

def verify_investments_cleared():
    """验证投资记录是否已清空"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    investment_tables = ["investments", "product_strategy_weights"]
    
    for table in investment_tables:
        try:
            url = f"{SUPABASE_URL}/rest/v1/{table}?select=*"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                count = len(data)
                status = "✅" if count == 0 else "❌"
                print(f"{status} {table}: {count} 条记录")
        except Exception as e:
            print(f"❌ 查询表 {table} 失败: {e}")

def verify_remaining_data():
    """验证保留的数据"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    remaining_tables = ["strategies", "nav_records", "investors", "products"]
    
    for table in remaining_tables:
        try:
            url = f"{SUPABASE_URL}/rest/v1/{table}?select=*"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                count = len(data)
                print(f"📋 {table}: {count} 条记录")
        except Exception as e:
            print(f"❌ 查询表 {table} 失败: {e}")

if __name__ == "__main__":
    print("🎯 只清空投资记录和持仓信息")
    print("📍 保留策略、净值记录、投资人、产品等数据")
    confirm = input("\n确认清空投资记录？(输入 'yes' 确认): ")
    
    if confirm.lower() == 'yes':
        clear_investments_only()
        print("\n🎉 投资记录清空完成！")
        print("💡 提示:")
        print("   - 投资记录和持仓信息已删除")
        print("   - 策略、净值记录、投资人、产品数据已保留")
        print("   - 可以重新配置产品策略权重")
        print("   - 可以重新进行投资申购")
    else:
        print("❌ 操作已取消")
