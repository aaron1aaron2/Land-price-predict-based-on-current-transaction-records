# encoding: utf-8
"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.08.05
Last Update: 2022.08.08
Describe: 土地使用分區的分類與篩選。
"""
import os
import pandas as pd

import matplotlib.pyplot as plt

# 基本設定
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']

output_folder = 'data/data_procces/7_landuse_select'
os.makedirs(output_folder, exist_ok=True)

# 觀察目標土地的使用分區 =================================================
target_df = pd.read_csv('data/data_procces/5_get_coordinate(target)/crawler_result_mod.csv')
# target_df['使用分區'].value_counts().plot(kind='bar', rot=0, color='#00B08D', figsize=(10, 6))
target_df['使用分區'].value_counts().plot(kind='pie', rot=0, cmap=plt.get_cmap('Set3'), 
                autopct='%1.0f%%', pctdistance=0.8, labeldistance=1.1)
plt.savefig(os.path.join(output_folder, 'target_landuse_pie.png'))

# 觀察時價登入資料的土地使用分區 ===========================================
df = pd.read_csv('data/data_procces/6_sort_crawler_data/transaction_coordinate_use.csv', dtype=str)

landuse_df = df[['都市土地使用分區', '非都市土地使用分區', '非都市土地使用編定']].drop_duplicates().reset_index(drop=True)

tmp = landuse_df['都市土地使用分區'].fillna('無') + '|' + landuse_df['非都市土地使用分區'].fillna('無') + '|' +\
        landuse_df['非都市土地使用編定'].fillna('無')

landuse_df.loc[tmp.str.find('農') != -1, '使用分區'] = '農'
landuse_df.loc[tmp.str.find('住') != -1, '使用分區'] = '住'
landuse_df.loc[tmp.str.find('商') != -1, '使用分區'] = '商'
landuse_df.loc[tmp.str.find('工') != -1, '使用分區'] = '工'

landuse_df['使用分區'] = landuse_df['使用分區'].fillna('其他')

landuse_df.to_csv(os.path.join(output_folder, 'landuse_sort.csv'), index=False)

df = df.merge(landuse_df, on= ['都市土地使用分區', '非都市土地使用分區', '非都市土地使用編定'], how='left')

df.to_csv(os.path.join(output_folder, 'transaction_all.csv'), index=False)

# 觀察分布
plt.clf()
df['使用分區'].value_counts().plot(kind='pie', rot=0, cmap=plt.get_cmap('Pastel1'), 
                autopct='%1.0f%%', pctdistance=0.8, labeldistance=1.1)
plt.savefig(os.path.join(output_folder, 'transaction_landuse_pie.png'))