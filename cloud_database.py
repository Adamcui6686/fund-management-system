#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
云数据库版本 - 支持多用户数据共享
使用 Supabase (免费的PostgreSQL云数据库)
"""

import os
import pandas as pd
import streamlit as st
from datetime import datetime
import requests
import json

class CloudDatabaseManager:
    def __init__(self):
        # Supabase配置 (免费PostgreSQL云数据库)
        self.supabase_url = st.secrets.get("SUPABASE_URL", "")
        self.supabase_key = st.secrets.get("SUPABASE_ANON_KEY", "")
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json"
        }
    
    def execute_query(self, table, method="GET", data=None, filters=None):
        """执行API查询"""
        url = f"{self.supabase_url}/rest/v1/{table}"
        
        if filters:
            params = "&".join([f"{k}=eq.{v}" for k, v in filters.items()])
            url += f"?{params}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PATCH":
                response = requests.patch(url, headers=self.headers, json=data)
            
            if response.status_code in [200, 201]:
                return pd.DataFrame(response.json())
            else:
                st.error(f"数据库错误: {response.text}")
                return pd.DataFrame()
        
        except Exception as e:
            st.error(f"连接数据库失败: {str(e)}")
            return pd.DataFrame()
    
    # 策略相关方法
    def add_strategy(self, name, description="", start_date=None, initial_nav=1.0):
        """添加策略"""
        if start_date is None:
            start_date = datetime.now().date().isoformat()
        
        data = {
            "name": name,
            "description": description,
            "start_date": start_date,
            "initial_nav": initial_nav
        }
        
        result = self.execute_query("strategies", "POST", data)
        return not result.empty
    
    def get_strategies(self):
        """获取所有策略"""
        return self.execute_query("strategies")
    
    # 净值记录相关方法
    def add_nav_record(self, strategy_id, date, nav_value):
        """添加净值记录"""
        # 计算收益率
        last_nav = self.get_last_nav(strategy_id, date)
        return_rate = None
        if last_nav is not None:
            return_rate = (nav_value - last_nav) / last_nav * 100
        
        data = {
            "strategy_id": strategy_id,
            "date": date.isoformat() if hasattr(date, 'isoformat') else date,
            "nav_value": nav_value,
            "return_rate": return_rate
        }
        
        result = self.execute_query("nav_records", "POST", data)
        return not result.empty
    
    def get_last_nav(self, strategy_id, before_date):
        """获取指定日期前的最后一个净值"""
        # 这里需要更复杂的查询，简化处理
        records = self.execute_query("nav_records", filters={"strategy_id": strategy_id})
        if not records.empty:
            records['date'] = pd.to_datetime(records['date'])
            filtered = records[records['date'] < pd.to_datetime(before_date)]
            if not filtered.empty:
                return filtered.sort_values('date').iloc[-1]['nav_value']
        return None
    
    def get_nav_records(self, strategy_id=None, start_date=None, end_date=None):
        """获取净值记录"""
        if strategy_id:
            return self.execute_query("nav_records", filters={"strategy_id": strategy_id})
        else:
            return self.execute_query("nav_records")
    
    # 投资人相关方法
    def add_investor(self, name, contact=""):
        """添加投资人"""
        data = {"name": name, "contact": contact}
        result = self.execute_query("investors", "POST", data)
        return not result.empty
    
    def get_investors(self):
        """获取所有投资人"""
        return self.execute_query("investors")
    
    # 产品相关方法
    def add_product(self, name, description=""):
        """添加产品"""
        data = {"name": name, "description": description}
        result = self.execute_query("products", "POST", data)
        return not result.empty
    
    def get_products(self):
        """获取所有产品"""
        return self.execute_query("products")
