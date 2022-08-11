# encoding: utf-8
"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.08.03
Last Update: 2022.08.03
Describe: 經手動與 google map 交叉確認「地籍圖資網路便民服務系統」的誤差較小，但是爬取速度太慢且會擋 ip，爬取全部土地位置估計需要 10 ~15 天。
            在時間上步允許，所以這邊希望比較 「地籍圖資網路便民服務系統」 與 「地號 GeoJSON API」 兩種地號轉經緯服務，透過在主要 54 筆資料上的差距。
            希望使用固定差距調整「地號 GeoJSON API」爬取到5萬多筆土地的的經緯度，以供後續任務使用。
"""
import os
import pandas as pd
import matplotlib.pyplot as plt

from geopy.distance import geodesic

output_folder = 'data/procces/supplementary'
os.makedirs(output_folder, exist_ok=True)

df_api = pd.read_csv('data/procces/old_version/5_get_coordinate(target).v1/crawler_result.csv')
df_easymap = pd.read_csv('data/procces/5_get_coordinate(target)/crawler_result.csv')

df_api.rename(columns={'xcenter': 'long(api)', 'ycenter': 'lat(api)'}, inplace=True)
df_easymap.drop('result_text', axis=1, inplace=True)


df = df_api.merge(df_easymap[['地段', '地號', 'lat', 'long']], on=['地段', '地號'], how='inner')


# df['lat_error'] = df['lat'] - df['lat(api)']
# df['long_error'] = df['long'] - df['long(api)']
# df[['lat_error', 'long_error']].sort_values('long_error').reset_index(drop=True).plot()

# plt.savefig(os.path.join(output_folder, 'coordinate_error_of_easymap_and_API.png'))

# 距離上的偏誤
df['距離誤差'] = df.apply(lambda x: geodesic([x['lat(api)'], x['long(api)']],[x['lat'], x['long']]).meters,axis=1)
# df_AB['linear_distance'] = df_AB.apply(lambda x:geodesic(x['start_coordinate'].split(','),x['end_coordinate'].split(',')).kilometers,axis=1)

df.sort_values('距離誤差').reset_index(drop=True)['距離誤差'].plot()
plt.savefig(os.path.join(output_folder, 'coordinate_error_of_easymap_and_API.png'))