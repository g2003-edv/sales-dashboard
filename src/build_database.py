"""构建 SQLite 数据库"""
import os
import sqlite3
from contextlib import closing

import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DB_PATH = os.path.join(DATA_DIR, 'sales.db')


def build_database():
    df = pd.read_csv(os.path.join(DATA_DIR, 'sales_raw.csv'), encoding='utf-8-sig')

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        # TODO: 维度表应该加索引，数据量大的时候JOIN会很慢
        conn.execute("CREATE TABLE dim_product (product_id TEXT PRIMARY KEY, product_name TEXT, category TEXT)")
        conn.execute("CREATE TABLE dim_region (region TEXT, city TEXT, PRIMARY KEY(region, city))")
        conn.execute("CREATE TABLE dim_date (date TEXT PRIMARY KEY, month TEXT, quarter INTEGER)")
        conn.execute("""
            CREATE TABLE fact_sales (
                order_id TEXT PRIMARY KEY,
                date TEXT NOT NULL REFERENCES dim_date(date),
                month TEXT,
                product_id TEXT NOT NULL REFERENCES dim_product(product_id),
                product_name TEXT,
                category TEXT,
                region TEXT NOT NULL,
                city TEXT NOT NULL,
                quantity INTEGER,
                unit_price REAL,
                total_amount REAL,
                discount_rate REAL,
                FOREIGN KEY (region, city) REFERENCES dim_region(region, city)
            )
        """)

        # 先写维度表，再写事实表，否则外键检查会失败
        dim_product = df[['product_id', 'product_name', 'category']].drop_duplicates()
        dim_product.to_sql('dim_product', conn, if_exists='append', index=False)

        dim_region = df[['region', 'city']].drop_duplicates()
        dim_region.to_sql('dim_region', conn, if_exists='append', index=False)

        dim_date = df[['date', 'month']].drop_duplicates().copy()
        month_number = dim_date['month'].str[5:7].astype(int)
        dim_date['quarter'] = (month_number - 1) // 3 + 1
        dim_date.to_sql('dim_date', conn, if_exists='append', index=False)

        conn.commit()

        df.to_sql('fact_sales', conn, if_exists='append', index=False)
        conn.commit()

    print(f"  数据库构建完成: data/sales.db")


if __name__ == '__main__':
    build_database()
