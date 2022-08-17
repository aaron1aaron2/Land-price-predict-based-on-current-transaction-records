"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.08.16
Last Update: 2022.08.16
Describe: 觀察範圍內，有效的交易點
"""
import os
import pandas as pd

from geopy.distance import geodesic

output_folder = 'data/supplementary'
os.makedirs(output_folder, exist_ok=True)

df_tar = pd.read_csv('data/method_procces/0_target_land_group/group_list.csv')
df_tran = pd.read_csv('data/data_procces/8_time_range_select/transaction_all.csv')

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

# def get_distance(x):
#     try:
#         return geodesic(x['tran_land_center'].split(','),x['group_center'].split(',')).meters
#     except:
#         return ''

# tmp = two_point_df.head(60000).apply(lambda x: get_distance(x), axis=1) # 16.2 s/60000 筆

def get_distance(x):
    try:
        return geodesic(x[0].split(','),x[1].split(',')).meters
    except:
        return ''

two_point_df['linear_distance']  = list(map(get_distance, two_point_df[['tran_land_center', 'group_center']].values)) #  11.9 s/60000 筆
