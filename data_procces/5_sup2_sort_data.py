"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.08.03
Last Update: 2022.08.03
Describe: 資料整理
"""

import os
import pandas as pd

output_folder = 'data/procces/5_sup2_sort_data'

os.makedirs(output_folder, exist_ok=True)

df1 = pd.read_csv('data/procces/5_get_coordinate(target)/crawler_result.csv')
df2 = pd.read_csv('data/procces/5_sup1_get_coordinate(target)/crawler_result.csv')


df1.rename(columns={'xcenter': 'long', 'ycenter': 'lat'}, inplace=True)
df2.drop('result_text', axis=1, inplace=True)

pd.concat([df2, df1]).to_csv(os.path.join(output_folder, 'crawler_result.csv'), index=False)