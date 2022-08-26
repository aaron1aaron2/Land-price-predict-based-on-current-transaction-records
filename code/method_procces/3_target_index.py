# encoding: utf-8
"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.08.23
Last Update: 2022.08.25
Describe: 計算每段時間，目標點、參考點在一定範圍內的區域指標
"""
import os
import tqdm
import pandas as pd
import matplotlib.pyplot as plt

distance_matrix_folder = 'data/method_procces/2_calculate_distance_matrix'
output_folder = 'data/method_procces/3_target_index'
os.makedirs(output_folder, exist_ok=True)

dist_threshold = 3000
target_value_col = '單價元平方公尺'

start_date = '2012-7'
end_date = '2022-4'

target_coordinate_col = 'group_center'
transaction_coordinate_col = 'tran_coordinate'
refer_coordinate_col_ls = ['refer_point1', 'refer_point2', 'refer_point3', 'refer_point4']

target_cols = [target_coordinate_col] + refer_coordinate_col_ls
target_cols = [i + '_DIST' for i in target_cols]

df_tran = pd.read_csv('data/data_procces/8_time_range_select/transaction_all.csv', usecols=['land_id', 'year', 'month', 'day', '單價元平方公尺'])
df_tran = df_tran.astype(int)

# 日期基準
date_ls = pd.date_range(start=start_date, end=end_date, freq='M')
date_table = pd.DataFrame({
        'year': date_ls.year,
        'month': date_ls.month
    })

for gp_file in os.listdir(distance_matrix_folder):
    df_distance = pd.read_csv(os.path.join(distance_matrix_folder, gp_file), usecols=['land_id'] + target_cols)
    for col in target_cols:
        id_select = df_distance.loc[df_distance[col] <= dist_threshold, 'land_id'].to_list()
        df_tran_select = df_tran[df_tran['land_id'].isin(id_select)].copy()

        # 計算區域指標 >>>>>>>>>>>>>>>>>>>
        # 區域內每月交易數量
        # df_tran_select.groupby(['year', 'month'])['單價元平方公尺'].count()

        # 區域內每月平均價
        month_mean = df_tran_select.groupby(['year', 'month'])[target_value_col].mean()
        # month_mean.plot()
        # plt.show()
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

        # 並到時間表，缺直處理 >>>>>>>>>>>>
        month_mean = date_table.merge(month_mean.reset_index(), how='left')
        # month_mean = date_table.merge(month_mean.reset_index().drop(115).drop(113), how='left') # 測試用
        na_num = month_mean[month_mean[target_value_col].isna()].shape[0]

        f_fill = month_mean[target_value_col].fillna(method='ffill')
        b_fill = month_mean[target_value_col].fillna(method='bfill')

        f_b_avg_fill  = (f_fill + b_fill)/2

        unable_fill_na_num = f_b_avg_fill[f_b_avg_fill.isna()].shape[0]
        
        f_b_avg_fill.dropna(inplace=True)
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
