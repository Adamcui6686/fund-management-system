import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
import numpy as np

# 根据环境选择数据库
try:
    # 尝试导入云数据库管理器
    from supabase_database import SupabaseManager
    db = SupabaseManager()
    st.sidebar.success("🌐 已连接云数据库")
except Exception as e:
    # 如果云数据库不可用，回退到本地数据库
    from database import DatabaseManager
    db = DatabaseManager()
    st.sidebar.warning("💻 使用本地数据库")

# 页面配置
st.set_page_config(
    page_title="私募基金净值管理系统",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 侧边栏导航
st.sidebar.title("📈 私募基金净值管理")
st.sidebar.markdown("---")

page = st.sidebar.selectbox(
    "选择功能页面",
    ["📊 数据概览", "🎯 策略管理", "📝 净值录入", "👥 投资人管理", "📦 产品管理", "📈 图表分析"]
)

# 主页面标题
st.title("私募基金净值管理系统")

if page == "📊 数据概览":
    st.header("数据概览")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # 获取统计数据
    strategies = db.get_strategies()
    investors = db.get_investors()
    products = db.get_products()
    nav_records = db.get_nav_records()
    
    with col1:
        st.metric("策略数量", len(strategies))
    
    with col2:
        st.metric("投资人数量", len(investors))
    
    with col3:
        st.metric("产品数量", len(products))
    
    with col4:
        st.metric("净值记录数", len(nav_records))
    
    st.markdown("---")
    
    # 最新净值记录
    if not nav_records.empty:
        st.subheader("最新净值记录")
        latest_records = nav_records.groupby('strategy_id').last().reset_index()
        
        if not strategies.empty:
            # 合并策略名称
            strategies_dict = {row['id']: row['name'] for _, row in strategies.iterrows()}
            latest_records['strategy_name'] = latest_records['strategy_id'].map(strategies_dict)
        
        display_df = latest_records[['strategy_name', 'date', 'nav_value', 'return_rate']].copy()
        display_df.columns = ['策略名称', '日期', '净值', '收益率(%)']
        if 'return_rate' in display_df.columns:
            display_df['收益率(%)'] = display_df['收益率(%)'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
        st.dataframe(display_df, use_container_width=True)

elif page == "🎯 策略管理":
    st.header("策略管理")
    
    tab1, tab2 = st.tabs(["添加策略", "策略列表"])
    
    with tab1:
        st.subheader("添加新策略")
        
        with st.form("add_strategy_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                strategy_name = st.text_input("策略名称*", placeholder="请输入策略名称")
                start_date = st.date_input("开始日期", value=datetime.now().date())
            
            with col2:
                description = st.text_area("策略描述", placeholder="请描述策略的投资风格、特点等")
                initial_nav = st.number_input("初始净值", value=1.000, min_value=0.001, step=0.001, format="%.3f")
            
            submitted = st.form_submit_button("添加策略", type="primary")
            
            if submitted:
                if strategy_name:
                    try:
                        success = db.add_strategy(strategy_name, description, start_date.isoformat(), initial_nav)
                        if success:
                            st.success(f"策略 '{strategy_name}' 添加成功！")
                            st.rerun()
                        else:
                            st.error("添加策略失败，可能策略名称已存在")
                    except Exception as e:
                        st.error(f"添加策略失败：{str(e)}")
                else:
                    st.error("请输入策略名称")
    
    with tab2:
        st.subheader("策略列表")
        
        strategies = db.get_strategies()
        
        if not strategies.empty:
            # 显示策略表格
            display_df = strategies[['name', 'description', 'start_date', 'initial_nav', 'created_at']].copy()
            display_df.columns = ['策略名称', '描述', '开始日期', '初始净值', '创建时间']
            
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("暂无策略数据，请先添加策略")

elif page == "📝 净值录入":
    st.header("净值录入")
    
    strategies = db.get_strategies()
    
    if strategies.empty:
        st.warning("请先在策略管理页面添加策略")
    else:
        tab1, tab2 = st.tabs(["单个录入", "批量录入"])
        
        with tab1:
            st.subheader("单个净值录入")
            
            with st.form("add_nav_form"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    strategy_options = {row['name']: row['id'] for _, row in strategies.iterrows()}
                    selected_strategy = st.selectbox("选择策略", options=list(strategy_options.keys()))
                
                with col2:
                    nav_date = st.date_input("净值日期", value=datetime.now().date())
                
                with col3:
                    nav_value = st.number_input("净值", value=1.000, min_value=0.001, step=0.001, format="%.3f")
                
                submitted = st.form_submit_button("录入净值", type="primary")
                
                if submitted:
                    strategy_id = strategy_options[selected_strategy]
                    try:
                        success = db.add_nav_record(strategy_id, nav_date.isoformat(), nav_value)
                        if success:
                            st.success(f"策略 '{selected_strategy}' 在 {nav_date} 的净值 {nav_value} 录入成功！")
                            st.rerun()
                        else:
                            st.error("录入失败")
                    except Exception as e:
                        st.error(f"录入失败：{str(e)}")
        
        with tab2:
            st.subheader("批量净值录入")
            st.info("您可以同时为多个策略录入相同日期的净值")
            
            # 快速录入表格
            st.subheader("快速录入（同一日期多个策略）")
            
            with st.form("batch_nav_form"):
                batch_date = st.date_input("录入日期", value=datetime.now().date())
                
                st.write("为每个策略输入净值：")
                nav_inputs = {}
                
                cols = st.columns(min(3, len(strategies)))
                for i, (_, strategy) in enumerate(strategies.iterrows()):
                    with cols[i % 3]:
                        nav_inputs[strategy['id']] = st.number_input(
                            f"{strategy['name']}", 
                            value=1.000, 
                            min_value=0.001, 
                            step=0.001,
                            format="%.3f",
                            key=f"nav_{strategy['id']}"
                        )
                
                if st.form_submit_button("批量录入", type="primary"):
                    success_count = 0
                    for strategy_id, nav_value in nav_inputs.items():
                        try:
                            success = db.add_nav_record(strategy_id, batch_date.isoformat(), nav_value)
                            if success:
                                success_count += 1
                        except Exception as e:
                            st.error(f"策略ID {strategy_id} 录入失败：{str(e)}")
                    
                    if success_count > 0:
                        st.success(f"成功录入 {success_count} 个策略的净值数据！")
                        st.rerun()

# 其他页面代码保持不变...
# （为了节省空间，这里省略了其他页面的代码，实际使用时需要完整复制）

# 在页面底部显示数据库状态
st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 使用提示")
st.sidebar.markdown("""
1. 先在 **策略管理** 中添加您的投资策略
2. 在 **净值录入** 中定期录入策略净值
3. 在 **图表分析** 中查看净值曲线和收益分析
4. 可以创建产品组合多个策略
""")

st.sidebar.markdown("---")
try:
    if hasattr(db, 'supabase_url'):
        st.sidebar.success("🌐 云端模式")
        st.sidebar.caption("数据实时同步")
    else:
        st.sidebar.info("💻 本地模式")
        st.sidebar.caption("仅限本机访问")
except:
    st.sidebar.info("💻 本地模式")

st.sidebar.markdown("*私募基金净值管理系统 v2.0*")
