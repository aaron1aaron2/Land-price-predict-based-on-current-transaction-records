# encoding: utf-8
"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.09.07
Last Update: 2022.09.07
Describe: 對土地分群
"""
import itertools

import pandas as pd
from sklearn.cluster import DBSCAN
from geopy.distance import geodesic

from PropGman.utils import timer

class LandGroup:
    def __init__(self, method:str):
        super(LandGroup, self).__init__()
        self.method = method

        self.method_ls = ['DBSCAN']
        
        if method not in self.method_ls: 
            raise AttributeError(f"module 'LandGroup' has no attribute 'DBSCAN'")

    def _get_distance_matrix(self, df, id_col, coordinate_col):
        # 整理資料
        df = df[[id_col, coordinate_col]]
        
        df_AB = pd.DataFrame(list(itertools.combinations(df['id'], 2)), 
                            columns=['start_id', 'end_id'])

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

        return distanct_mat

    def get_new_id(self, df):
        cur_id = df[self.method].max() +1

        result = []
        for i in df['DBSCAN'].to_list():
            result.append(i) if i !=-1 else result.append(cur_id)
            if i==-1: cur_id += 1
    @timer
    def main(self, df:pd.DataFrame, distance_threshold:int, id_col:str, coordinate_col:str) -> pd.DataFrame:

        distanct_mat = self._get_distance_matrix(df)

        # 分群
        if self.method in ['DBSCAN', 'dbscan']:
            db = DBSCAN(eps=distance_threshold, min_samples=2, metric='precomputed').fit(distanct_mat) # precomputed 代表使用距離矩陣
            df[self.method] = db.labels_

        # 建立 group id


        df['group_id'] = result

        df = df.join(df['coordinate'].str.extract('(?P<lat>.+),(?P<long>.+)').astype(float))

        group_center = df.groupby('group_id').apply(lambda gp: f"{gp['lat'].mean()},{gp['long'].mean()}").reset_index()
        group_center.rename({0:'group_center'}, axis=1, inplace=True)

        df = df.merge(group_center, how='left')
        df.drop(['lat', 'long'], axis=1, inplace=True)

        return df