#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
示例数据生成脚本
运行此脚本可以快速生成一些示例数据，帮助您体验系统功能
"""

from database import DatabaseManager
from datetime import datetime, timedelta
import random

def create_sample_data():
    """创建示例数据"""
    
    print("🚀 开始创建示例数据...")
    
    # 初始化数据库
    db = DatabaseManager()
    
    # 创建示例策略
    print("📊 创建示例策略...")
    
    strategies = [
        {
            'name': '股票多头策略',
            'description': '专注于A股优质成长股的多头策略',
            'start_date': datetime(2024, 1, 1).date(),
            'initial_nav': 1.0
        },
        {
            'name': '债券套利策略',
            'description': '国债与企业债之间的套利策略',
            'start_date': datetime(2024, 1, 1).date(),
            'initial_nav': 1.0
        },
        {
            'name': '量化中性策略',
            'description': '市场中性量化选股策略',
            'start_date': datetime(2024, 2, 1).date(),
            'initial_nav': 1.0
        }
    ]
    
    strategy_ids = []
    for strategy in strategies:
        try:
            strategy_id = db.add_strategy(
                strategy['name'],
                strategy['description'],
                strategy['start_date'],
                strategy['initial_nav']
            )
            strategy_ids.append(strategy_id)
            print(f"✅ 创建策略: {strategy['name']}")
        except Exception as e:
            print(f"⚠️  策略 {strategy['name']} 可能已存在")
    
    # 生成净值数据
    print("📈 生成净值数据...")
    
    # 生成每周的净值数据（从1月1日到现在）
    start_date = datetime(2024, 1, 1).date()
    end_date = datetime.now().date()
    
    current_date = start_date
    navs = [1.0, 1.0, 1.0]  # 三个策略的当前净值
    
    week_count = 0
    while current_date <= end_date:
        if current_date.weekday() == 4:  # 每周五录入净值
            week_count += 1
            
            for i, strategy_id in enumerate(strategy_ids):
                if i == 2 and current_date < datetime(2024, 2, 1).date():
                    # 量化中性策略2月才开始
                    continue
                
                # 模拟净值变化
                if i == 0:  # 股票多头策略 - 波动较大
                    change = random.uniform(-0.05, 0.08)
                elif i == 1:  # 债券套利策略 - 波动较小
                    change = random.uniform(-0.02, 0.03)
                else:  # 量化中性策略 - 稳定增长
                    change = random.uniform(-0.015, 0.025)
                
                navs[i] = max(0.1, navs[i] * (1 + change))
                
                try:
                    db.add_nav_record(strategy_id, current_date, round(navs[i], 3))
                except:
                    pass  # 忽略重复数据错误
        
        current_date += timedelta(days=1)
    
    print(f"✅ 生成了 {week_count} 周的净值数据")
    
    # 创建示例投资人
    print("👥 创建示例投资人...")
    
    investors = [
        {'name': '张三', 'contact': '13800138001'},
        {'name': '李四', 'contact': '13800138002'},
        {'name': '王五', 'contact': 'wangwu@email.com'},
        {'name': '赵六', 'contact': '13800138004'}
    ]
    
    for investor in investors:
        try:
            db.add_investor(investor['name'], investor['contact'])
            print(f"✅ 创建投资人: {investor['name']}")
        except:
            print(f"⚠️  投资人 {investor['name']} 可能已存在")
    
    # 创建示例产品
    print("📦 创建示例产品...")
    
    products = [
        {
            'name': '稳健增长组合',
            'description': '以债券策略为主，股票策略为辅的稳健型产品'
        },
        {
            'name': '积极成长组合',
            'description': '以股票多头为主的积极型产品'
        }
    ]
    
    product_ids = []
    for product in products:
        try:
            product_id = db.add_product(product['name'], product['description'])
            product_ids.append(product_id)
            print(f"✅ 创建产品: {product['name']}")
        except:
            print(f"⚠️  产品 {product['name']} 可能已存在")
    
    # 设置产品权重
    if len(product_ids) >= 2 and len(strategy_ids) >= 2:
        print("⚖️  设置产品权重...")
        
        try:
            # 稳健增长组合：60%债券 + 40%股票
            db.set_product_strategy_weight(product_ids[0], strategy_ids[1], 0.6)  # 债券60%
            db.set_product_strategy_weight(product_ids[0], strategy_ids[0], 0.4)  # 股票40%
            
            # 积极成长组合：70%股票 + 30%量化中性
            db.set_product_strategy_weight(product_ids[1], strategy_ids[0], 0.7)  # 股票70%
            if len(strategy_ids) >= 3:
                db.set_product_strategy_weight(product_ids[1], strategy_ids[2], 0.3)  # 量化30%
            
            print("✅ 产品权重配置完成")
        except Exception as e:
            print(f"⚠️  权重配置可能已存在")
    
    # 创建示例投资记录
    if len(product_ids) >= 2 and len(investors) >= 4:
        print("💰 创建示例投资记录...")
        
        try:
            # 获取投资人ID
            investor_ids = investors['id'].tolist()
            
            # 模拟投资记录
            import random
            
            investment_records = [
                # 张三投资稳健增长组合
                (investor_ids[0], product_ids[0], 100000, datetime(2024, 2, 1).date()),
                (investor_ids[0], product_ids[0], 50000, datetime(2024, 5, 1).date()),
                
                # 李四投资积极成长组合
                (investor_ids[1], product_ids[1], 200000, datetime(2024, 1, 15).date()),
                (investor_ids[1], product_ids[1], -50000, datetime(2024, 8, 1).date()),  # 赎回
                
                # 王五投资两个产品
                (investor_ids[2], product_ids[0], 80000, datetime(2024, 3, 1).date()),
                (investor_ids[2], product_ids[1], 120000, datetime(2024, 4, 1).date()),
                
                # 赵六投资稳健增长组合
                (investor_ids[3], product_ids[0], 150000, datetime(2024, 6, 1).date()),
            ]
            
            for investor_id, product_id, amount, invest_date in investment_records:
                investment_type = "investment" if amount > 0 else "redemption"
                db.add_investment(investor_id, product_id, amount, invest_date, investment_type)
            
            print("✅ 投资记录创建完成")
        except Exception as e:
            print(f"⚠️  投资记录创建失败: {e}")
    
    print("\n🎉 示例数据创建完成！")
    print("\n📋 创建的示例数据包括：")
    print("   • 3个投资策略（股票多头、债券套利、量化中性）")
    print(f"   • {week_count}周的净值数据")
    print("   • 4个示例投资人")
    print("   • 2个示例产品组合")
    print("   • 产品策略权重配置")
    print("   • 示例投资记录（申购、赎回）")
    
    print("\n🚀 现在您可以运行以下命令启动系统：")
    print("   streamlit run app.py")
    print("\n或者双击 '启动系统.sh' 文件")

if __name__ == "__main__":
    create_sample_data()
