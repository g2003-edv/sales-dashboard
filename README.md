# 销售数据可视化看板

模拟电商订单数据，用SQLite做星型模型，SQL做多维分析，最后输出一个纯静态的HTML看板。

## 项目概述

没有后端服务器，所有数据存在SQLite里，SQL查询结果直接生成ECharts图表，嵌入到一个HTML文件里，双击就能打开看。

## 技术栈

Python、Pandas、SQLite、SQL、ECharts、HTML/CSS

## 数据模型

```
fact_sales (事实表)
├── order_id, date, month
├── product_id, product_name, category
├── region, city
├── quantity, unit_price, total_amount, discount_rate

dim_product (维度表)
dim_region (维度表)
dim_date (维度表)
```

## 核心功能

| 模块 | 说明 |
|------|------|
| 数据生成 | 模拟5000+条订单，含618/双11/春节的季节性波动 |
| 数据库构建 | SQLite星型模型 |
| SQL分析 | 6组多维查询 |
| 可视化看板 | 6个ECharts图表 + 4个指标卡片 |

## 数据规模

- 订单总量：5,000条
- 商品品类：数码/服饰/美妆/食品（4大类10款SKU）
- 覆盖区域：华东/华北/华南/西南/西北（15个城市）
- 时间跨度：2024全年

## 踩坑记录

- **外键约束**：SQLite默认不开启外键检查，一开始insert的时候有脏数据也没报错。后来加了`PRAGMA foreign_keys = ON`才发现有几个订单的产品ID在维度表里不存在。
- **SQL窗口函数**：写月度环比增长率的时候，LAG()函数一开始用不熟练，分区条件写错了，结果算出来是全局的LAG而不是按品类分区的。查了半天文档才调对。
- **ECharts双轴对齐**：月度趋势图想同时显示销售额（柱状）和销量（折线），两个Y轴的刻度范围没对齐，视觉上对比不明显。后来加了max/min的百分比计算才解决。
- **中文标签截断**：TOP10商品名称太长，ECharts的横向条形图标签被截断。加了formatter回调函数做换行处理。
- **静态HTML体积**：所有图表数据直接内嵌在HTML里，文件有800多KB。如果数据量再大可能要考虑分文件加载，目前5000条还行。

## 快速开始

```bash
pip install -r requirements.txt
python main.py
```

然后在浏览器中打开 `dashboard/index.html`。

## 看板包含的图表

- 月度销售趋势（柱状+折线双轴）
- 品类销售占比（环形饼图）
- 区域销售分布（渐变柱状图）
- TOP10热销商品（横向条形图）
- 城市销售排行TOP10（柱状图）
- 日销售趋势（平滑面积图）

## License

MIT
