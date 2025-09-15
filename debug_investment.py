#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试投资申购和持仓查询问题
"""

import streamlit as st
from supabase_database import SupabaseManager

def debug_investment_issue():
    """调试投资申购问题"""
    st.title("🔍 调试投资申购问题")
    
    try:
        db = SupabaseManager()
        st.success("✅ 成功连接Supabase数据库")
        
        # 1. 检查投资人数据
        st.subheader("1. 检查投资人数据")
        investors = db.get_investors()
        if not investors.empty:
            st.dataframe(investors)
        else:
            st.warning("❌ 没有投资人数据")
            return
        
        # 2. 检查产品数据
        st.subheader("2. 检查产品数据")
        products = db.get_products()
        if not products.empty:
            st.dataframe(products)
        else:
            st.warning("❌ 没有产品数据")
            return
        
        # 3. 检查投资记录
        st.subheader("3. 检查所有投资记录")
        all_investments = db.get_investor_investments()
        if not all_investments.empty:
            st.dataframe(all_investments)
        else:
            st.warning("❌ 没有投资记录")
        
        # 4. 测试添加投资记录
        st.subheader("4. 测试添加投资记录")
        if st.button("添加测试投资记录"):
            try:
                investor_id = investors.iloc[0]['id']
                product_id = products.iloc[0]['id']
                amount = 100000.0
                investment_date = "2024-01-01"
                
                st.write(f"添加投资记录:")
                st.write(f"- 投资人ID: {investor_id}")
                st.write(f"- 产品ID: {product_id}")
                st.write(f"- 金额: {amount}")
                st.write(f"- 日期: {investment_date}")
                
                result = db.add_investment(investor_id, product_id, amount, investment_date, "investment")
                
                if result:
                    st.success("✅ 投资记录添加成功")
                else:
                    st.error("❌ 投资记录添加失败")
                    
                # 重新检查投资记录
                st.write("重新检查投资记录:")
                updated_investments = db.get_investor_investments()
                if not updated_investments.empty:
                    st.dataframe(updated_investments)
                    
            except Exception as e:
                st.error(f"❌ 添加投资记录时出错: {e}")
        
        # 5. 测试持仓查询
        st.subheader("5. 测试持仓查询")
        if not investors.empty:
            investor_id = investors.iloc[0]['id']
            investor_name = investors.iloc[0]['name']
            
            st.write(f"查询投资人 {investor_name} (ID: {investor_id}) 的持仓:")
            
            portfolio = db.get_investor_portfolio(investor_id)
            if not portfolio.empty:
                st.dataframe(portfolio)
            else:
                st.warning(f"❌ 投资人 {investor_name} 没有持仓数据")
        
        # 6. 检查产品净值计算
        st.subheader("6. 检查产品净值计算")
        if not products.empty:
            product_id = products.iloc[0]['id']
            product_name = products.iloc[0]['name']
            
            current_nav = db.calculate_product_nav(product_id)
            st.write(f"产品 {product_name} (ID: {product_id}) 的当前净值: {current_nav}")
            
            if current_nav is None:
                st.warning("❌ 无法获取产品净值，可能没有策略权重配置或净值记录")
        
    except Exception as e:
        st.error(f"❌ 连接数据库失败: {e}")

if __name__ == "__main__":
    debug_investment_issue()
