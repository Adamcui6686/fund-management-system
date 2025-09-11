import streamlit as st
import requests

st.title("Supabase连接测试")

# 直接在代码中硬编码测试
SUPABASE_URL = "https://vnaqasemczklpiborssf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZuYXFhc2VtY3prbHBpYm9yc3NmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjY2MTkxOCwiZXhwIjoyMDcyMjM3OTE4fQ.zudOn4Tf8o_6M8c3nnOyaKG8ZaU244wcI5kPMjkQrzo"

st.write("测试URL:", SUPABASE_URL)
st.write("密钥前20字符:", SUPABASE_KEY[:20] + "...")

try:
    url = f"{SUPABASE_URL}/rest/v1/strategies"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    st.write("状态码:", response.status_code)
    st.write("响应内容:", response.text)
    
    if response.status_code == 200:
        st.success("✅ 连接成功！")
    else:
        st.error(f"❌ 连接失败: {response.status_code}")
        st.write("错误详情:", response.text)
        
except Exception as e:
    st.error(f"❌ 异常: {str(e)}")

