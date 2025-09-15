#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清空云端Supabase数据库脚本
删除所有表数据，保留表结构
"""

import requests
import json
from datetime import datetime

# Supabase配置
SUPABASE_URL = "https://vnaqasemczklpiborssf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZuYXFhc2VtY3prbHBpYm9yc3NmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjY2MTkxOCwiZXhwIjoyMDcyMjM3OTE4fQ.zudOn4Tf8o_6M8c3nnOyaKG8ZaU244wcI5kPMjkQrzo"

def clear_cloud_database():
    """清空云端Supabase数据库中的所有数据"""
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    # 需要清空的表（按依赖关系排序，先清空有外键的表）
    tables_to_clear = [
        "investments",      # 投资记录
        "product_strategy_weights",  # 产品策略权重
        "products",         # 产品
        "investors",        # 投资人
        "nav_records",      # 净值记录
        "strategies"        # 策略
    ]
    
    print("🗑️  开始清空云端数据库...")
    print(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        for table in tables_to_clear:
            print(f"\n🔄 正在清空表: {table}")
            
            # 删除所有数据 (使用WHERE子句)
            url = f"{SUPABASE_URL}/rest/v1/{table}?id=gt.0"
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 204:
                print(f"✅ 已清空表: {table}")
            elif response.status_code == 200:
                print(f"✅ 已清空表: {table}")
            else:
                print(f"⚠️  表 {table} 清空状态: {response.status_code}")
                if response.text:
                    print(f"   响应: {response.text}")
        
        print("\n🎉 云端数据库清空完成！")
        print("📊 已清空的表:")
        for table in tables_to_clear:
            print(f"   - {table}")
        
        print("\n💡 提示:")
        print("   - 所有云端数据已删除")
        print("   - 表结构保持不变")
        print("   - 可以重新开始录入数据")
        print("   - 本地数据库数据不受影响")
        
    except Exception as e:
        print(f"❌ 清空云端数据库失败: {e}")

def verify_clear():
    """验证清空结果"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    print("\n🔍 验证清空结果...")
    
    tables_to_check = ["strategies", "nav_records", "investors", "products", "investments"]
    
    for table in tables_to_check:
        try:
            url = f"{SUPABASE_URL}/rest/v1/{table}?select=count"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                print(f"📊 {table}: {count} 条记录")
            else:
                print(f"❌ 无法查询表 {table}: {response.status_code}")
        except Exception as e:
            print(f"❌ 查询表 {table} 失败: {e}")

if __name__ == "__main__":
    print("🚨 警告: 此操作将删除云端Supabase数据库中的所有数据！")
    print("📍 数据库地址: https://vnaqasemczklpiborssf.supabase.co")
    confirm = input("\n确认清空云端数据库？(输入 'yes' 确认): ")
    
    if confirm.lower() == 'yes':
        clear_cloud_database()
        verify_clear()
    else:
        print("❌ 操作已取消")
