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
df_tran.reset_index(drop=True, inplace=True)

# 整理
df_tran['land_id'] = df_tran['land_id'].astype(int)
df_tran['tran_coordinate'] = df_tran['lat'].astype(str) + ',' +  df_tran['long'].astype(str)
df_tran.drop(['lat', 'long'], axis=1, inplace=True)

# 計算距離
target_coordinate_col = 'group_center'
transaction_coordinate_col = 'tran_center'
refer_coordinate_col_ls = ['refer_point1', 'refer_point2', 'refer_point3', 'refer_point4']

target_cols = [target_coordinate_col] + refer_coordinate_col_ls

def get_distance(x):
    """部分經緯度有問題"""
    try:
        lat1, long1 = x[0].split(',')
        lat2, long2 = x[1].split(',')

        if (abs(lat1) <= 90) & (abs(lat2) <= 90) & (long1<180) & (long2<180):
            return geodesic([lat1, long1],[lat2, long2]).meters
        else:
            return ''
    except:
        return ''

for gp_id in df_tar['group_id'].to_list():
    df_coor = df_tran.copy()
    df_coor['group_id'] = gp_id
    df_coor = df_coor.merge(df_tar, how='left')
    df_coor.to_csv(os.path.join(output_folder, f'group{gp_id}_coordinate.csv'), index=False)

    df_coor_dup = df_coor.drop_duplicates([target_coordinate_col, transaction_coordinate_col])
    for col in target_cols:
        df_coor_dup[f'{col}_DIST'] = list(map(get_distance, df_coor_dup[[transaction_coordinate_col, col]].values)) #  11.9 s/60000 筆 
        df_coor_dup = df_coor_dup[~(df_coor_dup[f'{col}_DIST']=='')]


    tmp.to_csv(os.path.join(output_folder, f'group{gp_id}_distance.csv'), index=False)