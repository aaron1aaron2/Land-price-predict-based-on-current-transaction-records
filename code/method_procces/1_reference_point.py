"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.08.16
Last Update: 2022.08.19
Describe: 設立對應的參考點。上下左右(3000公尺)的位置。
            1. 經緯度加減度數對應距離，由 google map 桃園市中心點為基準測試 -> (24.9605666,121.2188135)
            2. 關於範圍設定可以看 code/supplementary/m0__effective_range_select.py
"""
import os

import decimal
import pandas as pd

from functools import partial
from geopy.distance import geodesic

output_folder = 'data/method_procces/1_reference_point'
os.makedirs(output_folder, exist_ok=True)

df = pd.read_csv('data/method_procces/0_target_land_group/group_list.csv')

# 經緯度轉換距離測試 ---------------------------------------
decimal_places = lambda val: abs(decimal.Decimal(str(val)).as_tuple().exponent)

test_coordinate = '24.9605666,121.2188135'
lat, long = test_coordinate.split(',')
lat_len, long_len = decimal_places(lat), decimal_places(long)

# 緯度
test_interval = 0.0005
test_interval_pos = decimal_places(test_interval)

result_ls = []
for i in [round(i*test_interval, test_interval_pos) for i in range(1, 100)]:
    lat_new = str(round(float(lat)+i, lat_len))
    distance = geodesic(test_coordinate.split(','),[lat_new, long]).meters
    result_ls.append([i, f'{lat_new},{long}', test_coordinate, distance])

result_df = pd.DataFrame(result_ls, columns=['degree', 'target_coordinate', 'base_coordinate', 'distance(meter)'])

result_df.to_csv(os.path.join(output_folder, 'lat_test_table.csv'), index=False)

# 用內插法找出 100 公尺對應多少度
near_point = result_df.loc[(result_df['distance(meter)'] - 100).abs().sort_values().head(2).index]
near_point.sort_values('distance(meter)', inplace=True)

up_distance = near_point.loc[1, 'distance(meter)']
down_distance = near_point.loc[0, 'distance(meter)']
up_degree = near_point.loc[1, 'degree']
down_degree = near_point.loc[0, 'degree']

assert (up_distance >= 100) & (down_distance <= 100), 'The range does not contain 100 meters'

lat_degree = ((100-down_distance)/(up_distance-down_distance)*(up_degree-down_degree)) + down_degree
# lat_degree = 0.0009027527123486883

# 經度
test_interval = 0.0005
test_interval_pos = decimal_places(test_interval)

result_ls = []
for i in [round(i*test_interval, test_interval_pos) for i in range(1, 100)]:
    long_new = str(round(float(long)+i, long_len))
    distance = geodesic(test_coordinate.split(','),[lat, long_new]).meters
    result_ls.append([i, f'{lat},{long_new}', test_coordinate, distance])

result_df = pd.DataFrame(result_ls, columns=['degree', 'target_coordinate', 'base_coordinate', 'distance(meter)'])

result_df.to_csv(os.path.join(output_folder, 'long_test_table.csv'), index=False)

# 用內插法找出 100 公尺對應多少度
near_point = result_df.loc[(result_df['distance(meter)'] - 100).abs().sort_values().head(2).index]
near_point.sort_values('distance(meter)', inplace=True)

up_distance = near_point.loc[1, 'distance(meter)']
down_distance = near_point.loc[0, 'distance(meter)']
up_degree = near_point.loc[1, 'degree']
down_degree = near_point.loc[0, 'degree']

assert (up_distance >= 100) & (down_distance <= 100), 'The range does not contain 100 meters'

long_degree = ((100-down_distance)/(up_distance-down_distance)*(up_degree-down_degree)) + down_degree
# long_degree = 0.0009902726875066093

# 產生各群的參考點 ---------------------------------------
def get_reference(coordinate, target_meter, long_per_100_meter, lat_per_100_meter):
    lat, long = coordinate.split(',')

    lat_degree = target_meter*lat_per_100_meter/100
    long_degree = target_meter*long_per_100_meter/100

    result = {
        'group_center': coordinate,
        'refer_point1': f'{float(lat)+lat_degree},{long}',
        'refer_point2': f'{float(lat)-lat_degree},{long}',
        'refer_point3': f'{lat},{float(long)+long_degree}',
        'refer_point4': f'{lat},{float(long)-long_degree}'
    }


    return result

result_ls = list(map(partial(
        get_reference, 
        target_meter=3000, 
        long_per_100_meter=long_degree, 
        lat_per_100_meter=lat_degree
    ), df['group_center'].to_list()))

df = df.merge(pd.DataFrame(result_ls), how='left')
df.to_csv(os.path.join(output_folder, 'reference_point.csv'), index=False)