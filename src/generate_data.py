"""生成模拟销售数据"""
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
ORDER_COUNT = 5000


def seasonal_factor(month):
    """大促月（618/双11）订单更多，春节月订单更少"""
    if month in (6, 11):
        return 2.5
    if month in (1, 2):
        return 0.6
    return 1.0


def generate_sales_data():
    np.random.seed(42)  # FIXME: 固定种子导致每次生成的数据都一样，应该用当前日期做种子或支持参数传入
    
    products = [
        {'id': 'P001', 'name': '智能手机', 'category': '数码', 'price': 3999},
        {'id': 'P002', 'name': '无线耳机', 'category': '数码', 'price': 899},
        {'id': 'P003', 'name': '平板电脑', 'category': '数码', 'price': 2999},
        {'id': 'P004', 'name': '运动鞋', 'category': '服饰', 'price': 599},
        {'id': 'P005', 'name': 'T恤', 'category': '服饰', 'price': 129},
        {'id': 'P006', 'name': '连衣裙', 'category': '服饰', 'price': 359},
        {'id': 'P007', 'name': '护肤套装', 'category': '美妆', 'price': 699},
        {'id': 'P008', 'name': '口红', 'category': '美妆', 'price': 199},
        {'id': 'P009', 'name': '零食大礼包', 'category': '食品', 'price': 89},
        {'id': 'P010', 'name': '进口牛奶', 'category': '食品', 'price': 59},
    ]
    
    regions = ['华东', '华北', '华南', '西南', '西北']
    cities = {
        '华东': ['上海', '杭州', '南京'],
        '华北': ['北京', '天津', '石家庄'],
        '华南': ['广州', '深圳', '佛山'],
        '西南': ['成都', '重庆', '昆明'],
        '西北': ['西安', '兰州', '乌鲁木齐'],
    }
    
    orders = []
    start_date = datetime(2024, 1, 1)
    days = [start_date + timedelta(days=i) for i in range(365)]

    # 季节因子作用在订单笔数上：按月的权重抽样日期，大促月生成更多订单
    day_weights = np.array([seasonal_factor(d.month) for d in days], dtype=float)
    day_weights /= day_weights.sum()
    day_indices = np.random.choice(len(days), size=ORDER_COUNT, p=day_weights)

    for i in range(ORDER_COUNT):
        date = days[int(day_indices[i])]
        product = np.random.choice(products)
        region = np.random.choice(regions)
        city = np.random.choice(cities[region])

        # 季节性已体现在订单笔数上，单笔购买量保持稳定（否则会被平方放大）
        quantity = max(1, int(np.random.poisson(2)))
        unit_price = product['price'] * np.random.uniform(0.8, 1.0)
        total_amount = round(quantity * unit_price, 2)
        
        orders.append({
            'order_id': f'ORD{date.strftime("%Y%m%d")}{i:05d}',
            'date': date.strftime('%Y-%m-%d'),
            'month': date.strftime('%Y-%m'),
            'product_id': product['id'],
            'product_name': product['name'],
            'category': product['category'],
            'region': region,
            'city': city,
            'quantity': quantity,
            'unit_price': round(unit_price, 2),
            'total_amount': total_amount,
            'discount_rate': round(1 - unit_price / product['price'], 2),
        })
    
    df = pd.DataFrame(orders)
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(os.path.join(DATA_DIR, 'sales_raw.csv'), index=False, encoding='utf-8-sig')
    print(f"  生成 {len(df)} 条销售记录: data/sales_raw.csv")


if __name__ == '__main__':
    generate_sales_data()
