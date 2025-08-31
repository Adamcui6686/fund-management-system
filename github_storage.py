#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub数据存储方案
将数据以JSON格式存储在GitHub仓库中
实现简单的数据共享
"""

import streamlit as st
import pandas as pd
import json
import requests
import base64
from datetime import datetime

class GitHubStorageManager:
    def __init__(self):
        # GitHub配置
        self.github_token = st.secrets.get("GITHUB_TOKEN", "")
        self.repo_owner = st.secrets.get("GITHUB_OWNER", "")
        self.repo_name = st.secrets.get("GITHUB_REPO", "")
        self.data_file = "fund_data.json"
        
        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def load_data(self):
        """从GitHub加载数据"""
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{self.data_file}"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                content = response.json()
                data = json.loads(base64.b64decode(content['content']).decode('utf-8'))
                return data, content['sha']
            else:
                # 文件不存在，返回空数据结构
                return self.get_empty_data_structure(), None
        except Exception as e:
            st.error(f"加载数据失败: {str(e)}")
            return self.get_empty_data_structure(), None
    
    def save_data(self, data, sha=None):
        """保存数据到GitHub"""
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{self.data_file}"
        
        content = base64.b64encode(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')).decode('utf-8')
        
        payload = {
            "message": f"更新数据 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "content": content
        }
        
        if sha:
            payload["sha"] = sha
        
        try:
            response = requests.put(url, headers=self.headers, json=payload)
            return response.status_code in [200, 201]
        except Exception as e:
            st.error(f"保存数据失败: {str(e)}")
            return False
    
    def get_empty_data_structure(self):
        """获取空的数据结构"""
        return {
            "strategies": [],
            "nav_records": [],
            "investors": [],
            "products": [],
            "product_weights": [],
            "investments": []
        }
    
    # 策略相关方法
    def add_strategy(self, name, description="", start_date=None, initial_nav=1.0):
        """添加策略"""
        data, sha = self.load_data()
        
        if start_date is None:
            start_date = datetime.now().date().isoformat()
        
        new_id = max([s.get('id', 0) for s in data['strategies']], default=0) + 1
        
        strategy = {
            "id": new_id,
            "name": name,
            "description": description,
            "start_date": start_date,
            "initial_nav": initial_nav,
            "created_at": datetime.now().isoformat()
        }
        
        data['strategies'].append(strategy)
        return self.save_data(data, sha)
    
    def get_strategies(self):
        """获取所有策略"""
        data, _ = self.load_data()
        return pd.DataFrame(data['strategies'])
    
    def add_nav_record(self, strategy_id, date, nav_value):
        """添加净值记录"""
        data, sha = self.load_data()
        
        # 计算收益率
        strategy_records = [r for r in data['nav_records'] if r['strategy_id'] == strategy_id]
        return_rate = None
        if strategy_records:
            last_record = max(strategy_records, key=lambda x: x['date'])
            return_rate = (nav_value - last_record['nav_value']) / last_record['nav_value'] * 100
        
        new_id = max([r.get('id', 0) for r in data['nav_records']], default=0) + 1
        
        record = {
            "id": new_id,
            "strategy_id": strategy_id,
            "date": date.isoformat() if hasattr(date, 'isoformat') else date,
            "nav_value": nav_value,
            "return_rate": return_rate,
            "created_at": datetime.now().isoformat()
        }
        
        # 移除重复记录
        data['nav_records'] = [r for r in data['nav_records'] 
                              if not (r['strategy_id'] == strategy_id and r['date'] == record['date'])]
        data['nav_records'].append(record)
        
        return self.save_data(data, sha)
    
    def get_nav_records(self, strategy_id=None, start_date=None, end_date=None):
        """获取净值记录"""
        data, _ = self.load_data()
        records = data['nav_records']
        
        if strategy_id:
            records = [r for r in records if r['strategy_id'] == strategy_id]
        
        df = pd.DataFrame(records)
        
        # 添加策略名称
        if not df.empty and not data['strategies']:
            strategies = {s['id']: s['name'] for s in data['strategies']}
            df['strategy_name'] = df['strategy_id'].map(strategies)
        
        return df
