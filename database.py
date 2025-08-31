import sqlite3
import pandas as pd
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_path="fund_management.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 策略表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                start_date DATE,
                initial_nav REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 净值记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nav_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_id INTEGER,
                date DATE NOT NULL,
                nav_value REAL NOT NULL,
                return_rate REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (strategy_id) REFERENCES strategies (id),
                UNIQUE(strategy_id, date)
            )
        ''')
        
        # 投资人表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS investors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 投资记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS investments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                investor_id INTEGER,
                product_id INTEGER,
                investment_date DATE NOT NULL,
                amount REAL NOT NULL,
                shares REAL,
                nav_at_investment REAL,
                type TEXT CHECK(type IN ('investment', 'redemption')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (investor_id) REFERENCES investors (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # 产品表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 产品策略权重表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_strategy_weights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                strategy_id INTEGER,
                weight REAL NOT NULL,
                effective_date DATE,
                FOREIGN KEY (product_id) REFERENCES products (id),
                FOREIGN KEY (strategy_id) REFERENCES strategies (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query, params=None):
        """执行查询"""
        conn = sqlite3.connect(self.db_path)
        if params:
            result = pd.read_sql_query(query, conn, params=params)
        else:
            result = pd.read_sql_query(query, conn)
        conn.close()
        return result
    
    def execute_command(self, command, params=None):
        """执行命令（INSERT, UPDATE, DELETE）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if params:
            cursor.execute(command, params)
        else:
            cursor.execute(command)
        conn.commit()
        lastrowid = cursor.lastrowid
        conn.close()
        return lastrowid
    
    # 策略相关方法
    def add_strategy(self, name, description="", start_date=None, initial_nav=1.0):
        """添加策略"""
        if start_date is None:
            start_date = datetime.now().date()
        
        command = """
            INSERT INTO strategies (name, description, start_date, initial_nav)
            VALUES (?, ?, ?, ?)
        """
        return self.execute_command(command, (name, description, start_date, initial_nav))
    
    def get_strategies(self):
        """获取所有策略"""
        query = "SELECT * FROM strategies ORDER BY created_at"
        return self.execute_query(query)
    
    def get_strategy_by_id(self, strategy_id):
        """根据ID获取策略"""
        query = "SELECT * FROM strategies WHERE id = ?"
        return self.execute_query(query, (strategy_id,))
    
    # 净值记录相关方法
    def add_nav_record(self, strategy_id, date, nav_value):
        """添加净值记录"""
        # 计算收益率
        last_nav = self.get_last_nav(strategy_id, date)
        return_rate = None
        if last_nav is not None:
            return_rate = (nav_value - last_nav) / last_nav * 100
        
        command = """
            INSERT OR REPLACE INTO nav_records (strategy_id, date, nav_value, return_rate)
            VALUES (?, ?, ?, ?)
        """
        return self.execute_command(command, (strategy_id, date, nav_value, return_rate))
    
    def get_last_nav(self, strategy_id, before_date):
        """获取指定日期前的最后一个净值"""
        query = """
            SELECT nav_value FROM nav_records 
            WHERE strategy_id = ? AND date < ? 
            ORDER BY date DESC LIMIT 1
        """
        result = self.execute_query(query, (strategy_id, before_date))
        return result['nav_value'].iloc[0] if not result.empty else None
    
    def get_nav_records(self, strategy_id=None, start_date=None, end_date=None):
        """获取净值记录"""
        query = """
            SELECT nr.*, s.name as strategy_name 
            FROM nav_records nr
            JOIN strategies s ON nr.strategy_id = s.id
        """
        conditions = []
        params = []
        
        if strategy_id:
            conditions.append("nr.strategy_id = ?")
            params.append(strategy_id)
        
        if start_date:
            conditions.append("nr.date >= ?")
            params.append(start_date)
        
        if end_date:
            conditions.append("nr.date <= ?")
            params.append(end_date)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY nr.date"
        
        return self.execute_query(query, params if params else None)
    
    # 投资人相关方法
    def add_investor(self, name, contact=""):
        """添加投资人"""
        command = "INSERT INTO investors (name, contact) VALUES (?, ?)"
        return self.execute_command(command, (name, contact))
    
    def get_investors(self):
        """获取所有投资人"""
        query = "SELECT * FROM investors ORDER BY name"
        return self.execute_query(query)
    
    # 产品相关方法
    def add_product(self, name, description=""):
        """添加产品"""
        command = "INSERT INTO products (name, description) VALUES (?, ?)"
        return self.execute_command(command, (name, description))
    
    def get_products(self):
        """获取所有产品"""
        query = "SELECT * FROM products ORDER BY name"
        return self.execute_query(query)
    
    def set_product_strategy_weight(self, product_id, strategy_id, weight, effective_date=None):
        """设置产品策略权重"""
        if effective_date is None:
            effective_date = datetime.now().date()
        
        command = """
            INSERT OR REPLACE INTO product_strategy_weights 
            (product_id, strategy_id, weight, effective_date)
            VALUES (?, ?, ?, ?)
        """
        return self.execute_command(command, (product_id, strategy_id, weight, effective_date))
    
    def get_product_weights(self, product_id, date=None):
        """获取产品策略权重"""
        if date is None:
            date = datetime.now().date()
        
        query = """
            SELECT psw.*, s.name as strategy_name
            FROM product_strategy_weights psw
            JOIN strategies s ON psw.strategy_id = s.id
            WHERE psw.product_id = ? AND psw.effective_date <= ?
            ORDER BY psw.strategy_id, psw.effective_date DESC
        """
        
        result = self.execute_query(query, (product_id, date))
        
        # 获取每个策略的最新权重
        if not result.empty:
            latest_weights = result.groupby('strategy_id').first().reset_index()
            return latest_weights
        return result
    
    # 投资记录相关方法
    def add_investment(self, investor_id, product_id, amount, investment_date=None, investment_type='investment'):
        """添加投资记录"""
        if investment_date is None:
            investment_date = datetime.now().date()
        
        # 获取投资时的产品净值
        nav_at_investment = self.calculate_product_nav(product_id, investment_date)
        
        # 计算份额
        shares = amount / nav_at_investment if nav_at_investment > 0 else 0
        
        command = """
            INSERT INTO investments (investor_id, product_id, investment_date, amount, shares, nav_at_investment, type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_command(command, (investor_id, product_id, investment_date, amount, shares, nav_at_investment, investment_type))
    
    def get_investor_investments(self, investor_id=None, product_id=None):
        """获取投资记录"""
        query = """
            SELECT i.*, inv.name as investor_name, p.name as product_name
            FROM investments i
            JOIN investors inv ON i.investor_id = inv.id
            JOIN products p ON i.product_id = p.id
        """
        conditions = []
        params = []
        
        if investor_id:
            conditions.append("i.investor_id = ?")
            params.append(investor_id)
        
        if product_id:
            conditions.append("i.product_id = ?")
            params.append(product_id)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY i.investment_date DESC"
        
        return self.execute_query(query, params if params else None)
    
    def calculate_product_nav(self, product_id, date=None):
        """计算产品净值（基于策略权重）"""
        if date is None:
            date = datetime.now().date()
        
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
    
    def get_strategy_nav_at_date(self, strategy_id, date):
        """获取策略在指定日期的净值"""
        query = """
            SELECT nav_value FROM nav_records 
            WHERE strategy_id = ? AND date <= ? 
            ORDER BY date DESC LIMIT 1
        """
        result = self.execute_query(query, (strategy_id, date))
        return result['nav_value'].iloc[0] if not result.empty else None
    
    def get_investor_portfolio(self, investor_id):
        """获取投资人持仓信息"""
        query = """
            SELECT 
                p.name as product_name,
                p.id as product_id,
                SUM(CASE WHEN i.type = 'investment' THEN i.amount ELSE -i.amount END) as total_investment,
                SUM(CASE WHEN i.type = 'investment' THEN i.shares ELSE -i.shares END) as total_shares,
                COUNT(*) as transaction_count
            FROM investments i
            JOIN products p ON i.product_id = p.id
            WHERE i.investor_id = ?
            GROUP BY p.id, p.name
            HAVING total_shares > 0
        """
        
        portfolio = self.execute_query(query, (investor_id,))
        
        if not portfolio.empty:
            # 计算当前市值和收益
            for idx, row in portfolio.iterrows():
                current_nav = self.calculate_product_nav(row['product_id'])
                current_value = row['total_shares'] * current_nav
                profit_loss = current_value - row['total_investment']
                profit_rate = (profit_loss / row['total_investment']) * 100 if row['total_investment'] > 0 else 0
                
                portfolio.loc[idx, 'current_nav'] = current_nav
                portfolio.loc[idx, 'current_value'] = current_value
                portfolio.loc[idx, 'profit_loss'] = profit_loss
                portfolio.loc[idx, 'profit_rate'] = profit_rate
        
        return portfolio
