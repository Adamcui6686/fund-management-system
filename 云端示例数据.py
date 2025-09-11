#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
云端示例数据生成器
为私募基金净值管理系统生成丰富的示例数据
"""

import streamlit as st
from supabase_database import SupabaseManager
from datetime import datetime, date, timedelta
import random
import pandas as pd

def generate_sample_data():
    """生成丰富的示例数据"""
    
    try:
        db = SupabaseManager()
        st.title("🚀 生成云端示例数据")
        
        if st.button("开始生成示例数据", type="primary"):
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
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
            for i, (name, desc, start_date, initial_nav) in enumerate(strategies_data):
                success = db.add_strategy(name, desc, start_date, initial_nav)
                if success:
                    # 获取刚添加的策略ID
                    strategies = db.get_strategies()
                    strategy_id = strategies[strategies['name'] == name].iloc[0]['id']
                    strategy_ids.append(strategy_id)
                    st.success(f"✅ 添加策略: {name}")
                else:
                    st.warning(f"⚠️ 策略 {name} 可能已存在")
            
            progress_bar.progress(20)
            
            # 2. 生成净值数据
            status_text.text("正在生成净值历史数据...")
            
            start_date = datetime(2023, 1, 1).date()
            end_date = datetime.now().date()
            
            # 为每个策略生成净值数据
            for strategy_id in strategy_ids:
                current_date = start_date
                current_nav = 1.000
                
                while current_date <= end_date:
                    # 跳过周末
                    if current_date.weekday() < 5:
                        # 生成随机收益率 (-3% 到 +3%)
                        daily_return = random.normalvariate(0.001, 0.015)  # 年化10%收益，15%波动
                        current_nav = current_nav * (1 + daily_return)
                        current_nav = max(0.1, current_nav)  # 确保净值不为负
                        
                        # 每周五录入净值
                        if current_date.weekday() == 4:  # 周五
                            db.add_nav_record(strategy_id, current_date.isoformat(), round(current_nav, 3))
                    
                    current_date += timedelta(days=1)
            
            st.success("✅ 净值数据生成完成")
            progress_bar.progress(50)
            
            # 3. 添加投资人
            status_text.text("正在添加投资人...")
            investors_data = [
                ("张三", "13800138000"),
                ("李四", "13900139000"),
                ("王五", "13700137000"),
                ("赵六", "13600136000"),
                ("钱七", "13500135000"),
                ("孙八", "13400134000"),
                ("周九", "13300133000"),
                ("吴十", "13200132000"),
                ("郑十一", "13100131000"),
                ("王十二", "13000130000"),
                ("机构投资者A", "021-12345678"),
                ("家族办公室B", "010-87654321"),
                ("私人银行客户C", "0755-11111111"),
                ("高净值客户D", "020-22222222"),
                ("企业年金E", "0571-33333333")
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
            
            # 为每个产品分配策略权重
            product_strategies = [
                # 稳健增长1号：市场中性40% + 量化多因子30% + 可转债套利30%
                (product_ids[0], [(strategy_ids[1], 0.4), (strategy_ids[0], 0.3), (strategy_ids[3], 0.3)]),
                # 进取增长2号：CTA40% + 事件驱动30% + 行业轮动30%
                (product_ids[1], [(strategy_ids[2], 0.4), (strategy_ids[6], 0.3), (strategy_ids[4], 0.3)]),
                # 平衡配置3号：均衡配置
                (product_ids[2], [(strategy_ids[0], 0.25), (strategy_ids[1], 0.25), (strategy_ids[4], 0.25), (strategy_ids[5], 0.25)]),
                # 价值精选4号：价值成长70% + 行业轮动30%
                (product_ids[3], [(strategy_ids[5], 0.7), (strategy_ids[4], 0.3)]),
                # 宏观配置5号：宏观对冲50% + CTA30% + 市场中性20%
                (product_ids[4], [(strategy_ids[7], 0.5), (strategy_ids[2], 0.3), (strategy_ids[1], 0.2)]),
                # 量化精英6号：量化多因子60% + 市场中性40%
                (product_ids[5], [(strategy_ids[0], 0.6), (strategy_ids[1], 0.4)]),
                # 套利稳健7号：可转债套利80% + 事件驱动20%
                (product_ids[6], [(strategy_ids[3], 0.8), (strategy_ids[6], 0.2)])
            ]
            
            for product_id, strategies in product_strategies:
                for strategy_id, weight in strategies:
                    db.set_product_strategy_weight(product_id, strategy_id, weight, "2023-01-01")
            
            st.success("✅ 产品策略权重配置完成")
            progress_bar.progress(85)
            
            # 6. 生成投资记录
            status_text.text("正在生成投资交易记录...")
            
            # 为每个投资人生成投资记录
            investment_amounts = [100000, 200000, 500000, 1000000, 2000000, 5000000, 10000000]
            
            for investor_id in investor_ids[:12]:  # 前12个投资人
                # 每个投资人投资1-3个产品
                num_products = random.randint(1, 3)
                selected_products = random.sample(product_ids, num_products)
                
                for product_id in selected_products:
                    # 初始投资
                    amount = random.choice(investment_amounts)
                    investment_date = random.choice([
                        "2023-01-15", "2023-02-01", "2023-03-01", "2023-04-01", 
                        "2023-05-01", "2023-06-01", "2023-07-01", "2023-08-01",
                        "2023-09-01", "2023-10-01", "2023-11-01", "2023-12-01",
                        "2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01",
                        "2024-05-01", "2024-06-01", "2024-07-01", "2024-08-01"
                    ])
                    
                    db.add_investment(investor_id, product_id, amount, investment_date, "investment")
                    
                    # 50%概率有追加投资
                    if random.random() < 0.5:
                        additional_amount = amount * random.uniform(0.2, 0.8)
                        later_date = (datetime.strptime(investment_date, "%Y-%m-%d") + timedelta(days=random.randint(30, 180))).strftime("%Y-%m-%d")
                        if datetime.strptime(later_date, "%Y-%m-%d").date() <= datetime.now().date():
                            db.add_investment(investor_id, product_id, additional_amount, later_date, "investment")
                    
                    # 20%概率有部分赎回
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

if __name__ == "__main__":
    generate_sample_data()

