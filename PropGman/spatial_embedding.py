# encoding: utf-8
"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.08.23
Last Update: 2022.08.25
Describe: 
"""
import os
import itertools
import pandas as pd
import numpy as np
from geopy.distance import geodesic

from PropGman.model.node2vec import generateSE
from PropGman.utils import build_folder, saveJson

pd.options.mode.chained_assignment = None  # default='warn'

def get_one_way_edge(df, group:str, coor_col:str, id_col:str):
    '''
    Group according to G, create a one-way-edge for all points in each group.

    point out
    ---
    There will be `(n-1)*n/2` lines(edge) at n points
    '''
    # 檢查輸入參數
    if group != None:
        cols = [group, coor_col, id_col]
    else:
        cols = [coor_col, id_col]

    for col in cols:
        assert col in df.columns, "'{}' not in dataframe! please check a column name.".format(col)
    
    df = df[cols]

    #產生配對
    if group != None:
        df_AB = df.groupby(df[group]).apply(lambda x:pd.DataFrame(list(itertools.combinations(x[id_col], 2))))
    else:
        df_AB = pd.DataFrame(list(itertools.combinations(df[id_col], 2)))

    df_AB.rename(columns={
                    0:'start_id',
                    1:'end_id'
                   }, 
                 inplace=True)

    #資料合併
    df.rename(columns={
                 '{}'.format(coor_col):'start_latlong',
                 '{}'.format(id_col):'start_id'
                }, 
              inplace=True)

    df_AB = pd.merge(df_AB, df, on=['start_id'], how='left')

    df.rename(columns={
                'start_latlong':'end_latlong',
                'start_id':'end_id'
                }, 
              inplace=True)

    df_AB = pd.merge(df_AB, df, on=['end_id'], how='left')
    
    return df_AB

def get_two_way_with_self(df, one_wey_table, coor_col:str, id_col:str):
    '''
    Flip two points and add the connection between the same points.
    Then we can get table, which can convert to  `distance matrix`.

    warn
    ---
    `start_id`, `end_id`, `start_latlong`, `end_latlong`, `linear_distance` must exist in the field.
    '''

    # 檢查參數
    for arg in [coor_col, id_col]:
        assert arg in df.columns, "[{}] not in dataframe input".format(arg)

    df = df[[id_col, coor_col]]

    #翻轉AB
    df.rename(columns={
        '{}'.format(id_col):'start_id',
        '{}'.format(coor_col):'start_latlong'}, inplace=True)


    df_end = df[['start_id','start_latlong']].rename(columns={
                                                        'start_id':'end_id',
                                                        'start_latlong':'end_latlong'
                                                        })
    df_self = pd.concat([df,df_end],sort=True,axis=1)
    
    #自己到自己補零
    df_self['linear_distance'] = np.zeros(shape=(len(df),1))

    one_wey_table_T = one_wey_table.rename(columns={
                                                'start_latlong':'end_latlong',
                                                'end_latlong':'start_latlong',
                                                'start_id':'end_id',
                                                'end_id':'start_id',
                                                'start_addr':'end_addr',
                                                'end_addr':'start_addr'
                                                })

    two_wey_table = pd.concat([one_wey_table, one_wey_table_T, df_self], sort=True)

    no = two_wey_table['start_id'].astype(str).str.extract(r'(?P<start_no>\d+)').astype(int)
    no2 = two_wey_table['end_id'].astype(str).str.extract(r'(?P<end_no>\d+)').astype(int)

    two_wey_table = pd.concat([two_wey_table, no, no2], axis=1)

    two_wey_table.sort_values(['start_no','end_no'], inplace=True) 


    return two_wey_table[['start_no', 'end_no', 'start_id', 'end_id', 'start_latlong', 'end_latlong', 'linear_distance']]

def get_linear_distance(df):
    '''
    Use two points of latitude and longitude to get the straight line distance.

    warn
    ---
    `start_latlong` and `end_latlong` must exist in the field. 

    Both `start_latlong` and `end_latlong` need to comply with the following format: "25.10514,121.5182"
    '''
    for col in ['start_latlong', 'end_latlong']:
        assert (col in df.columns)

    df['linear_distance'] = df.apply(lambda x:geodesic(x['start_latlong'].split(','),x['end_latlong'].split(',')).meters,axis=1)

    return df

def get_adj_value(df, threshold=0):
    '''The formula is `exponent (-1 * square (df['linear_distance']) / square (variance))`'''
    assert threshold>=0, '`threshold` must be greater than zero'
    Variation = np.var(df['linear_distance'].values)
    adj_ls = np.exp(-1*np.square(df['linear_distance'].values)/Variation)
    df['adj'] = list(map(lambda x: x if x >= threshold else 0, adj_ls))

    return df