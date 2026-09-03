# 销售数据可视化看板

基于 SQLite + Python + ECharts 的企业级销售数据分析看板。

## 项目概述

本项目模拟了一套电商平台的销售数据，通过 SQLite 进行数据清洗与多维分析，最终生成包含 6 大核心图表的静态 HTML 看板，支持离线查看与部署。

## 核心功能

| 模块 | 说明 |
|------|------|
| 数据生成 | 模拟 5000+ 条销售记录，含季节性波动与折扣策略 |
| 数据库构建 | SQLite 星型模型：事实表 + 维度表 |
| SQL 分析 | 6 组核心分析查询（月度/品类/区域/商品/城市/日趋势）|
| 可视化看板 | ECharts 图表：折线、柱状、饼图、面积图 |

## 快速开始

```bash
pip install -r requirements.txt
python main.py
```

然后在浏览器中打开 `dashboard/index.html`。

## 技术栈

Python | Pandas | SQLite | ECharts | HTML/CSS

## 数据模型

```
fact_sales (事实表)
├── order_id, date, month
├── product_id, product_name, category
├── region, city
├── quantity, unit_price, total_amount, discount_rate

dim_product / dim_region / dim_date (维度表)
```
