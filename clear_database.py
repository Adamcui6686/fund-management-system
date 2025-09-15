#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清空数据库脚本
删除所有表数据，保留表结构
"""

import sqlite3
import os

def clear_database():
    """清空数据库中的所有数据"""
    
    # 数据库文件路径
    db_path = "fund_management.db"
    
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在")
        return
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🗑️  开始清空数据库...")
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = cursor.fetchall()
        
        if not tables:
            print("ℹ️  数据库中没有用户表")
            return
        
        # 禁用外键约束
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        # 清空每个表
        for table in tables:
            table_name = table[0]
            cursor.execute(f"DELETE FROM {table_name}")
            print(f"✅ 已清空表: {table_name}")
        
        # 重置自增ID
        for table in tables:
            table_name = table[0]
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}'")
        
        # 启用外键约束
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # 提交更改
        conn.commit()
        
        print("🎉 数据库清空完成！")
        print("📊 已清空的表:")
        for table in tables:
            print(f"   - {table[0]}")
        
        print("\n💡 提示:")
        print("   - 所有数据已删除")
        print("   - 表结构保持不变")
        print("   - 可以重新开始录入数据")
        
    except Exception as e:
        print(f"❌ 清空数据库失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚨 警告: 此操作将删除所有数据！")
    confirm = input("确认清空数据库？(输入 'yes' 确认): ")
    
    if confirm.lower() == 'yes':
        clear_database()
    else:
        print("❌ 操作已取消")

