from pathlib import Path
import pandas as pd

DATA_DIR = Path('data')
CSV_PATH = DATA_DIR / '淘宝全品类全国数据.csv'

print('当前工作目录：', Path.cwd())
print('数据文件存在：', CSV_PATH.exists())

df = pd.read_csv(CSV_PATH)
print(df.shape)

print('数据规模：', df.shape)
print('字段名：', df.columns.tolist())
print(df.head(5))
print(df.info())

print(df.dtypes)

missing_count = df.isna().sum().sort_values(ascending=False)
print(missing_count)

# 缺失率（百分比）
missing_rate = (df.isna().mean() * 100).round(1).sort_values(ascending=False)
print(missing_rate)

# 一列：Series
price_series = df['商品价格']
print(type(price_series))

# 多列：DataFrame
product_view = df[['商品id', '一级品类', '商品价格', '省份', '商品销量']]
print(type(product_view))
print(product_view.head())

print(df.loc[0:4, ['一级品类', '商品价格', '省份']])
print(df.iloc[0:5, 0:4])

# 单条件
guandong = df[df['省份'] == '广东']

# 多条件：每个条件都要加括号，使用 & 连接
condition = (df['省份'] == '广东') & (df['商品价格'] >= 1000)
selected = df.loc[condition, ['商品id', '一级品类', '二级品类', '商品价格', '省份', '商品销量']]
selected = selected.sort_values(by='商品价格', ascending=False)
print(selected.head(10))

# 或条件
zhejiang_or_jiangsu = df[(df['省份'] == '浙江') | (df['省份'] == '江苏')]
print('浙江或江苏商品数：', zhejiang_or_jiangsu.shape[0])

# 商品价格的描述性统计
print(df['商品价格'].describe().round(2))

# 一级品类商品数
print(df['一级品类'].value_counts())

# 一级品类汇总
category_summary = (
    df.groupby('一级品类')
      .agg(商品数=('商品id', 'size'),
           平均价格=('商品价格', 'mean'),
           中位价格=('商品价格', 'median'))
      .sort_values('平均价格', ascending=False)
      .round(2)
)
print(category_summary)

provinces = ['广东', '江苏']
subset = df[df['省份'].isin(provinces)]

province_summary = (
    subset.groupby('省份')
          .agg(商品数=('商品id', 'size'),
               平均价格=('商品价格', 'mean'),
               中位价格=('商品价格', 'median'))
          .round(2)
)
print(province_summary)

for province in provinces:
    top_category = (subset.loc[subset['省份'] == province, '一级品类']
                         .value_counts()
                         .head(1))
    print('\n', province, '最常见一级品类：')
    print(top_category)