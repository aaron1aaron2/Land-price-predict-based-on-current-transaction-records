# encoding: utf-8
"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.09.13
Last Update: 2022.09.13
Describe: 計算區域性指標
"""
import os
import tqdm
import pandas as pd

from datetime import datetime
from PropGman.utils import timer


class RegionalIndex:
    def __init__(self, start_date:str, end_date:str, time_freq:str, dist_threshold:int):
        super(RegionalIndex, self).__init__()
        
        # 時間區間
        self.start_date = start_date
        self.end_date = end_date

        self.time_freq = time_freq

        # 距離範圍
        self.dist_threshold = dist_threshold

    def _get_date_table(self):
        # 日期基準
        date_ls = pd.date_range(start=self.start_date, end=self.end_date, freq=self.time_freq)
        date_table = pd.DataFrame({
                'year': date_ls.year,
                'month': date_ls.month
            })
        self.total_time_step = date_table.shape[0]

        return date_table

    def _fill_na(self, df, cols):
        na_num = df[df[cols].isna()].shape[0]

        f_fill = df[target_value_col].fillna(method='ffill')
        b_fill = df[target_value_col].fillna(method='bfill')

        f_b_avg_fill  = (f_fill + b_fill)/2

        unable_fill_na_num = f_b_avg_fill[f_b_avg_fill.isna()].shape[0]


    def get_index(self, df_distance:pd.DataFrame, df_tran:pd.DataFrame, method:str, target_value_col:str, col:str):
        id_select = df_distance.loc[df_distance[col] <= self.dist_threshold, 'land_id'].to_list()
        df_tran_select = df_tran[df_tran['land_id'].isin(id_select)].copy()

        date_table = self._get_date_table()

        # df_tran_select.groupby(['year', 'month'])['單價元平方公尺'].count()
        if method=='mean':
            month_mean = df_tran_select.groupby(['year', 'month'])[target_value_col].mean()
        else:
            month_mean = df_tran_select.groupby(['year', 'month'])[target_value_col].mean()

        month_mean = date_table.merge(month_mean.reset_index(), how='left')

        self._fill_na(month_mean, target_value_col)

        {
            'file':gp_file, 'column_name':col, 
            'na_num':na_num, 'unable_fill_na':unable_fill_na_num,
            'na_rate':round(na_num/self.total_time_step, 2), 
            'unable_fill_na_rate':round(unable_fill_na_num/self.total_time_step, 2)
        }
