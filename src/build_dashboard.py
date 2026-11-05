"""生成 HTML 看板"""
import os
import json
import pandas as pd

SQL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sql')
DASHBOARD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dashboard')


def _mom_pct(series):
    """环比：最后一期相对上一期的百分比变化；期数不足或上期为 0 时返回 None"""
    if series is None:
        return None
    values = pd.to_numeric(pd.Series(series), errors='coerce').reset_index(drop=True)
    if len(values) < 2:
        return None
    prev, cur = values.iloc[-2], values.iloc[-1]
    if pd.isna(prev) or pd.isna(cur) or prev == 0:
        return None
    return (float(cur) - float(prev)) / float(prev) * 100


def _mom_html(pct):
    """指标卡副标题：算不出来就显示 —，不编造数字"""
    if pct is None:
        return '<div class="metric-change muted">环比 —</div>'
    css_class = 'up' if pct >= 0 else 'down'
    return f'<div class="metric-change {css_class}">环比 {pct:+.1f}%</div>'


def build_dashboard():
    os.makedirs(DASHBOARD_DIR, exist_ok=True)
    
    monthly = pd.read_csv(os.path.join(SQL_DIR, 'monthly_sales.csv'), encoding='utf-8-sig')
    category = pd.read_csv(os.path.join(SQL_DIR, 'category_sales.csv'), encoding='utf-8-sig')
    region = pd.read_csv(os.path.join(SQL_DIR, 'region_sales.csv'), encoding='utf-8-sig')
    top_products = pd.read_csv(os.path.join(SQL_DIR, 'top_products.csv'), encoding='utf-8-sig')
    daily = pd.read_csv(os.path.join(SQL_DIR, 'daily_trend.csv'), encoding='utf-8-sig')
    city = pd.read_csv(os.path.join(SQL_DIR, 'city_performance.csv'), encoding='utf-8-sig')
    
    monthly = monthly.sort_values('month').reset_index(drop=True)
    monthly_revenue = pd.to_numeric(monthly['revenue'], errors='coerce')
    monthly_qty = pd.to_numeric(monthly['qty'], errors='coerce')
    monthly_orders = (
        pd.to_numeric(monthly['orders'], errors='coerce')
        if 'orders' in monthly.columns else None
    )

    total_revenue = monthly_revenue.sum()
    total_orders = (
        monthly_orders.sum() if monthly_orders is not None
        else pd.to_numeric(category['orders'], errors='coerce').sum()
    )
    total_qty = monthly_qty.sum()
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

    revenue_mom = _mom_pct(monthly_revenue)
    orders_mom = _mom_pct(monthly_orders)
    qty_mom = _mom_pct(monthly_qty)
    if monthly_orders is not None:
        monthly_aov = monthly_revenue / monthly_orders.where(monthly_orders != 0)
        aov_mom = _mom_pct(monthly_aov)
    else:
        aov_mom = None
    
    monthly_data = {
        'months': monthly['month'].tolist(),
        'revenue': [round(x, 2) for x in monthly['revenue'].tolist()],
        'qty': monthly['qty'].tolist(),
    }
    
    category_data = {
        'names': category['category'].tolist(),
        'values': [round(x, 2) for x in category['revenue'].tolist()],
    }
    
    region_data = {
        'names': region['region'].tolist(),
        'values': [round(x, 2) for x in region['revenue'].tolist()],
    }
    
    top_products_data = {
        'names': top_products['product_name'].tolist(),
        'revenue': [round(x, 2) for x in top_products['revenue'].tolist()],
    }
    
    city_data = {
        'names': city['city'].tolist()[:10],
        'values': [round(x, 2) for x in city['revenue'].tolist()[:10]],
    }
    
    daily_data = {
        'dates': daily['date'].tolist(),
        'values': [round(x, 2) for x in daily['revenue'].tolist()],
    }
    
    # FIXME: CSS样式全硬编码在Python字符串里，改个颜色要改代码，应该抽成模板文件
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>销售数据可视化看板</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            background: #f0f2f5;
            color: #333;
        }}
        .header {{
            background: linear-gradient(135deg, #1890ff 0%, #722ed1 100%);
            color: white;
            padding: 30px 40px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .header h1 {{ font-size: 28px; font-weight: 500; }}
        .header p {{ opacity: 0.85; margin-top: 8px; font-size: 14px; }}
        
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            padding: 24px 40px;
        }}
        .metric-card {{
            background: white;
            padding: 24px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: 600;
            color: #1890ff;
            margin-bottom: 8px;
        }}
        .metric-label {{ color: #666; font-size: 14px; }}
        .metric-change {{
            font-size: 12px;
            margin-top: 4px;
        }}
        .metric-change.up {{ color: #52c41a; }}
        .metric-change.down {{ color: #cf1322; }}
        .metric-change.muted {{ color: #999; }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(480px, 1fr));
            gap: 20px;
            padding: 0 40px 24px;
        }}
        .chart-card {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            padding: 20px;
        }}
        .chart-card h3 {{
            font-size: 16px;
            font-weight: 500;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid #f0f0f0;
        }}
        .chart-container {{ width: 100%; height: 320px; }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: #999;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>销售数据可视化看板</h1>
        <p>2024 年度全渠道销售数据分析 | 基于 SQLite + Python + ECharts</p>
    </div>
    
    <div class="metrics">
        <div class="metric-card">
            <div class="metric-value">¥{total_revenue:,.0f}</div>
            <div class="metric-label">总销售额</div>
            {_mom_html(revenue_mom)}
        </div>
        <div class="metric-card">
            <div class="metric-value">{total_orders:,}</div>
            <div class="metric-label">总订单数</div>
            {_mom_html(orders_mom)}
        </div>
        <div class="metric-card">
            <div class="metric-value">{total_qty:,}</div>
            <div class="metric-label">总销量（件）</div>
            {_mom_html(qty_mom)}
        </div>
        <div class="metric-card">
            <div class="metric-value">¥{avg_order_value:.0f}</div>
            <div class="metric-label">客单价</div>
            {_mom_html(aov_mom)}
        </div>
    </div>
    
    <div class="charts-grid">
        <div class="chart-card">
            <h3>月度销售趋势</h3>
            <div id="monthlyChart" class="chart-container"></div>
        </div>
        <div class="chart-card">
            <h3>品类销售占比</h3>
            <div id="categoryChart" class="chart-container"></div>
        </div>
        <div class="chart-card">
            <h3>区域销售分布</h3>
            <div id="regionChart" class="chart-container"></div>
        </div>
        <div class="chart-card">
            <h3>TOP10 热销商品</h3>
            <div id="productChart" class="chart-container"></div>
        </div>
        <div class="chart-card">
            <h3>城市销售排行 TOP10</h3>
            <div id="cityChart" class="chart-container"></div>
        </div>
        <div class="chart-card">
            <h3>日销售趋势</h3>
            <div id="dailyChart" class="chart-container"></div>
        </div>
    </div>
    
    <div class="footer">
        数据来源：模拟电商销售数据 | 技术栈：Python + Pandas + SQLite + ECharts
    </div>
    
    <script>
        const monthlyData = {json.dumps(monthly_data, ensure_ascii=False)};
        const categoryData = {json.dumps(category_data, ensure_ascii=False)};
        const regionData = {json.dumps(region_data, ensure_ascii=False)};
        const topProductsData = {json.dumps(top_products_data, ensure_ascii=False)};
        const cityData = {json.dumps(city_data, ensure_ascii=False)};
        const dailyData = {json.dumps(daily_data, ensure_ascii=False)};
        
        echarts.init(document.getElementById('monthlyChart')).setOption({{
            tooltip: {{ trigger: 'axis' }},
            legend: {{ data: ['销售额', '销量'] }},
            xAxis: {{ type: 'category', data: monthlyData.months, axisLabel: {{ rotate: 45 }} }},
            yAxis: [
                {{ type: 'value', name: '销售额', axisLabel: {{ formatter: '¥{{value}}' }} }},
                {{ type: 'value', name: '销量' }}
            ],
            series: [
                {{ name: '销售额', type: 'bar', data: monthlyData.revenue, itemStyle: {{ color: '#1890ff' }} }},
                {{ name: '销量', type: 'line', yAxisIndex: 1, data: monthlyData.qty, itemStyle: {{ color: '#52c41a' }} }}
            ]
        }});
        
        echarts.init(document.getElementById('categoryChart')).setOption({{
            tooltip: {{ trigger: 'item', formatter: '{{b}}: ¥{{c}} ({{d}}%)' }},
            legend: {{ orient: 'vertical', left: 'left' }},
            series: [{{
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                itemStyle: {{ borderRadius: 8, borderColor: '#fff', borderWidth: 2 }},
                label: {{ show: true, formatter: '{{b}}\\n{{d}}%' }},
                data: categoryData.names.map((name, i) => ({{ name, value: categoryData.values[i] }}))
            }}]
        }});
        
        echarts.init(document.getElementById('regionChart')).setOption({{
            tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }} }},
            xAxis: {{ type: 'category', data: regionData.names }},
            yAxis: {{ type: 'value', axisLabel: {{ formatter: '¥{{value}}' }} }},
            series: [{{
                type: 'bar',
                data: regionData.values,
                itemStyle: {{
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        {{ offset: 0, color: '#1890ff' }},
                        {{ offset: 1, color: '#722ed1' }}
                    ])
                }}
            }}]
        }});
        
        echarts.init(document.getElementById('productChart')).setOption({{
            tooltip: {{ trigger: 'axis' }},
            xAxis: {{ type: 'value', axisLabel: {{ formatter: '¥{{value}}' }} }},
            yAxis: {{ type: 'category', data: topProductsData.names.reverse() }},
            series: [{{
                type: 'bar',
                data: topProductsData.revenue.reverse(),
                itemStyle: {{ color: '#13c2c2' }},
                label: {{ show: true, position: 'right', formatter: '¥{{c}}' }}
            }}]
        }});
        
        echarts.init(document.getElementById('cityChart')).setOption({{
            tooltip: {{ trigger: 'axis' }},
            xAxis: {{ type: 'category', data: cityData.names, axisLabel: {{ rotate: 30 }} }},
            yAxis: {{ type: 'value', axisLabel: {{ formatter: '¥{{value}}' }} }},
            series: [{{
                type: 'bar',
                data: cityData.values,
                itemStyle: {{ color: '#fa8c16' }}
            }}]
        }});
        
        echarts.init(document.getElementById('dailyChart')).setOption({{
            tooltip: {{ trigger: 'axis' }},
            xAxis: {{ type: 'category', data: dailyData.dates, axisLabel: {{ show: false }} }},
            yAxis: {{ type: 'value', axisLabel: {{ formatter: '¥{{value}}' }} }},
            series: [{{
                type: 'line',
                data: dailyData.values,
                smooth: true,
                areaStyle: {{
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        {{ offset: 0, color: 'rgba(24,144,255,0.3)' }},
                        {{ offset: 1, color: 'rgba(24,144,255,0.05)' }}
                    ])
                }},
                itemStyle: {{ color: '#1890ff' }}
            }}]
        }});
    </script>
</body>
</html>"""
    
    with open(os.path.join(DASHBOARD_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"  看板已生成: dashboard/index.html")


if __name__ == '__main__':
    build_dashboard()
