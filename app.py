import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
import numpy as np

# 页面配置
st.set_page_config(
    page_title="私募基金净值管理系统",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化数据库 - 智能选择本地或云端
@st.cache_resource
def init_database():
    try:
        # 尝试使用云数据库
        from supabase_database import SupabaseManager
        db = SupabaseManager()
        # 简单测试连接
        test_strategies = db.get_strategies()
        st.sidebar.success("🌐 已连接云数据库")
        return db
    except Exception as e:
        # 回退到本地数据库
        from database import DatabaseManager
        st.sidebar.warning("💻 使用本地数据库")
        st.sidebar.caption(f"云连接失败: {str(e)[:50]}...")
        return DatabaseManager()

db = init_database()

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
        latest_records = latest_records.merge(strategies[['id', 'name']], left_on='strategy_id', right_on='id', suffixes=('', '_strategy'))
        
        display_df = latest_records[['name', 'date', 'nav_value', 'return_rate']].copy()
        display_df.columns = ['策略名称', '日期', '净值', '收益率(%)']
        display_df['收益率(%)'] = display_df['收益率(%)'].round(2)
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
                initial_nav = st.number_input("初始净值", value=1.0, min_value=0.01, step=0.01)
            
            submitted = st.form_submit_button("添加策略", type="primary")
            
            if submitted:
                if strategy_name:
                    try:
                        db.add_strategy(strategy_name, description, start_date, initial_nav)
                        st.success(f"策略 '{strategy_name}' 添加成功！")
                        st.rerun()
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
                        db.add_nav_record(strategy_id, nav_date, nav_value)
                        st.success(f"策略 '{selected_strategy}' 在 {nav_date} 的净值 {nav_value} 录入成功！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"录入失败：{str(e)}")
        
        with tab2:
            st.subheader("批量净值录入")
            st.info("您可以上传Excel文件进行批量录入，或者使用下面的表格进行快速录入")
            
            # 文件上传
            uploaded_file = st.file_uploader("上传Excel文件", type=['xlsx', 'xls'])
            
            if uploaded_file is not None:
                try:
                    df = pd.read_excel(uploaded_file)
                    st.subheader("文件预览")
                    st.dataframe(df.head())
                    
                    if st.button("开始批量导入"):
                        # 这里可以添加批量导入逻辑
                        st.success("批量导入功能开发中...")
                except Exception as e:
                    st.error(f"文件读取失败：{str(e)}")
            
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
                            db.add_nav_record(strategy_id, batch_date, nav_value)
                            success_count += 1
                        except Exception as e:
                            st.error(f"策略ID {strategy_id} 录入失败：{str(e)}")
                    
                    if success_count > 0:
                        st.success(f"成功录入 {success_count} 个策略的净值数据！")
                        st.rerun()

elif page == "👥 投资人管理":
    st.header("投资人管理")
    
    tab1, tab2, tab3, tab4 = st.tabs(["投资人列表", "添加投资人", "投资申购", "持仓查询"])
    
    with tab1:
        st.subheader("投资人列表")
        
        investors = db.get_investors()
        
        if not investors.empty:
            display_df = investors[['name', 'contact', 'created_at']].copy()
            display_df.columns = ['姓名', '联系方式', '创建时间']
            st.dataframe(display_df, use_container_width=True)
            
            # 显示投资汇总信息
            st.subheader("投资汇总")
            investment_summary = []
            
            for _, investor in investors.iterrows():
                portfolio = db.get_investor_portfolio(investor['id'])
                if not portfolio.empty:
                    total_investment = portfolio['total_investment'].sum()
                    total_current_value = portfolio['current_value'].sum()
                    total_profit = total_current_value - total_investment
                    total_profit_rate = (total_profit / total_investment * 100) if total_investment > 0 else 0
                    
                    investment_summary.append({
                        '投资人': investor['name'],
                        '总投资金额': f"¥{total_investment:,.2f}",
                        '当前市值': f"¥{total_current_value:,.2f}",
                        '盈亏金额': f"¥{total_profit:,.2f}",
                        '收益率': f"{total_profit_rate:.2f}%"
                    })
            
            if investment_summary:
                summary_df = pd.DataFrame(investment_summary)
                st.dataframe(summary_df, use_container_width=True)
        else:
            st.info("暂无投资人数据")
    
    with tab2:
        st.subheader("添加投资人")
        
        with st.form("add_investor_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                investor_name = st.text_input("投资人姓名*", placeholder="请输入投资人姓名")
            
            with col2:
                contact = st.text_input("联系方式", placeholder="电话或邮箱")
            
            submitted = st.form_submit_button("添加投资人", type="primary")
            
            if submitted:
                if investor_name:
                    try:
                        db.add_investor(investor_name, contact)
                        st.success(f"投资人 '{investor_name}' 添加成功！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"添加投资人失败：{str(e)}")
                else:
                    st.error("请输入投资人姓名")
    
    with tab3:
        st.subheader("投资申购/赎回")
        
        investors = db.get_investors()
        products = db.get_products()
        
        if investors.empty or products.empty:
            st.warning("请先添加投资人和产品")
        else:
            with st.form("investment_form"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # 投资人选择
                    investor_options = {row['name']: row['id'] for _, row in investors.iterrows()}
                    selected_investor = st.selectbox("选择投资人", options=list(investor_options.keys()))
                
                with col2:
                    # 产品选择
                    product_options = {row['name']: row['id'] for _, row in products.iterrows()}
                    selected_product = st.selectbox("选择产品", options=list(product_options.keys()))
                
                with col3:
                    # 交易类型
                    transaction_type = st.selectbox("交易类型", ["申购", "赎回"])
                
                col4, col5, col6 = st.columns(3)
                
                with col4:
                    investment_date = st.date_input("投资日期", value=datetime.now().date())
                
                with col5:
                    amount = st.number_input("金额", value=1000.0, min_value=0.01, step=1000.0)
                
                with col6:
                    # 显示当前产品净值
                    if selected_product:
                        product_id = product_options[selected_product]
                        current_nav = db.calculate_product_nav(product_id, investment_date)
                        st.metric("产品净值", f"{current_nav:.3f}")
                    else:
                        current_nav = 1.0
                
                submitted = st.form_submit_button("确认交易", type="primary")
                
                if submitted:
                    if amount > 0:
                        try:
                            investor_id = investor_options[selected_investor]
                            product_id = product_options[selected_product]
                            
                            # 赎回时金额为负数
                            final_amount = amount if transaction_type == "申购" else -amount
                            transaction_type_en = "investment" if transaction_type == "申购" else "redemption"
                            
                            db.add_investment(investor_id, product_id, final_amount, investment_date, transaction_type_en)
                            
                            shares = final_amount / current_nav
                            st.success(f"""
                            {transaction_type}成功！
                            - 投资人：{selected_investor}
                            - 产品：{selected_product}
                            - 金额：¥{amount:,.2f}
                            - 份额：{shares:.4f}
                            - 净值：{current_nav:.4f}
                            """)
                            st.rerun()
                        except Exception as e:
                            st.error(f"交易失败：{str(e)}")
                    else:
                        st.error("请输入有效金额")
    
    with tab4:
        st.subheader("持仓查询")
        
        investors = db.get_investors()
        
        if investors.empty:
            st.warning("暂无投资人数据")
        else:
            # 投资人选择
            investor_options = {row['name']: row['id'] for _, row in investors.iterrows()}
            selected_investor = st.selectbox("选择投资人", options=list(investor_options.keys()), key="portfolio_investor")
            
            if selected_investor:
                investor_id = investor_options[selected_investor]
                
                # 显示持仓信息
                portfolio = db.get_investor_portfolio(investor_id)
                
                if not portfolio.empty:
                    st.subheader(f"{selected_investor} 的持仓信息")
                    
                    # 格式化显示数据
                    display_portfolio = portfolio.copy()
                    display_portfolio['总投资金额'] = display_portfolio['total_investment'].apply(lambda x: f"¥{x:,.2f}")
                    display_portfolio['持有份额'] = display_portfolio['total_shares'].apply(lambda x: f"{x:.4f}")
                    display_portfolio['当前净值'] = display_portfolio['current_nav'].apply(lambda x: f"{x:.3f}")
                    display_portfolio['当前市值'] = display_portfolio['current_value'].apply(lambda x: f"¥{x:,.2f}")
                    display_portfolio['盈亏金额'] = display_portfolio['profit_loss'].apply(lambda x: f"¥{x:,.2f}")
                    display_portfolio['收益率'] = display_portfolio['profit_rate'].apply(lambda x: f"{x:.2f}%")
                    
                    final_display = display_portfolio[['product_name', '总投资金额', '持有份额', '当前净值', '当前市值', '盈亏金额', '收益率']].copy()
                    final_display.columns = ['产品名称', '总投资金额', '持有份额', '当前净值', '当前市值', '盈亏金额', '收益率(%)']
                    
                    st.dataframe(final_display, use_container_width=True)
                    
                    # 投资历史记录
                    st.subheader("投资历史记录")
                    investments = db.get_investor_investments(investor_id)
                    
                    if not investments.empty:
                        display_investments = investments[['investment_date', 'product_name', 'type', 'amount', 'shares', 'nav_at_investment']].copy()
                        display_investments.columns = ['投资日期', '产品名称', '交易类型', '金额', '份额', '交易净值']
                        display_investments['交易类型'] = display_investments['交易类型'].map({'investment': '申购', 'redemption': '赎回'})
                        display_investments['金额'] = display_investments['金额'].apply(lambda x: f"¥{x:,.2f}")
                        display_investments['份额'] = display_investments['份额'].apply(lambda x: f"{x:.4f}")
                        display_investments['交易净值'] = display_investments['交易净值'].apply(lambda x: f"{x:.3f}")
                        
                        st.dataframe(display_investments, use_container_width=True)
                else:
                    st.info(f"{selected_investor} 暂无持仓")

elif page == "📦 产品管理":
    st.header("产品管理")
    
    tab1, tab2, tab3 = st.tabs(["产品列表", "添加产品", "策略权重配置"])
    
    with tab1:
        st.subheader("产品列表")
        
        products = db.get_products()
        
        if not products.empty:
            display_df = products[['name', 'description', 'created_at']].copy()
            display_df.columns = ['产品名称', '描述', '创建时间']
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("暂无产品数据")
    
    with tab2:
        st.subheader("添加产品")
        
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                product_name = st.text_input("产品名称*", placeholder="请输入产品名称")
            
            with col2:
                product_description = st.text_area("产品描述", placeholder="请描述产品特点")
            
            submitted = st.form_submit_button("添加产品", type="primary")
            
            if submitted:
                if product_name:
                    try:
                        db.add_product(product_name, product_description)
                        st.success(f"产品 '{product_name}' 添加成功！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"添加产品失败：{str(e)}")
                else:
                    st.error("请输入产品名称")
    
    with tab3:
        st.subheader("策略权重配置")
        
        products = db.get_products()
        strategies = db.get_strategies()
        
        if products.empty or strategies.empty:
            st.warning("请先添加产品和策略")
        else:
            # 选择产品
            product_options = {row['name']: row['id'] for _, row in products.iterrows()}
            selected_product = st.selectbox("选择产品", options=list(product_options.keys()))
            product_id = product_options[selected_product]
            
            # 显示当前权重配置
            current_weights = db.get_product_weights(product_id)
            
            if not current_weights.empty:
                st.subheader("当前权重配置")
                display_weights = current_weights[['strategy_name', 'weight', 'effective_date']].copy()
                display_weights.columns = ['策略名称', '权重(%)', '生效日期']
                display_weights['权重(%)'] = (display_weights['权重(%)'] * 100).round(2)
                st.dataframe(display_weights, use_container_width=True)
            
            st.subheader("设置新权重")
            
            with st.form("set_weights_form"):
                effective_date = st.date_input("生效日期", value=datetime.now().date())
                
                st.write("设置各策略权重（%）：")
                weight_inputs = {}
                total_weight = 0
                
                for _, strategy in strategies.iterrows():
                    weight = st.number_input(
                        f"{strategy['name']}", 
                        value=0.0, 
                        min_value=0.0, 
                        max_value=100.0, 
                        step=0.1,
                        key=f"weight_{strategy['id']}"
                    )
                    weight_inputs[strategy['id']] = weight
                    total_weight += weight
                
                st.info(f"总权重：{total_weight:.1f}%")
                
                if st.form_submit_button("保存权重配置", type="primary"):
                    if abs(total_weight - 100.0) < 0.1:
                        try:
                            for strategy_id, weight in weight_inputs.items():
                                if weight > 0:
                                    db.set_product_strategy_weight(product_id, strategy_id, weight/100, effective_date)
                            st.success("权重配置保存成功！")
                            st.rerun()
                        except Exception as e:
                            st.error(f"保存失败：{str(e)}")
                    else:
                        st.error("总权重必须等于100%")

elif page == "📈 图表分析":
    st.header("图表分析")
    
    strategies = db.get_strategies()
    
    if strategies.empty:
        st.warning("暂无策略数据，请先添加策略和净值记录")
    else:
        tab1, tab2, tab3 = st.tabs(["净值曲线", "收益率分析", "策略对比"])
        
        with tab1:
            st.subheader("净值曲线图")
            
            # 策略选择
            strategy_options = {row['name']: row['id'] for _, row in strategies.iterrows()}
            selected_strategies = st.multiselect(
                "选择要显示的策略", 
                options=list(strategy_options.keys()),
                default=list(strategy_options.keys())[:3]  # 默认选择前3个
            )
            
            if selected_strategies:
                # 日期范围选择
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("开始日期")
                with col2:
                    end_date = st.date_input("结束日期", value=datetime.now().date())
                
                # 获取净值数据
                nav_data = db.get_nav_records(start_date=start_date, end_date=end_date)
                
                if not nav_data.empty:
                    # 过滤选中的策略
                    selected_strategy_ids = [strategy_options[name] for name in selected_strategies]
                    filtered_data = nav_data[nav_data['strategy_id'].isin(selected_strategy_ids)]
                    
                    if not filtered_data.empty:
                        # 绘制净值曲线
                        fig = go.Figure()
                        
                        for strategy_name in selected_strategies:
                            strategy_id = strategy_options[strategy_name]
                            strategy_data = filtered_data[filtered_data['strategy_id'] == strategy_id]
                            
                            fig.add_trace(go.Scatter(
                                x=strategy_data['date'],
                                y=strategy_data['nav_value'],
                                mode='lines+markers',
                                name=strategy_name,
                                line=dict(width=2),
                                marker=dict(size=4)
                            ))
                        
                        fig.update_layout(
                            title="策略净值曲线",
                            xaxis_title="日期",
                            yaxis_title="净值",
                            hovermode='x unified',
                            height=500
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # 显示净值数据表
                        st.subheader("净值数据详情")
                        display_data = filtered_data[['strategy_name', 'date', 'nav_value', 'return_rate']].copy()
                        display_data.columns = ['策略名称', '日期', '净值', '收益率(%)']
                        display_data['收益率(%)'] = display_data['收益率(%)'].round(2)
                        st.dataframe(display_data, use_container_width=True)
                    else:
                        st.info("选定日期范围内没有净值数据")
                else:
                    st.info("暂无净值数据，请先录入净值")
        
        with tab2:
            st.subheader("收益率分析")
            
            nav_data = db.get_nav_records()
            
            if not nav_data.empty:
                # 计算各策略的统计指标
                stats_data = []
                
                for _, strategy in strategies.iterrows():
                    strategy_navs = nav_data[nav_data['strategy_id'] == strategy['id']]
                    
                    if not strategy_navs.empty:
                        returns = strategy_navs['return_rate'].dropna()
                        
                        if len(returns) > 0:
                            stats = {
                                '策略名称': strategy['name'],
                                '累计收益率(%)': ((strategy_navs['nav_value'].iloc[-1] / strategy['initial_nav'] - 1) * 100).round(2),
                                '平均收益率(%)': returns.mean().round(2),
                                '收益率波动率(%)': returns.std().round(2),
                                '最大收益率(%)': returns.max().round(2),
                                '最小收益率(%)': returns.min().round(2),
                                '记录数量': len(strategy_navs)
                            }
                            stats_data.append(stats)
                
                if stats_data:
                    stats_df = pd.DataFrame(stats_data)
                    st.dataframe(stats_df, use_container_width=True)
                    
                    # 收益率分布图
                    if len(selected_strategies) > 0:
                        selected_strategy_ids = [strategy_options[name] for name in selected_strategies if name in strategy_options]
                        filtered_returns = nav_data[nav_data['strategy_id'].isin(selected_strategy_ids) & nav_data['return_rate'].notna()]
                        
                        if not filtered_returns.empty:
                            fig = px.histogram(
                                filtered_returns,
                                x='return_rate',
                                color='strategy_name',
                                title="收益率分布图",
                                nbins=20,
                                opacity=0.7
                            )
                            fig.update_layout(xaxis_title="收益率(%)", yaxis_title="频次")
                            st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("暂无足够数据进行统计分析")
            else:
                st.info("暂无净值数据")
        
        with tab3:
            st.subheader("策略对比分析")
            
            if len(strategies) >= 2:
                # 选择要对比的策略
                compare_strategies = st.multiselect(
                    "选择要对比的策略（最多4个）",
                    options=list(strategy_options.keys()),
                    default=list(strategy_options.keys())[:2],
                    max_selections=4
                )
                
                if len(compare_strategies) >= 2:
                    nav_data = db.get_nav_records()
                    
                    if not nav_data.empty:
                        # 创建对比图表
                        fig = go.Figure()
                        
                        for strategy_name in compare_strategies:
                            strategy_id = strategy_options[strategy_name]
                            strategy_data = nav_data[nav_data['strategy_id'] == strategy_id].copy()
                            
                            if not strategy_data.empty:
                                # 计算累计收益率
                                initial_nav = strategies[strategies['id'] == strategy_id]['initial_nav'].iloc[0]
                                strategy_data['cumulative_return'] = (strategy_data['nav_value'] / initial_nav - 1) * 100
                                
                                fig.add_trace(go.Scatter(
                                    x=strategy_data['date'],
                                    y=strategy_data['cumulative_return'],
                                    mode='lines+markers',
                                    name=strategy_name,
                                    line=dict(width=2),
                                    marker=dict(size=4)
                                ))
                        
                        fig.update_layout(
                            title="策略累计收益率对比",
                            xaxis_title="日期",
                            yaxis_title="累计收益率(%)",
                            hovermode='x unified',
                            height=500
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # 策略相关性分析（如果有足够数据）
                        if len(compare_strategies) >= 2:
                            returns_pivot = nav_data[nav_data['strategy_id'].isin([strategy_options[name] for name in compare_strategies])].pivot(
                                index='date', 
                                columns='strategy_name', 
                                values='return_rate'
                            ).dropna()
                            
                            if len(returns_pivot) > 1:
                                correlation_matrix = returns_pivot.corr()
                                
                                fig_corr = px.imshow(
                                    correlation_matrix,
                                    title="策略收益率相关性矩阵",
                                    color_continuous_scale="RdBu",
                                    aspect="auto"
                                )
                                
                                st.plotly_chart(fig_corr, use_container_width=True)
                    else:
                        st.info("暂无净值数据")
                else:
                    st.info("请至少选择2个策略进行对比")
            else:
                st.info("需要至少2个策略才能进行对比分析")

# 侧边栏信息
st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 使用提示")
st.sidebar.markdown("""
1. 先在 **策略管理** 中添加您的投资策略
2. 在 **净值录入** 中定期录入策略净值
3. 在 **图表分析** 中查看净值曲线和收益分析
4. 可以创建产品组合多个策略
""")

st.sidebar.markdown("---")
st.sidebar.markdown("*私募基金净值管理系统 v1.0*")
