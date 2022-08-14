# encoding: utf-8
"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.08.05
Last Update: 2022.08.05
Describe: 許多目標土地位置上很相近，所以在這步驟會使用 DBSCAN 聚類方式對土地點分群。讓位置相近的土地歸到成同一個目標點。
"""
import os
from unittest import result
import folium
import itertools
import pandas as pd

from matplotlib import cm, colors

from sklearn.cluster import DBSCAN
from geopy.distance import geodesic


output_folder = 'data/procces/9_m1_target_land_group'
os.makedirs(output_folder, exist_ok=True)

df = pd.read_csv('data/procces/5_get_coordinate(target)/crawler_result_mod.csv')

df['id'] = df.index

# 建立目標土地的 distanc matrix ========================================
df = pd.read_csv(os.path.join(output_folder, 'target_land.csv'), usecols=['id', 'lat', 'long'])

df_AB = pd.DataFrame(list(itertools.combinations(df['id'], 2)), 
                    columns=['start_id', 'end_id'])

df['coordinate'] = df['lat'].astype(str) + ',' + df['long'].astype(str)
df.drop(['lat', 'long'], axis=1, inplace=True)

df_start = df.rename(columns={
            'coordinate':'start_coordinate',
            'id':'start_id'
        })

df_AB = pd.merge(df_AB, df_start, on=['start_id'],how='left')

df_end = df_start.rename(columns={
        'start_coordinate':'end_coordinate',
        'start_id':'end_id'
    })

df_AB = pd.merge(df_AB, df_end, on=['end_id'], how='left')

df_AB['linear_distance'] = df_AB.apply(lambda x:geodesic(x['start_coordinate'].split(','),x['end_coordinate'].split(',')).meters,axis=1)

df_BA = df_AB.rename(columns={
        'end_id':'start_id',
        'start_id':'end_id'
})

df_all = pd.concat([df_AB, df_BA])
distanct_mat = df_all.pivot_table(values='linear_distance', index=['start_id'], columns=['end_id'])
distanct_mat.fillna(0, inplace=True)

# DBSCAN 分群 & 畫地圖 =========================================================
colors_ls = cm.get_cmap('Set1') # 0-7

for i in [100, 200, 300, 400, 500]:
    db = DBSCAN(eps=i, min_samples=2, metric='precomputed').fit(distanct_mat) # precomputed 代表使用距離矩陣
    df[f'DBSCAN_{i}'] = db.labels_

    map_ = folium.Map(
                [24.961640, 121.142500],
                zoom_start=12 )

    for idx, coor, group  in df[['id', 'coordinate', f'DBSCAN_{i}']].values:
        color = colors.to_hex(colors_ls(group%8)) if group!=-1 else 'black'
        folium.CircleMarker(location=coor.split(','),
                            radius=4, popup='popup',
                            color=color, 
                            fill=True,
                            fill_color=color).add_to(map_)
        
    map_.save(os.path.join(output_folder, f'DBSCAN_{i}.html'))

df.to_csv(os.path.join(output_folder, 'DBSCAN_result.csv'), index=False)


cur_id = df['DBSCAN_500'].max() +1

result = []
for i in df['DBSCAN_500'].to_list():
    result.append(i) if i !=-1 else result.append(cur_id)
    if i==-1: cur_id += 1

df['group_id'] = result

df_org = pd.read_csv(os.path.join(output_folder, 'target_land.csv'))
df = df_org.merge(df[['id', 'coordinate', 'group_id']], how='left')

df.drop('result_text', axis=1, inplace=True)
df.to_csv(os.path.join(output_folder, 'target_land_group.csv'), index=False)