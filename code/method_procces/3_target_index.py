# encoding: utf-8
"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.08.23
Last Update: 2022.08.23
Describe: 計算每段時間，目標點、參考點在一定範圍內的區域指標
"""
import os
import tqdm
import pandas as pd

distance_matrix_folder = 'data/method_procces/2_calculate_distance_matrix'
output_folder = 'data/method_procces/3_target_index'
os.makedirs(output_folder, exist_ok=True)

target_coordinate_col = 'group_center'
transaction_coordinate_col = 'tran_coordinate'
refer_coordinate_col_ls = ['refer_point1', 'refer_point2', 'refer_point3', 'refer_point4']

target_cols = [target_coordinate_col] + refer_coordinate_col_ls

df_tran = pd.read_csv('data/data_procces/8_time_range_select/transaction_all.csv', usecols=['land_id', 'year', 'month', 'day'])
df_tran = df_tran.astype(int)

for gp_file in os.listdir(distance_matrix_folder):
    df_distance = pd.read_csv(os.path.join(distance_matrix_folder, gp_file))
