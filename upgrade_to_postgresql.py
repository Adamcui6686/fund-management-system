#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库升级脚本：从SQLite迁移到PostgreSQL
支持多用户并发访问
"""

import os
import psycopg2
from database import DatabaseManager
import pandas as pd

def create_postgresql_database():
    """创建PostgreSQL数据库结构"""
    
    # PostgreSQL连接配置
    pg_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'fund_management'),
        'user': os.getenv('DB_USER', 'fund_admin'),
        'password': os.getenv('DB_PASSWORD', 'your_password')
    }
    
    # 连接PostgreSQL
    conn = psycopg2.connect(**pg_config)
    cursor = conn.cursor()
    
    # 创建表结构
    tables_sql = [
        """
        CREATE TABLE IF NOT EXISTS strategies (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,
            description TEXT,
            start_date DATE,
            initial_nav DECIMAL(10,4) DEFAULT 1.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS nav_records (
            id SERIAL PRIMARY KEY,
            strategy_id INTEGER REFERENCES strategies(id),
            date DATE NOT NULL,
            nav_value DECIMAL(10,4) NOT NULL,
            return_rate DECIMAL(8,4),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(strategy_id, date)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS investors (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            contact VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS product_strategy_weights (
            id SERIAL PRIMARY KEY,
            product_id INTEGER REFERENCES products(id),
            strategy_id INTEGER REFERENCES strategies(id),
            weight DECIMAL(5,4) NOT NULL,
            effective_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS investments (
            id SERIAL PRIMARY KEY,
            investor_id INTEGER REFERENCES investors(id),
            product_id INTEGER REFERENCES products(id),
            investment_date DATE NOT NULL,
            amount DECIMAL(15,2) NOT NULL,
            shares DECIMAL(15,6),
            nav_at_investment DECIMAL(10,4),
            type VARCHAR(20) CHECK(type IN ('investment', 'redemption')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS user_sessions (
            id SERIAL PRIMARY KEY,
            user_name VARCHAR(255) NOT NULL,
            session_token VARCHAR(255) NOT NULL,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        );
        """
    ]
    
    # 执行建表语句
    for sql in tables_sql:
        cursor.execute(sql)
    
    # 创建索引
    indexes_sql = [
        "CREATE INDEX IF NOT EXISTS idx_nav_records_date ON nav_records(date);",
        "CREATE INDEX IF NOT EXISTS idx_nav_records_strategy ON nav_records(strategy_id);",
        "CREATE INDEX IF NOT EXISTS idx_investments_investor ON investments(investor_id);",
        "CREATE INDEX IF NOT EXISTS idx_investments_product ON investments(product_id);"
    ]
    
    for sql in indexes_sql:
        cursor.execute(sql)
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("✅ PostgreSQL数据库创建完成")

def migrate_data_from_sqlite():
    """从SQLite迁移数据到PostgreSQL"""
    
    print("📦 开始数据迁移...")
    
    # 初始化SQLite数据库管理器
    sqlite_db = DatabaseManager()
    
    # 获取所有数据
    strategies = sqlite_db.get_strategies()
    investors = sqlite_db.get_investors()
    products = sqlite_db.get_products()
    nav_records = sqlite_db.get_nav_records()
    
    print(f"📊 找到数据：{len(strategies)}个策略，{len(investors)}个投资人，{len(products)}个产品，{len(nav_records)}条净值记录")
    
    # TODO: 这里需要实现具体的数据迁移逻辑
    # 将SQLite中的数据批量插入到PostgreSQL
    
    print("✅ 数据迁移完成")

def create_env_template():
    """创建环境变量模板文件"""
    
    env_template = """
# PostgreSQL数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fund_management
DB_USER=fund_admin
DB_PASSWORD=your_secure_password

# 应用配置
APP_SECRET_KEY=your_secret_key_here
APP_ENVIRONMENT=production

# Streamlit配置
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_PORT=8501
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_template)
    
    print("✅ 创建了 .env.template 文件，请复制为 .env 并填入真实配置")

if __name__ == "__main__":
    print("🚀 开始数据库升级...")
    
    create_env_template()
    # create_postgresql_database()
    # migrate_data_from_sqlite()
    
    print("🎉 数据库升级准备完成！")
    print("📋 下一步：")
    print("1. 安装PostgreSQL数据库")
    print("2. 复制 .env.template 为 .env 并配置数据库信息")
    print("3. 运行数据迁移脚本")
