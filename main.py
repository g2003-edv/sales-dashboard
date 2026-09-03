"""
销售数据可视化看板
基于 SQLite + Python + ECharts 的静态数据看板生成
"""
import os
from src.generate_data import generate_sales_data
from src.build_database import build_database
from src.run_analysis import run_sql_analysis
from src.build_dashboard import build_dashboard


def main():
    print("=== 销售数据可视化看板 ===")
    
    print("[1/4] 生成模拟销售数据...")
    generate_sales_data()
    
    print("[2/4] 构建 SQLite 数据库...")
    build_database()
    
    print("[3/4] 执行 SQL 分析...")
    run_sql_analysis()
    
    print("[4/4] 生成 HTML 看板...")
    build_dashboard()
    
    print("\n全部完成，看板文件: dashboard/index.html")


if __name__ == '__main__':
    main()
