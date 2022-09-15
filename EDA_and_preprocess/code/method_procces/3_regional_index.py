# encoding: utf-8
"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.08.23
Last Update: 2022.08.26
Describe: 計算每段時間，目標點、參考點在一定範圍內的區域指標
"""
import os
import tqdm
import pandas as pd

distance_matrix_folder = 'data/method_procces/2_calculate_distance_matrix'
output_folder = 'data/method_procces/3_target_index'
os.makedirs(output_folder, exist_ok=True)
os.makedirs(os.path.join(output_folder, 'groups'), exist_ok=True)

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
total_num = date_table.shape[0]

task_ls = [(gp_file, col) for gp_file in os.listdir(distance_matrix_folder) for col in target_cols]
fill_result_dt_ls = []

# 為了看進度，不使用雙 FOR 迴圈寫法
pre_gp_file = ''
gp_table = date_table.copy()
for gp_file, col in tqdm.tqdm(task_ls):
    if gp_file != pre_gp_file:
        df_distance = pd.read_csv(os.path.join(distance_matrix_folder, gp_file), usecols=['land_id'] + target_cols)

    id_select = df_distance.loc[df_distance[col] <= dist_threshold, 'land_id'].to_list()
    df_tran_select = df_tran[df_tran['land_id'].isin(id_select)].copy()

    # 計算區域指標 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # 區域內每月交易數量
    # df_tran_select.groupby(['year', 'month'])['單價元平方公尺'].count()

    # 區域內每月平均價
    month_mean = df_tran_select.groupby(['year', 'month'])[target_value_col].mean()
    # month_mean.plot()
    # plt.show()
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # 並到時間表，缺直處理 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    month_mean = date_table.merge(month_mean.reset_index(), how='left')
    # month_mean = date_table.merge(month_mean.reset_index().drop(115).drop(113), how='left') # 測試用
    na_num = month_mean[month_mean[target_value_col].isna()].shape[0]

    f_fill = month_mean[target_value_col].fillna(method='ffill')
    b_fill = month_mean[target_value_col].fillna(method='bfill')

    f_b_avg_fill  = (f_fill + b_fill)/2

    unable_fill_na_num = f_b_avg_fill[f_b_avg_fill.isna()].shape[0]

    fill_result_dt_ls.append({
        'file':gp_file, 'column_name':col, 
        'na_num':na_num, 'unable_fill_na':unable_fill_na_num,
        'na_rate':round(na_num/total_num, 2), 
        'unable_fill_na_rate':round(unable_fill_na_num/total_num, 2)
        })
    
    if (gp_file == pre_gp_file) | (pre_gp_file==''):
        gp_table[col] = f_b_avg_fill
        if all([i in gp_table.columns for i in target_cols]):
            gp_table.to_csv(os.path.join(output_folder, 'groups', f'{gp_file}'), index=False)
        pass
    else:
        gp_table = date_table.copy()
        gp_table[col] = f_b_avg_fill

    pre_gp_file = gp_file
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

pd.DataFrame(fill_result_dt_ls).to_csv(os.path.join(output_folder, 'fillna_record.csv'), index=False)