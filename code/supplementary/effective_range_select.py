"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.08.16
Last Update: 2022.08.16
Describe: 設立對應的參考點。上下左右
"""
import os
import pandas as pd

from geopy.distance import geodesic

output_folder = 'data/supplementary'
os.makedirs(output_folder, exist_ok=True)

df_tar = pd.read_csv('data/method_procces/0_target_land_group/target_land_group.csv')
df_tran = pd.read_csv('data/data_procces/8_time_range_select/transaction_all.csv')