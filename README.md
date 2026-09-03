# 销售数据可视化看板 — SQL 数据建模与多维分析

> **技能关键词**：数据建模 · 星型模型 · SQL 多维分析 · ETL · 数据清洗 · 数据可视化 · ECharts · 静态看板 · SQLite · Pandas · Python

## 项目概述

模拟电商平台全渠道销售数据，通过 **SQL 星型模型** 进行数据建模与多维分析，最终生成包含 6 大核心图表的静态 HTML 看板，可直接部署或离线查看。

**核心能力覆盖**：
- 数据建模：设计 **星型模型**（事实表 + 维度表），支撑灵活多维分析
- SQL 分析：6 组核心查询（月度/品类/区域/商品/城市/日趋势）
- 数据可视化：ECharts 图表（折线、柱状、饼图、面积图、双轴图）
- 看板工程：纯静态 HTML，零后端依赖，支持任意 Web 服务器部署

## 技术栈

`Python` · `Pandas` · `SQLite` · `SQL` · `ECharts` · `HTML/CSS`

## 数据模型

```
fact_sales (事实表)
├── order_id, date, month
├── product_id, product_name, category
├── region, city
├── quantity, unit_price, total_amount, discount_rate

dim_product (维度表) ── product_id, product_name, category
dim_region (维度表) ── region, city
dim_date (维度表) ── date, month, quarter
```

## 核心功能

| 模块 | 说明 | 技能实践 |
|------|------|---------|
| 数据生成 | `data/sales_raw.csv` | 模拟 5000+ 条订单，含季节性波动（618/双11/春节）与折扣策略 |
| 数据库构建 | `data/sales.db` | SQLite 星型模型，事实表 + 3 张维度表 |
| SQL 分析 | `sql/*.csv` | 6 组多维查询：月度趋势 / 品类占比 / 区域分布 / TOP10 商品 / 城市排行 / 日趋势 |
| 可视化看板 | `dashboard/index.html` | 6 大 ECharts 图表 + 4 个核心指标卡片 |

## 数据规模

- **订单总量**：5,000 条
- **商品品类**：数码 / 服饰 / 美妆 / 食品（4 大类 10 款 SKU）
- **覆盖区域**：华东 / 华北 / 华南 / 西南 / 西北（15 个城市）
- **时间跨度**：2024 全年

## 快速开始

```bash
pip install -r requirements.txt
python main.py
```

然后在浏览器中打开 `dashboard/index.html`。

## 看板预览

看板包含以下图表：
- **月度销售趋势**：柱状图 + 折线图双轴展示（销售额 vs 销量）
- **品类销售占比**：环形饼图，直观展示各品类贡献
- **区域销售分布**：渐变柱状图，五大区业绩对比
- **TOP10 热销商品**：横向条形图，单品营收排名
- **城市销售排行 TOP10**：柱状图，城市级业绩分布
- **日销售趋势**：平滑面积图，全年销售波动一目了然
