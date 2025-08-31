#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
常见功能扩展示例
复制这些代码到 app.py 中即可添加新功能
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np

# ========== 示例1：数据导出功能 ==========
def add_data_export_feature():
    """添加数据导出功能"""
    
    # 在侧边栏选项中添加
    page = st.sidebar.selectbox(
        "选择功能页面",
        ["📊 数据概览", "🎯 策略管理", "📝 净值录入", 
         "👥 投资人管理", "📦 产品管理", "📈 图表分析",
         "📋 数据导出"]  # 新增这一行
    )
    
    # 添加新页面处理
    if page == "📋 数据导出":
        st.header("数据导出")
        
        col1, col2 = st.columns(2)
        
        with col1:
            export_type = st.selectbox("选择导出类型", 
                                     ["净值数据", "投资记录", "策略汇总", "投资人信息"])
        
        with col2:
            date_range = st.selectbox("时间范围", 
                                    ["全部", "近1个月", "近3个月", "近6个月", "近1年"])
        
        if st.button("生成报表", type="primary"):
            # 根据选择导出不同数据
            if export_type == "净值数据":
                data = db.get_nav_records()
                filename = f"净值数据_{datetime.now().strftime('%Y%m%d')}.csv"
            elif export_type == "投资记录":
                data = db.get_investor_investments()
                filename = f"投资记录_{datetime.now().strftime('%Y%m%d')}.csv"
            elif export_type == "策略汇总":
                data = db.get_strategies()
                filename = f"策略汇总_{datetime.now().strftime('%Y%m%d')}.csv"
            else:
                data = db.get_investors()
                filename = f"投资人信息_{datetime.now().strftime('%Y%m%d')}.csv"
            
            if not data.empty:
                csv = data.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 下载CSV文件",
                    data=csv,
                    file_name=filename,
                    mime="text/csv"
                )
                st.success("报表生成成功！点击上方按钮下载。")
            else:
                st.warning("暂无数据可导出")

# ========== 示例2：风险指标计算 ==========
def add_risk_analysis():
    """添加风险分析功能"""
    
    # 在图表分析中添加新标签页
    tab1, tab2, tab3, tab4 = st.tabs(["净值曲线", "收益率分析", "策略对比", "风险分析"])
    
    with tab4:
        st.subheader("风险指标分析")
        
        strategies = db.get_strategies()
        if not strategies.empty:
            strategy_options = {row['name']: row['id'] for _, row in strategies.iterrows()}
            selected_strategy = st.selectbox("选择策略", options=list(strategy_options.keys()))
            
            if selected_strategy:
                strategy_id = strategy_options[selected_strategy]
                nav_data = db.get_nav_records(strategy_id)
                
                if len(nav_data) > 10:
                    # 计算风险指标
                    returns = nav_data['return_rate'].dropna() / 100
                    nav_values = nav_data['nav_value']
                    
                    # 基础指标
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        annual_return = (nav_values.iloc[-1] / nav_values.iloc[0]) ** (252/len(nav_data)) - 1
                        st.metric("年化收益率", f"{annual_return*100:.2f}%")
                    
                    with col2:
                        volatility = returns.std() * np.sqrt(52)  # 周度数据
                        st.metric("年化波动率", f"{volatility*100:.2f}%")
                    
                    with col3:
                        sharpe = (returns.mean() / returns.std()) * np.sqrt(52) if returns.std() > 0 else 0
                        st.metric("夏普比率", f"{sharpe:.2f}")
                    
                    with col4:
                        # 计算最大回撤
                        peak = nav_values.expanding().max()
                        drawdown = (nav_values - peak) / peak
                        max_dd = drawdown.min()
                        st.metric("最大回撤", f"{max_dd*100:.2f}%")
                    
                    # 风险分布图
                    import plotly.figure_factory as ff
                    
                    fig = ff.create_distplot([returns.dropna()], ['收益率分布'], 
                                           show_hist=True, show_curve=True)
                    fig.update_layout(title="收益率分布图")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("数据不足，需要至少10个净值记录进行风险分析")

# ========== 示例3：用户登录功能 ==========
def add_simple_login():
    """添加简单的用户登录功能"""
    
    # 在 app.py 最开始添加
    def check_login():
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
        
        if not st.session_state.logged_in:
            st.title("🔐 基金管理系统登录")
            
            with st.form("login_form"):
                username = st.text_input("用户名")
                password = st.text_input("密码", type="password")
                submitted = st.form_submit_button("登录")
                
                if submitted:
                    # 简单的用户验证（实际使用时应该用更安全的方式）
                    users = {
                        "admin": "admin123",
                        "manager": "manager123",
                        "viewer": "viewer123"
                    }
                    
                    if username in users and users[username] == password:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.success("登录成功！")
                        st.rerun()
                    else:
                        st.error("用户名或密码错误")
            
            st.stop()  # 阻止继续执行
    
    # 在主程序开始前调用
    check_login()
    
    # 在侧边栏显示用户信息
    st.sidebar.write(f"👤 欢迎，{st.session_state.username}")
    if st.sidebar.button("退出登录"):
        st.session_state.logged_in = False
        st.rerun()

# ========== 示例4：邮件通知功能 ==========
def add_email_notification():
    """添加邮件通知功能"""
    
    # 在设置页面添加邮件配置
    elif page == "⚙️ 系统设置":
        st.header("系统设置")
        
        tab1, tab2 = st.tabs(["邮件通知", "数据备份"])
        
        with tab1:
            st.subheader("邮件通知设置")
            
            with st.form("email_settings"):
                email = st.text_input("通知邮箱", placeholder="your@email.com")
                
                notify_options = st.multiselect(
                    "通知类型",
                    ["新投资人申购", "大额赎回提醒", "净值异常波动", "每周报表"]
                )
                
                threshold = st.number_input("异常波动阈值(%)", value=5.0, min_value=0.1)
                
                if st.form_submit_button("保存设置"):
                    # 保存邮件设置到数据库或配置文件
                    st.success("邮件设置已保存")
            
            # 发送测试邮件
            if st.button("发送测试邮件"):
                # 这里需要集成邮件服务（如SendGrid、阿里云邮件等）
                st.info("测试邮件发送功能需要配置SMTP服务")

# ========== 示例5：移动端优化 ==========
def add_mobile_optimization():
    """添加移动端优化"""
    
    # 检测设备类型
    def is_mobile():
        return st.session_state.get('mobile_view', False)
    
    # 在侧边栏添加视图切换
    view_mode = st.sidebar.radio("显示模式", ["桌面版", "移动版"])
    st.session_state.mobile_view = (view_mode == "移动版")
    
    # 响应式布局
    if is_mobile():
        # 移动端：单列布局
        st.write("📱 移动端模式")
        
        # 紧凑的指标显示
        metrics_container = st.container()
        with metrics_container:
            col1, col2 = st.columns(2)  # 移动端用2列而不是4列
    else:
        # 桌面端：多列布局
        col1, col2, col3, col4 = st.columns(4)

# ========== 使用说明 ==========
"""
如何添加这些功能：

1. 复制相应的代码到 app.py 文件中
2. 在GitHub上编辑文件，或者本地修改后推送
3. Streamlit Cloud会自动检测更改并重新部署

示例：添加数据导出功能
1. 复制 add_data_export_feature() 中的代码
2. 粘贴到 app.py 的相应位置
3. 保存文件，系统自动更新

注意事项：
- 新功能需要在侧边栏选项中添加对应的页面
- 复杂功能可能需要修改 database.py
- 测试功能时建议先在本地运行 streamlit run app.py
"""
