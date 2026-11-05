"""执行 SQL 分析"""
import os
import sqlite3
from contextlib import closing

import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
SQL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sql')
DB_PATH = os.path.join(DATA_DIR, 'sales.db')


def run_sql_analysis():
    os.makedirs(SQL_DIR, exist_ok=True)

    queries = {
        # TODO: 可以加上同比环比、留存率、RFM等分析维度
        'monthly_sales': """
            SELECT d.month AS month,
                   SUM(f.total_amount) AS revenue,
                   SUM(f.quantity) AS qty,
                   COUNT(DISTINCT f.order_id) AS orders
            FROM fact_sales f
            JOIN dim_date d ON f.date = d.date
            GROUP BY d.month
            ORDER BY d.month
        """,
        'category_sales': """
            SELECT p.category AS category,
                   SUM(f.total_amount) AS revenue,
                   SUM(f.quantity) AS qty,
                   COUNT(DISTINCT f.order_id) AS orders
            FROM fact_sales f
            JOIN dim_product p ON f.product_id = p.product_id
            GROUP BY p.category
            ORDER BY revenue DESC
        """,
        'region_sales': """
            SELECT r.region AS region,
                   SUM(f.total_amount) AS revenue,
                   SUM(f.quantity) AS qty
            FROM fact_sales f
            JOIN dim_region r ON f.region = r.region AND f.city = r.city
            GROUP BY r.region
            ORDER BY revenue DESC
        """,
        'top_products': """
            SELECT p.product_name AS product_name,
                   p.category AS category,
                   SUM(f.total_amount) AS revenue,
                   SUM(f.quantity) AS qty,
                   AVG(f.discount_rate) AS avg_discount
            FROM fact_sales f
            JOIN dim_product p ON f.product_id = p.product_id
            GROUP BY p.product_name, p.category
            ORDER BY revenue DESC
            LIMIT 10
        """,
        'daily_trend': """
            SELECT d.date AS date,
                   SUM(f.total_amount) AS revenue
            FROM fact_sales f
            JOIN dim_date d ON f.date = d.date
            GROUP BY d.date
            ORDER BY d.date
        """,
        'city_performance': """
            SELECT r.city AS city,
                   r.region AS region,
                   SUM(f.total_amount) AS revenue,
                   COUNT(DISTINCT f.order_id) AS orders
            FROM fact_sales f
            JOIN dim_region r ON f.region = r.region AND f.city = r.city
            GROUP BY r.city, r.region
            ORDER BY revenue DESC
        """,
    }

    results = {}
    with closing(sqlite3.connect(DB_PATH)) as conn:
        for name, sql in queries.items():
            df = pd.read_sql_query(sql, conn)
            results[name] = df
            df.to_csv(os.path.join(SQL_DIR, f'{name}.csv'), index=False, encoding='utf-8-sig')
            print(f"  分析完成: sql/{name}.csv")

    return results


if __name__ == '__main__':
    run_sql_analysis()
