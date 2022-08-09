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
import seaborn as sns

# 基本設定
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']

output_folder = 'data/procces/7_landuse_select'
os.makedirs(output_folder, exist_ok=True)

# 觀察目標土地的使用分區 =================================================
target_df = pd.read_csv('data/procces/5_get_coordinate(target)/crawler_result_mod.csv')
# target_df['使用分區'].value_counts().plot(kind='bar', rot=0, color='#00B08D', figsize=(10, 6))
target_df['使用分區'].value_counts().plot(kind='pie', rot=0, cmap=plt.get_cmap('Set3'), 
                autopct='%1.0f%%', pctdistance=0.8, labeldistance=1.1)
plt.savefig(os.path.join(output_folder, 'target_landuse_pie.png'))

# 觀察時價登入資料的土地使用分區 ===========================================
df = pd.read_csv('data/procces/6_sort_crawler_data/transaction_coordinate_use.csv', dtype=str)

landuse_df = df[['都市土地使用分區', '非都市土地使用分區', '非都市土地使用編定']].drop_duplicates().reset_index(drop=True)
landuse_df.fillna('無', inplace=True)

tmp = landuse_df['都市土地使用分區'] + '|' + landuse_df['非都市土地使用分區'] + '|' + landuse_df['非都市土地使用編定']

landuse_df.loc[tmp.str.find('農') != -1, '類型'] = '農'
landuse_df.loc[tmp.str.find('住') != -1, '類型'] = '住'
landuse_df.loc[tmp.str.find('商') != -1, '類型'] = '商'
landuse_df.loc[tmp.str.find('工') != -1, '類型'] = '工'

landuse_df['類型'] = landuse_df['類型'].fillna('其他')

landuse_df.to_csv('')


