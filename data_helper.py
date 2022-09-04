# encoding: utf-8
"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.08.29
Last Update: 2022.09.04
Describe: 集合所有方法步驟，可以一次性的透過參數設定整理訓練所需資料。
"""
import os
import json
import warnings
import argparse
import itertools
import importlib

import pandas as pd
from pandas.core.common import SettingWithCopyWarning

import yaml
from yaml.loader import SafeLoader

from pathlib import Path
from sklearn.cluster import DBSCAN
from geopy.distance import geodesic

from IPython import embed

warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

def get_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--config_path', type=str, default='configs/Basic.yaml')

    args = vars(parser.parse_args())
    config = read_config(args['config_path'])
    args.update(config)

    return args

# Step 1: group land use DBSCAN ==============================================================
def get_DBSCAN_group(df:pd.DataFrame, distance_threshold:int, id_col:str, coordinate_col:str) -> pd.DataFrame:
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

    # 分群
    db = DBSCAN(eps=distance_threshold, min_samples=2, metric='precomputed').fit(distanct_mat) # precomputed 代表使用距離矩陣
    df[f'DBSCAN'] = db.labels_

    # 建立 group id
    cur_id = df['DBSCAN'].max() +1

    result = []
    for i in df['DBSCAN'].to_list():
        result.append(i) if i !=-1 else result.append(cur_id)
        if i==-1: cur_id += 1

    df['group_id'] = result

    df = df.join(df['coordinate'].str.extract('(?P<lat>.+),(?P<long>.+)').astype(float))

    group_center = df.groupby('group_id').apply(lambda gp: f"{gp['lat'].mean()},{gp['long'].mean()}").reset_index()
    group_center.rename({0:'group_center'}, axis=1, inplace=True)

    df = df.merge(group_center, how='left')
    df.drop(['lat', 'long'], axis=1, inplace=True)

    return df

# Step 2: reference_point ==========================================================
def reference_point(module, func, **kwargs)->pd.DataFrame:
    # exec(f"from {module} import {func} as my_reference_point") # 讀取延遲
    my_reference_point = getattr(importlib.import_module(f'{module}'), func)

    return my_reference_point(**kwargs)

# Step 3: Calculate distance matrix ==========================================================



# Step 4: Calculate customized index ===================================================================



# Step 5: Create training data ===============================================================
def train_data(df, value_col, date_col, time_col, output_folder, with_csv):
    col_reads = [value_col, date_col, time_col]
    df['new_id'] = df.index
    # 轉換成 datetime 格式
    df['datetime'] = df[date_col] + '.' + df[time_col]
    df['datetime'] = pd.to_datetime(df['datetime'], format=r'%Y.%m.%d.%H%M%S')  

    # 將表扭曲成 row(datetime), columns(id), value
    df_pvt = df.pivot(index='datetime', columns='new_id', values=value_col)
    df_pvt.to_hdf(os.path.join(output_folder, 'data.h5'), key='data', mode='w')
    if with_csv:
        df_pvt.to_csv(os.path.join(output_folder, 'data.csv'))

# Step 6: generate SE data ===================================================================




# utils ======================================================================================
def build_folder(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def saveJson(data, path):
    with open(path, 'w', encoding='utf-8') as outfile:  
        json.dump(data, outfile, indent=2, ensure_ascii=False)

def save_config(data, path):
    with open(path, 'w', encoding='utf8') as f:
        data = yaml.dump(data, f, sort_keys=False, default_flow_style=False, allow_unicode=True)

def read_config(path):
    with open(path, 'r', encoding='utf8') as f:
        data = yaml.load(f, Loader=SafeLoader)
    return data

def update_config(data, path, update_locat, update_dt):
    if type(update_locat) == str:
        data[update_locat].update(update_dt)
    elif len(update_locat) == 1:
        data[update_locat[0]].update(update_dt)
    else:
        d = data
        for key in update_locat[:-1]:
            d = d[key]
        d.update(update_dt)

    save_config(data, path)

    return data

# main process =================================================
def main():
    # 參數設定 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    args = get_args()
    print("="*20 + f'\n{str(args)}\n'+ "="*20)

    # 主要參數 --------------
    output_proc = args['control']['output_proc_file']
    overwrite_record = args['control']['overwrite_record']

    main_out_folder = args['output_folder']['main']
    proc_out_folder = args['output_folder']['proc']

    # 輸出資料夾 -----------
    build_folder(main_out_folder)
    if output_proc: 
        build_folder(proc_out_folder)

    # config out -----------
    config_path = os.path.join(main_out_folder, 'configures.yaml')

    if (os.path.exists(config_path) & (not overwrite_record)):
        print('load the record config')
        args = read_config(config_path)
    else:
        save_config(args, config_path)

    print(f'Config has written to the {config_path}')

    record = args['procces_record']

    # data out -------------
    output_path = os.path.join(main_out_folder, 'data.h5')

    if os.path.exists(output_path):
        print("data.h5 is already build at ({})".format(output_path))
        exit()

    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # 讀取檔案 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    df_target = pd.read_csv(args['data']['target'])
    df_tran = pd.read_csv(args['data']['transaction'], dtype=str)
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # Step 1: group land use DBSCAN >>>>>>>>>>>>>>
    print("\nGroup land use DBSCAN...")
    output_file = os.path.join(proc_out_folder, '1_target_land_group.csv')
    if (record['step1'] & output_proc):
        print("load record")
        df_group = pd.read_csv(output_file)
    else:
        df_group = get_DBSCAN_group(
                df_target,
                distance_threshold=args['method']['1_distance_threshold'],
                id_col=args['column']['target']['id'],
                coordinate_col=args['column']['target']['coordinate'],
            )
        if output_proc:
            df_group.to_csv(output_file, index=False)
        args = update_config(args, config_path, 'procces_record', {'step1': True})
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # Step 2: Get reference point >>>>>>>>>>>>>>>>
    print("\nGet reference point...")
    output_file = os.path.join(proc_out_folder, '2_reference_point.csv')
    if (record['step2'] & output_proc):
        print("load record")
        df_refer_point = pd.read_csv(output_file)
    else:
        df_refer_point = reference_point(
                module=args['method']['2_reference_point_module'], 
                func=args['method']['2_reference_point_func'],
                df=df_group,
                distance=args['method']['2_reference_point_distance'],
                lat_per_100_meter=args['method']['2_lat_degree_per_100_meter'],
                long_per_100_meter=args['method']['2_long_degree_per_100_meter'] 
            )
        if output_proc:
            df_refer_point.to_csv(output_file, index=False)
        args = update_config(args, config_path, 'procces_record', {'step2': True})
    embed()
    exit()
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # Step 3: Calculate distance matrix >>>>>>>>>>>>>>>>>
    print("\nCalculate distance matrix...")

    args['procces_record']['step3'] = True
    save_config(args, config_path)
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # Step 4: Calculate customized index >>>>>>>>>
    print("\nCalculate customized index...")

    args['procces_record']['step4'] = True
    save_config(args, config_path)
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # Step 5: Create training data >>>>>>>>>>>>>>>
    print("\nCreate training data...")

    print(f'Successful output data.h5 to ({output_path})')
    args['procces_record']['step5'] = True
    save_config(args, config_path)
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # Step 6: Generate SE data >>>>>>>>>>>>>>>>>>>
    print("\nGenerate SE data...")

    args['procces_record']['step6'] = True
    save_config(args, config_path)
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


if __name__ == '__main__':
    main()