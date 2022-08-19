# encoding: utf-8
"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.08.14
Last Update: 2022.08.14
Describe: 獲取所有時價登入土地與目標土地經緯度之間的直線距離。
"""
import os
import itertools
import pandas as pd

from geopy.distance import geodesic

output_folder = 'data/method_procces/2_calculate_distance_matrix'
os.makedirs(output_folder, exist_ok=True)

df_tar = pd.read_csv('data/method_procces/1_reference_point/reference_point.csv')
df_tran = pd.read_csv('data/data_procces/8_time_range_select/transaction_all.csv', usecols=['long', 'lat', 'land_id'])
df_tran.drop_duplicates(inplace=True)
df_tran['land_id'] = df_tran['land_id'].astype(int)

tran_land = df_tran[['long', 'lat', 'land_id']].drop_duplicates()
tran_land['tran_land_center'] = tran_land['lat'].astype(str) + ',' +  tran_land['long'].astype(str)
tran_land.drop(['lat', 'long'], axis=1, inplace=True)
tran_land['land_id'] = tran_land['land_id'].astype(int)

two_point_df = pd.DataFrame()
for gp_id in df_tar['group_id'].to_list():
    tmp = tran_land.copy()
    tmp['group_id'] = gp_id
    two_point_df = pd.concat([two_point_df, tmp])

two_point_df = two_point_df.merge(df_tar, how='left')