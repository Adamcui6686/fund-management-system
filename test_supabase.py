#!/usr/bin/env python3
"""
Supabase连接测试脚本
"""

import requests
import json

# 测试参数
SUPABASE_URL = "https://vnaqasemczklpiborssf.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZuYXFhc2VtY3prbHBpYm9yc3NmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjY2MTkxOCwiZXhwIjoyMDcyMjM3OTE4fQ.zudOn4Tf8o_6M8c3nnOyaKG8ZaU244wcI5kPMjkQrzo"

def test_connection():
    """测试Supabase连接"""
    url = f"{SUPABASE_URL}/rest/v1/strategies"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json"
    }
    
    print("🔍 测试Supabase连接（使用service_role密钥）...")
    print(f"URL: {url}")
    print(f"Service Key (前20字符): {SUPABASE_SERVICE_KEY[:20]}...")
    print()
    
    try:
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 连接成功！")
            return True
        else:
            print(f"❌ 连接失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 网络错误: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()
