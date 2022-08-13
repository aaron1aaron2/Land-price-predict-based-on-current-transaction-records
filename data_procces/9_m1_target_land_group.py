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
import folium
import itertools
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.cluster import DBSCAN
from sklearn import metrics
from geopy.distance import geodesic

output_folder = 'data/procces/9_m1_target_land_group'
os.makedirs(output_folder, exist_ok=True)

df = pd.read_csv('data/procces/5_get_coordinate(target)/crawler_result_mod.csv')

df['id'] = df.index
df.to_csv(os.path.join(output_folder, 'target_land.csv'), index=False)

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

# DBSCAN 分群 =========================================================

db = DBSCAN(eps=0.005, min_samples=10, metric='precomputed').fit(data)
labels = db.labels_
raito = len(labels[labels[:] == -1]) / len(labels) # 計算噪聲點個數佔總數的比例
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0) # 獲取分簇的數目

score = metrics.silhouette_score(data, labels)
 
df['label'] = labels
sns.lmplot('lat_Amap', 'lng_Amap', df, hue='label', fit_reg=False)

## 第二部分
map_ = folium.Map(
            [24.961640, 121.142500],
            zoom_start=12 )

colors = ['#DC143C', '#FFB6C1', '#DB7093', '#C71585', '#8B008B', '#4B0082', '#7B68EE',
         '#0000FF', '#B0C4DE', '#708090', '#00BFFF', '#5F9EA0', '#00FFFF', '#7FFFAA',
         '#008000', '#FFFF00', '#808000', '#FFD700', '#FFA500', '#FF6347','#DC143C', 
         '#FFB6C1', '#DB7093', '#C71585', '#8B008B', '#4B0082', '#7B68EE',
         '#0000FF', '#B0C4DE', '#708090', '#00BFFF', '#5F9EA0', '#00FFFF', '#7FFFAA',
         '#008000', '#FFFF00', '#808000', '#FFD700', '#FFA500', '#FF6347', 
         '#DC143C', '#FFB6C1', '#DB7093', '#C71585', '#8B008B', '#4B0082', '#7B68EE',
         '#0000FF', '#B0C4DE', '#708090', '#00BFFF', '#5F9EA0', '#00FFFF', '#7FFFAA',
         '#008000', '#FFFF00', '#808000', '#FFD700', '#FFA500', '#FF6347',
         '#DC143C', '#FFB6C1', '#DB7093', '#C71585', '#8B008B', '#4B0082', '#7B68EE',
         '#0000FF', '#B0C4DE', '#708090', '#00BFFF', '#5F9EA0', '#00FFFF', '#7FFFAA',
         '#008000', '#FFFF00', '#808000', '#FFD700', '#FFA500', '#FF6347','#DC143C', 
         '#FFB6C1', '#DB7093', '#C71585', '#8B008B', '#4B0082', '#7B68EE',
         '#0000FF', '#B0C4DE', '#708090', '#00BFFF', '#5F9EA0', '#00FFFF', '#7FFFAA',
         '#008000', '#FFFF00', '#808000', '#FFD700', '#FFA500', '#FF6347', 
         '#DC143C', '#FFB6C1', '#DB7093', '#C71585', '#8B008B', '#4B0082', '#7B68EE',
         '#0000FF', '#B0C4DE', '#708090', '#00BFFF', '#5F9EA0', '#00FFFF', '#7FFFAA',
         '#008000', '#FFFF00', '#808000', '#FFD700', '#FFA500', '#FF6347','#000000']

for i in range(len(data)):
    folium.CircleMarker(location=[data[i][0], data[i][1]],
                        radius=4, popup='popup',
                        color=colors[labels[i]], fill=True,
                        fill_color=colors[labels[i]]).add_to(map_)
    
map_.save('all_cluster.html')