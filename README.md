# 私募基金净值管理系统

## 🌟 功能特点

- 📊 多策略管理和净值追踪
- 💰 投资人资金进出管理
- 📈 产品组合和权重配置
- 📊 可视化图表分析
- 👥 多人协作数据共享
- 🌐 云端部署，随时随地访问

## 🚀 在线访问

**系统地址**: [即将部署到Streamlit Cloud]

## 💻 本地运行

### 环境要求
- Python 3.8+
- Conda 或 pip

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/你的用户名/fund-management-system.git
cd fund-management-system
```

2. **创建虚拟环境**
```bash
conda create -n fund_management python=3.9
conda activate fund_management
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **运行应用**
```bash
streamlit run app.py
```

5. **访问系统**
打开浏览器访问: http://localhost:8501

## 🏗️ 系统架构

- **前端**: Streamlit Web应用
- **后端**: Python + Pandas数据处理
- **数据库**: 
  - 本地开发: SQLite
  - 云端部署: Supabase PostgreSQL
- **图表**: Plotly交互式图表
- **部署**: Streamlit Cloud

## 📋 功能模块

### 1. 数据概览
- 系统统计信息
- 最新净值记录

### 2. 策略管理
- 添加投资策略
- 策略列表查看

### 3. 净值录入
- 单个净值录入
- 批量净值录入

### 4. 投资人管理
- 投资人信息管理
- 投资申购记录
- 持仓查询分析

### 5. 产品管理
- 产品创建
- 策略权重配置

### 6. 图表分析
- 净值曲线图
- 收益率分析
- 策略对比

## 🔧 配置说明

### 云端部署配置
在Streamlit Cloud中配置以下环境变量:
```toml
SUPABASE_URL = "你的Supabase项目URL"
SUPABASE_ANON_KEY = "你的Supabase API密钥"
```

## 📞 技术支持

如有问题，请联系系统管理员。

---

*私募基金净值管理系统 © 2024*