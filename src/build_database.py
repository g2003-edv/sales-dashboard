"""构建 SQLite 数据库"""
import os
import sqlite3
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DB_PATH = os.path.join(DATA_DIR, 'sales.db')


def build_database():
    df = pd.read_csv(os.path.join(DATA_DIR, 'sales_raw.csv'), encoding='utf-8-sig')
    
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    
    # TODO: 维度表应该加索引，数据量大的时候JOIN会很慢
    conn.execute("CREATE TABLE dim_product (product_id TEXT PRIMARY KEY, product_name TEXT, category TEXT)")
    conn.execute("CREATE TABLE dim_region (region TEXT, city TEXT, PRIMARY KEY(region, city))")
    conn.execute("CREATE TABLE dim_date (date TEXT PRIMARY KEY, month TEXT, quarter TEXT)")
    conn.execute("CREATE TABLE fact_sales (order_id TEXT PRIMARY KEY, date TEXT, month TEXT, product_id TEXT, product_name TEXT, category TEXT, region TEXT, city TEXT, quantity INTEGER, unit_price REAL, total_amount REAL, discount_rate REAL)")
    
    df.to_sql('fact_sales', conn, if_exists='append', index=False)
    
    df[['product_id', 'product_name', 'category']].drop_duplicates().to_sql('dim_product', conn, if_exists='append', index=False)
    df[['region', 'city']].drop_duplicates().to_sql('dim_region', conn, if_exists='append', index=False)
    df[['date', 'month']].drop_duplicates().to_sql('dim_date', conn, if_exists='append', index=False)
    
    conn.commit()
    conn.close()
    print(f"  数据库构建完成: data/sales.db")
