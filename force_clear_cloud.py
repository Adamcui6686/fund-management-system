#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
强制清空云端Supabase数据库脚本
使用更彻底的方法删除所有数据
"""

import requests
import json

# Supabase配置
SUPABASE_URL = "https://vnaqasemczklpiborssf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZuYXFhc2VtY3prbHBpYm9yc3NmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjY2MTkxOCwiZXhwIjoyMDcyMjM3OTE4fQ.zudOn4Tf8o_6M8c3nnOyaKG8ZaU244wcI5kPMjkQrzo"

def force_clear_database():
    """强制清空云端数据库"""
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    # 所有表名
    tables = [
        "investments",
        "product_strategy_weights", 
        "products",
        "investors",
        "nav_records",
        "strategies"
    ]
    
    print("🗑️  强制清空云端数据库...")
    
    for table in tables:
        print(f"\n🔄 处理表: {table}")
        
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
    
    print("\n🔍 最终验证...")
    verify_clear()

def verify_clear():
    """验证清空结果"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    tables = ["strategies", "nav_records", "investors", "products", "investments", "product_strategy_weights"]
    
    total_records = 0
    for table in tables:
        try:
            url = f"{SUPABASE_URL}/rest/v1/{table}?select=*"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                count = len(data)
                total_records += count
                status = "✅" if count == 0 else "❌"
                print(f"{status} {table}: {count} 条记录")
            else:
                print(f"❌ 无法查询表 {table}: {response.status_code}")
        except Exception as e:
            print(f"❌ 查询表 {table} 失败: {e}")
    
    if total_records == 0:
        print("\n🎉 所有表已完全清空！")
    else:
        print(f"\n⚠️  仍有 {total_records} 条记录未清空")

if __name__ == "__main__":
    force_clear_database()

