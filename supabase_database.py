#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Supabase云数据库管理器
支持多用户实时数据共享
"""

import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
from typing import Optional, Dict, Any

class SupabaseManager:
    def __init__(self):
        """初始化Supabase连接"""
        try:
            self.supabase_url = st.secrets["SUPABASE_URL"]
            self.supabase_key = st.secrets["SUPABASE_ANON_KEY"]
            
            # 验证配置是否有效
            if not self.supabase_url or not self.supabase_key:
                raise KeyError("配置为空")
                
        except (KeyError, AttributeError) as e:
            # 如果无法获取密钥，抛出异常让应用回退到本地数据库
            raise Exception(f"Supabase配置错误: {str(e)}")
        
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> pd.DataFrame:
        """发送HTTP请求到Supabase"""
        url = f"{self.supabase_url}/rest/v1/{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PATCH":
                response = requests.patch(url, headers=self.headers, json=data, params=params)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers, params=params)
            
            if response.status_code in [200, 201]:
                result = response.json()
                return pd.DataFrame(result) if result else pd.DataFrame()
            else:
                st.error(f"数据库操作失败: {response.status_code} - {response.text}")
                return pd.DataFrame()
                
        except requests.exceptions.RequestException as e:
            st.error(f"网络连接失败: {str(e)}")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"未知错误: {str(e)}")
            return pd.DataFrame()
    
    # 策略管理
    def add_strategy(self, name: str, description: str = "", start_date: Optional[str] = None, initial_nav: float = 1.000) -> bool:
        """添加新策略"""
        if start_date is None:
            start_date = datetime.now().date().isoformat()
        elif hasattr(start_date, 'isoformat'):
            start_date = start_date.isoformat()
        else:
            start_date = str(start_date)
        
        data = {
            "name": name,
            "description": description,
            "start_date": start_date,
            "initial_nav": float(initial_nav)
        }
        
        result = self._make_request("POST", "strategies", data)
        return not result.empty
    
    def get_strategies(self) -> pd.DataFrame:
        """获取所有策略"""
        return self._make_request("GET", "strategies", params={"order": "created_at"})
    
    def get_strategy_by_id(self, strategy_id: int) -> pd.DataFrame:
        """根据ID获取策略"""
        params = {"id": f"eq.{strategy_id}"}
        return self._make_request("GET", "strategies", params=params)
    
    # 净值记录管理
    def add_nav_record(self, strategy_id: int, date: str, nav_value: float) -> bool:
        """添加净值记录"""
        # 处理日期格式
        if hasattr(date, 'isoformat'):
            date = date.isoformat()
        else:
            date = str(date)
            
        # 计算收益率
        last_nav = self.get_last_nav(strategy_id, date)
        return_rate = None
        if last_nav is not None:
            return_rate = (nav_value - last_nav) / last_nav * 100
        
        data = {
            "strategy_id": int(strategy_id),
            "date": date,
            "nav_value": float(nav_value),
            "return_rate": float(return_rate) if return_rate is not None else None
        }
        
        # 使用upsert避免重复数据
        endpoint = "nav_records"
        params = {"on_conflict": "strategy_id,date"}
        result = self._make_request("POST", endpoint, data)
        return not result.empty
    
    def get_last_nav(self, strategy_id: int, before_date: str) -> Optional[float]:
        """获取指定日期前的最后一个净值"""
        params = {
            "strategy_id": f"eq.{strategy_id}",
            "date": f"lt.{before_date}",
            "order": "date.desc",
            "limit": 1
        }
        result = self._make_request("GET", "nav_records", params=params)
        
        if not result.empty:
            return float(result.iloc[0]['nav_value'])
        return None
    
    def get_nav_records(self, strategy_id: Optional[int] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """获取净值记录"""
        params = {"order": "date.asc"}
        
        filters = []
        if strategy_id:
            filters.append(f"strategy_id.eq.{strategy_id}")
        if start_date:
            filters.append(f"date.gte.{start_date}")
        if end_date:
            filters.append(f"date.lte.{end_date}")
        
        if filters:
            params["and"] = f"({','.join(filters)})"
        
        # 联表查询获取策略名称
        params["select"] = "*, strategies(name)"
        
        result = self._make_request("GET", "nav_records", params=params)
        
        # 处理联表结果
        if not result.empty and 'strategies' in result.columns:
            result['strategy_name'] = result['strategies'].apply(lambda x: x['name'] if x else '')
            result = result.drop('strategies', axis=1)
        
        return result
    
    # 投资人管理
    def add_investor(self, name: str, contact: str = "") -> bool:
        """添加投资人"""
        data = {"name": name, "contact": contact}
        result = self._make_request("POST", "investors", data)
        return not result.empty
    
    def get_investors(self) -> pd.DataFrame:
        """获取所有投资人"""
        return self._make_request("GET", "investors", params={"order": "name"})
    
    # 产品管理
    def add_product(self, name: str, description: str = "") -> bool:
        """添加产品"""
        data = {"name": name, "description": description}
        result = self._make_request("POST", "products", data)
        return not result.empty
    
    def get_products(self) -> pd.DataFrame:
        """获取所有产品"""
        return self._make_request("GET", "products", params={"order": "name"})
    
    def set_product_strategy_weight(self, product_id: int, strategy_id: int, weight: float, effective_date: Optional[str] = None) -> bool:
        """设置产品策略权重"""
        if effective_date is None:
            effective_date = datetime.now().date().isoformat()
        elif hasattr(effective_date, 'isoformat'):
            effective_date = effective_date.isoformat()
        else:
            effective_date = str(effective_date)
        
        # 先删除该产品和策略的旧权重配置
        delete_params = {
            "product_id": f"eq.{product_id}",
            "strategy_id": f"eq.{strategy_id}",
            "effective_date": f"eq.{effective_date}"
        }
        
        try:
            self._make_request("DELETE", "product_strategy_weights", params=delete_params)
        except:
            pass  # 忽略删除失败的情况
        
        # 添加新的权重配置
        data = {
            "product_id": int(product_id),
            "strategy_id": int(strategy_id),
            "weight": float(weight),
            "effective_date": effective_date
        }
        
        result = self._make_request("POST", "product_strategy_weights", data)
        return not result.empty
    
    def get_product_weights(self, product_id: int, date: Optional[str] = None) -> pd.DataFrame:
        """获取产品策略权重"""
        if date is None:
            date = datetime.now().date().isoformat()
        
        params = {
            "product_id": f"eq.{product_id}",
            "effective_date": f"lte.{date}",
            "select": "*, strategies(name)",
            "order": "strategy_id,effective_date.desc"
        }
        
        result = self._make_request("GET", "product_strategy_weights", params=params)
        
        if not result.empty:
            # 处理联表结果
            if 'strategies' in result.columns:
                result['strategy_name'] = result['strategies'].apply(lambda x: x['name'] if x else '')
                result = result.drop('strategies', axis=1)
            
            # 获取每个策略的最新权重
            latest_weights = result.groupby('strategy_id').first().reset_index()
            return latest_weights
        
        return result
    
    # 投资记录管理
    def add_investment(self, investor_id: int, product_id: int, amount: float, investment_date: Optional[str] = None, investment_type: str = 'investment') -> bool:
        """添加投资记录"""
        if investment_date is None:
            investment_date = datetime.now().date().isoformat()
        
        # 获取投资时的产品净值
        nav_at_investment = self.calculate_product_nav(product_id, investment_date)
        
        # 计算份额
        shares = amount / nav_at_investment if nav_at_investment > 0 else 0
        
        data = {
            "investor_id": investor_id,
            "product_id": product_id,
            "investment_date": investment_date,
            "amount": amount,
            "shares": shares,
            "nav_at_investment": nav_at_investment,
            "type": investment_type
        }
        
        result = self._make_request("POST", "investments", data)
        return not result.empty
    
    def get_investor_investments(self, investor_id: Optional[int] = None, product_id: Optional[int] = None) -> pd.DataFrame:
        """获取投资记录"""
        params = {
            "select": "*, investors(name), products(name)",
            "order": "investment_date.desc"
        }
        
        filters = []
        if investor_id:
            filters.append(f"investor_id.eq.{investor_id}")
        if product_id:
            filters.append(f"product_id.eq.{product_id}")
        
        if filters:
            params["and"] = f"({','.join(filters)})"
        
        result = self._make_request("GET", "investments", params=params)
        
        # 处理联表结果
        if not result.empty:
            if 'investors' in result.columns:
                result['investor_name'] = result['investors'].apply(lambda x: x['name'] if x else '')
                result = result.drop('investors', axis=1)
            if 'products' in result.columns:
                result['product_name'] = result['products'].apply(lambda x: x['name'] if x else '')
                result = result.drop('products', axis=1)
        
        return result
    
    def calculate_product_nav(self, product_id: int, date: Optional[str] = None) -> float:
        """计算产品净值"""
        if date is None:
            date = datetime.now().date().isoformat()
        
        # 获取产品权重
        weights = self.get_product_weights(product_id, date)
        
        if weights.empty:
            return 1.0
        
        total_nav = 0
        total_weight = 0
        
        for _, weight_row in weights.iterrows():
            strategy_id = weight_row['strategy_id']
            weight = weight_row['weight']
            
            # 获取策略在指定日期的净值
            strategy_nav = self.get_strategy_nav_at_date(strategy_id, date)
            
            if strategy_nav is not None:
                total_nav += strategy_nav * weight
                total_weight += weight
        
        return total_nav / total_weight if total_weight > 0 else 1.0
    
    def get_strategy_nav_at_date(self, strategy_id: int, date: str) -> Optional[float]:
        """获取策略在指定日期的净值"""
        params = {
            "strategy_id": f"eq.{strategy_id}",
            "date": f"lte.{date}",
            "order": "date.desc",
            "limit": 1
        }
        result = self._make_request("GET", "nav_records", params=params)
        
        if not result.empty:
            return float(result.iloc[0]['nav_value'])
        return None
    
    def get_investor_portfolio(self, investor_id: int) -> pd.DataFrame:
        """获取投资人持仓信息"""
        # 由于Supabase的限制，我们需要在应用层进行聚合计算
        investments = self.get_investor_investments(investor_id)
        
        if investments.empty:
            return pd.DataFrame()
        
        # 按产品聚合
        portfolio_data = []
        for product_id in investments['product_id'].unique():
            product_investments = investments[investments['product_id'] == product_id]
            
            total_investment = product_investments[product_investments['type'] == 'investment']['amount'].sum()
            total_redemption = abs(product_investments[product_investments['type'] == 'redemption']['amount'].sum())
            net_investment = total_investment - total_redemption
            
            total_shares = product_investments[product_investments['type'] == 'investment']['shares'].sum()
            total_redeemed_shares = abs(product_investments[product_investments['type'] == 'redemption']['shares'].sum())
            net_shares = total_shares - total_redeemed_shares
            
            if net_shares > 0:
                current_nav = self.calculate_product_nav(product_id)
                current_value = net_shares * current_nav
                profit_loss = current_value - net_investment
                profit_rate = (profit_loss / net_investment * 100) if net_investment > 0 else 0
                
                portfolio_data.append({
                    'product_name': product_investments.iloc[0]['product_name'],
                    'product_id': product_id,
                    'total_investment': net_investment,
                    'total_shares': net_shares,
                    'current_nav': current_nav,
                    'current_value': current_value,
                    'profit_loss': profit_loss,
                    'profit_rate': profit_rate,
                    'transaction_count': len(product_investments)
                })
        
        return pd.DataFrame(portfolio_data)
