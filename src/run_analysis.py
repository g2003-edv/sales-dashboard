"""执行 SQL 分析"""
import os
import sqlite3
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
SQL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sql')
DB_PATH = os.path.join(DATA_DIR, 'sales.db')


def run_sql_analysis():
    os.makedirs(SQL_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    
    queries = {
        # TODO: 可以加上同比环比、留存率、RFM等分析维度
        'monthly_sales': "SELECT month, SUM(total_amount) as revenue, SUM(quantity) as qty FROM fact_sales GROUP BY month ORDER BY month",
        'category_sales': "SELECT category, SUM(total_amount) as revenue, SUM(quantity) as qty, COUNT(DISTINCT order_id) as orders FROM fact_sales GROUP BY category ORDER BY revenue DESC",
        'region_sales': "SELECT region, SUM(total_amount) as revenue, SUM(quantity) as qty FROM fact_sales GROUP BY region ORDER BY revenue DESC",
        'top_products': "SELECT product_name, category, SUM(total_amount) as revenue, SUM(quantity) as qty, AVG(discount_rate) as avg_discount FROM fact_sales GROUP BY product_name, category ORDER BY revenue DESC LIMIT 10",
        'daily_trend': "SELECT date, SUM(total_amount) as revenue FROM fact_sales GROUP BY date ORDER BY date",
        'city_performance': "SELECT city, region, SUM(total_amount) as revenue, COUNT(DISTINCT order_id) as orders FROM fact_sales GROUP BY city, region ORDER BY revenue DESC",
    }
    
    results = {}
    for name, sql in queries.items():
        df = pd.read_sql_query(sql, conn)
        results[name] = df
        df.to_csv(os.path.join(SQL_DIR, f'{name}.csv'), index=False, encoding='utf-8-sig')
        print(f"  分析完成: sql/{name}.csv")
    
    conn.close()
    return results
