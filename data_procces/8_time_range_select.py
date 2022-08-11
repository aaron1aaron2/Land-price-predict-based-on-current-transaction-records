# encoding: utf-8
"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.08.09
Last Update: 2022.08.09
Describe: 觀察時間與交易量的分布
"""
import os
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

# 基本設定
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']

output_folder = 'data/procces/8_time_range_select'
os.makedirs(output_folder, exist_ok=True)

df = pd.read_csv('data/procces/6_sort_crawler_data/transaction_coordinate_use.csv', dtype=str)

df.dropna(subset=['都市土地使用分區', '非都市土地使用分區', '非都市土地使用編定'], how='all', inplace=True)

df['year_TW'] = df['year']
df['year'] = df['year'].astype(int) + 1911
df['date'] = pd.to_datetime(df[["year", "month", "day"]].astype(int))

# 每月份的交易量
tmp = df[["year", "month", "day"]].astype(int)
tmp['day'] = 1

plt.clf()
# plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%b')) # define the formatting
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=12)) # show every 12th tick on x axes
# plt.xticks(rotation=40, fontweight='light', fontsize='x-small')

month_ct = pd.to_datetime(tmp).value_counts()
month_ct.plot(figsize=(10, 6))

plt.savefig(os.path.join(output_folder, '7_target_landuse_plot(month).png'))

# 每個月在不同
plt.clf()
df.groupby(['year', 'month']).size().unstack(fill_value=0)
sns.lineplot(x='year', y='Sales', data=, hue='使用分區', palette='Set1')
plt.show()