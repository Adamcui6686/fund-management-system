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
        # 检查是否在云端环境
        if hasattr(st, 'secrets') and 'SUPABASE_URL' in st.secrets:
            from supabase_database import SupabaseManager
            db = SupabaseManager()
            # 简单测试连接
            test_strategies = db.get_strategies()
            st.sidebar.success("🌐 已连接云数据库")
            st.sidebar.caption("数据实时同步")
            return db
        else:
            raise Exception("未配置云数据库")
    except Exception as e:
        # 回退到本地数据库
        from database import DatabaseManager
        st.sidebar.info("💻 使用本地数据库")
        st.sidebar.caption("数据安全存储")
        return DatabaseManager()

db = init_database()

# 侧边栏导航
st.sidebar.title("📈 私募基金净值管理")
st.sidebar.markdown("---")

page = st.sidebar.selectbox(
    "选择功能页面",
    ["📊 数据概览", "🎯 策略管理", "📝 净值录入", "👥 投资人管理", "📦 产品管理", "📈 图表分析", "生成示例数据"]
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
                    # 统一将日期转为字符串，避免下游JSON序列化错误
                    investment_date_str = investment_date.isoformat() if hasattr(investment_date, 'isoformat') else str(investment_date)
                
                with col5:
                    amount = st.number_input("金额", value=1000.0, min_value=0.01, step=1000.0)
                
                with col6:
                    # 显示当前产品净值
                    if selected_product:
                        product_id = product_options[selected_product]
                        try:
                            current_nav = db.calculate_product_nav(product_id, investment_date_str)
                        except Exception:
                            # 若出现序列化错误或网络问题，退回到默认净值
                            current_nav = 1.0
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
                            
                            # 统一传入字符串日期，避免云端API JSON序列化错误
                            db.add_investment(investor_id, product_id, final_amount, investment_date_str, transaction_type_en)
                            
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
                
                # 获取当前产品的权重配置作为默认值
                current_weights_dict = {}
                if not current_weights.empty:
                    current_weights_dict = {row['strategy_id']: row['weight'] * 100 for _, row in current_weights.iterrows()}
                
                for _, strategy in strategies.iterrows():
                    # 使用产品ID和策略ID组合的key，并设置当前权重作为默认值
                    default_weight = current_weights_dict.get(strategy['id'], 0.0)
                    weight = st.number_input(
                        f"{strategy['name']}", 
                        value=default_weight, 
                        min_value=0.0, 
                        max_value=100.0, 
                        step=0.1,
                        key=f"weight_{product_id}_{strategy['id']}"
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

elif page == "生成示例数据":
    st.header("生成丰富的示例数据")
    st.info("点击下方按钮为系统生成完整的示例数据，包括策略、投资人、产品、净值记录和投资交易。")
    
    if st.button("开始生成示例数据", type="primary", use_container_width=True):
        import random
        from datetime import datetime, date, timedelta
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # 1. 添加策略
            status_text.text("正在添加投资策略...")
            strategies_data = [
                ("量化多因子策略", "基于多因子模型的量化选股策略，主要投资A股市场", "2023-01-01", 1.000),
                ("市场中性策略", "股票多空配对交易，追求绝对收益", "2023-02-01", 1.000),
                ("CTA趋势策略", "期货趋势跟踪策略，涵盖商品、股指、国债期货", "2023-03-01", 1.000),
                ("可转债套利", "可转债相对价值套利策略", "2023-04-01", 1.000),
                ("行业轮动策略", "基于宏观经济周期的行业配置策略", "2023-01-15", 1.000),
                ("价值成长策略", "精选优质成长股的长期投资策略", "2023-05-01", 1.000),
                ("事件驱动策略", "基于公司特定事件的投资机会策略", "2023-06-01", 1.000),
                ("宏观对冲策略", "基于宏观经济判断的多资产配置策略", "2023-02-15", 1.000)
            ]
            
            strategy_ids = []
            for name, desc, start_date, initial_nav in strategies_data:
                success = db.add_strategy(name, desc, start_date, initial_nav)
                if success:
                    strategies = db.get_strategies()
                    strategy_id = strategies[strategies['name'] == name].iloc[0]['id']
                    strategy_ids.append(strategy_id)
                    st.success(f"✅ 添加策略: {name}")
            
            progress_bar.progress(20)
            
            # 2. 生成净值数据
            status_text.text("正在生成净值历史数据...")
            
            start_date = datetime(2023, 1, 1).date()
            end_date = datetime.now().date()
            
            for strategy_id in strategy_ids:
                current_date = start_date
                current_nav = 1.000
                
                while current_date <= end_date:
                    if current_date.weekday() < 5:  # 工作日
                        daily_return = random.normalvariate(0.001, 0.015)
                        current_nav = current_nav * (1 + daily_return)
                        current_nav = max(0.1, current_nav)
                        
                        if current_date.weekday() == 4:  # 周五录入
                            db.add_nav_record(strategy_id, current_date.isoformat(), round(current_nav, 3))
                    
                    current_date += timedelta(days=1)
            
            st.success("✅ 净值数据生成完成")
            progress_bar.progress(50)
            
            # 3. 添加投资人
            status_text.text("正在添加投资人...")
            investors_data = [
                ("张三", "13800138000"), ("李四", "13900139000"), ("王五", "13700137000"),
                ("赵六", "13600136000"), ("钱七", "13500135000"), ("孙八", "13400134000"),
                ("周九", "13300133000"), ("吴十", "13200132000"), ("郑十一", "13100131000"),
                ("王十二", "13000130000"), ("机构投资者A", "021-12345678"), ("家族办公室B", "010-87654321"),
                ("私人银行客户C", "0755-11111111"), ("高净值客户D", "020-22222222"), ("企业年金E", "0571-33333333")
            ]
            
            investor_ids = []
            for name, contact in investors_data:
                success = db.add_investor(name, contact)
                if success:
                    investors = db.get_investors()
                    investor_id = investors[investors['name'] == name].iloc[0]['id']
                    investor_ids.append(investor_id)
                    st.success(f"✅ 添加投资人: {name}")
            
            progress_bar.progress(65)
            
            # 4. 添加产品
            status_text.text("正在创建产品...")
            products_data = [
                ("稳健增长1号", "低风险稳健型产品，主要配置市场中性和量化多因子策略"),
                ("进取增长2号", "中高风险进取型产品，主要配置CTA和事件驱动策略"),
                ("平衡配置3号", "中等风险平衡型产品，多策略均衡配置"),
                ("价值精选4号", "专注价值投资的产品，主要配置价值成长策略"),
                ("宏观配置5号", "基于宏观判断的多资产配置产品"),
                ("量化精英6号", "纯量化策略产品组合"),
                ("套利稳健7号", "以套利策略为主的低风险产品")
            ]
            
            product_ids = []
            for name, desc in products_data:
                success = db.add_product(name, desc)
                if success:
                    products = db.get_products()
                    product_id = products[products['name'] == name].iloc[0]['id']
                    product_ids.append(product_id)
                    st.success(f"✅ 添加产品: {name}")
            
            progress_bar.progress(75)
            
            # 5. 设置产品策略权重
            status_text.text("正在配置产品策略权重...")
            
            product_strategies = [
                (product_ids[0], [(strategy_ids[1], 0.4), (strategy_ids[0], 0.3), (strategy_ids[3], 0.3)]),
                (product_ids[1], [(strategy_ids[2], 0.4), (strategy_ids[6], 0.3), (strategy_ids[4], 0.3)]),
                (product_ids[2], [(strategy_ids[0], 0.25), (strategy_ids[1], 0.25), (strategy_ids[4], 0.25), (strategy_ids[5], 0.25)]),
                (product_ids[3], [(strategy_ids[5], 0.7), (strategy_ids[4], 0.3)]),
                (product_ids[4], [(strategy_ids[7], 0.5), (strategy_ids[2], 0.3), (strategy_ids[1], 0.2)]),
                (product_ids[5], [(strategy_ids[0], 0.6), (strategy_ids[1], 0.4)]),
                (product_ids[6], [(strategy_ids[3], 0.8), (strategy_ids[6], 0.2)])
            ]
            
            for product_id, strategies in product_strategies:
                for strategy_id, weight in strategies:
                    db.set_product_strategy_weight(product_id, strategy_id, weight, "2023-01-01")
            
            st.success("✅ 产品策略权重配置完成")
            progress_bar.progress(85)
            
            # 6. 生成投资记录
            status_text.text("正在生成投资交易记录...")
            
            investment_amounts = [100000, 200000, 500000, 1000000, 2000000, 5000000, 10000000]
            
            for investor_id in investor_ids[:12]:
                num_products = random.randint(1, 3)
                selected_products = random.sample(product_ids, num_products)
                
                for product_id in selected_products:
                    amount = random.choice(investment_amounts)
                    investment_date = random.choice([
                        "2023-01-15", "2023-02-01", "2023-03-01", "2023-04-01", 
                        "2023-05-01", "2023-06-01", "2023-07-01", "2023-08-01",
                        "2023-09-01", "2023-10-01", "2023-11-01", "2023-12-01",
                        "2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01",
                        "2024-05-01", "2024-06-01", "2024-07-01", "2024-08-01"
                    ])
                    
                    db.add_investment(investor_id, product_id, amount, investment_date, "investment")
                    
                    if random.random() < 0.5:
                        additional_amount = amount * random.uniform(0.2, 0.8)
                        later_date = (datetime.strptime(investment_date, "%Y-%m-%d") + timedelta(days=random.randint(30, 180))).strftime("%Y-%m-%d")
                        if datetime.strptime(later_date, "%Y-%m-%d").date() <= datetime.now().date():
                            db.add_investment(investor_id, product_id, additional_amount, later_date, "investment")
                    
                    if random.random() < 0.2:
                        redemption_amount = amount * random.uniform(0.1, 0.3)
                        redemption_date = (datetime.strptime(investment_date, "%Y-%m-%d") + timedelta(days=random.randint(90, 270))).strftime("%Y-%m-%d")
                        if datetime.strptime(redemption_date, "%Y-%m-%d").date() <= datetime.now().date():
                            db.add_investment(investor_id, product_id, -redemption_amount, redemption_date, "redemption")
            
            st.success("✅ 投资交易记录生成完成")
            progress_bar.progress(100)
            
            status_text.text("✅ 所有示例数据生成完成！")
            
            # 显示统计信息
            st.subheader("📊 数据统计")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                strategies = db.get_strategies()
                st.metric("策略数量", len(strategies))
            
            with col2:
                investors = db.get_investors()
                st.metric("投资人数量", len(investors))
            
            with col3:
                products = db.get_products()
                st.metric("产品数量", len(products))
            
            with col4:
                nav_records = db.get_nav_records()
                st.metric("净值记录数", len(nav_records))
            
            st.success("🎉 云端示例数据生成完成！现在您可以体验完整的私募基金管理系统了！")
            st.info("💡 建议：现在可以访问各个功能页面查看数据，体验系统的完整功能。")
            
        except Exception as e:
            st.error(f"❌ 数据生成失败: {str(e)}")
            st.info("请确保已正确配置Supabase连接")

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
