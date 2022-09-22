# encoding: utf-8
"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.09.06
Last Update: 2022.09.19
Describe: 集合所有方法步驟，可以一次性的透過參數設定整理訓練所需資料。
"""
import re
import os
import tqdm

import warnings
import argparse
# import importlib

import pandas as pd
from pandas.core.common import SettingWithCopyWarning

from PropGman.utils import *

from PropGman.method import reference_point
from PropGman.method.land_group import LandGroup
from PropGman.method.corrdinate_distance import get_distance
from PropGman.method.regional_index import RegionalIndex

from IPython import embed

warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

def get_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--config_path', type=str, default='configs/Basic.yaml')

    args = vars(parser.parse_args())
    config = read_config(args['config_path'])
    args.update(config)

    return args

# Step 3: Calculate distance matrix ==========================================================
def get_distance_table(df_target:pd.DataFrame, df_tran:pd.DataFrame, tran_coor_col:str, target_coor_cols:list,
            tran_id_col:str, group_id_col:str, output_folder:str, max_distance:int) -> list:
    df_target = df_target[[group_id_col] + target_coor_cols].drop_duplicates()
    df_tran = df_tran[[tran_id_col, tran_coor_col]]
    for gp_id in tqdm.tqdm(df_target[group_id_col].to_list()):
        df_coor = df_tran.copy()
        df_coor[group_id_col] = gp_id
        df_coor = df_coor.merge(df_target, how='left', on=[group_id_col])

        # 計算參考點與目標點的距離
        df_coor_dup = df_coor.drop_duplicates(target_coor_cols + [tran_coor_col])
        for col in target_coor_cols:
            df_coor_dup = df_coor_dup.assign(**{f'{col}_DIST':list(map(get_distance, df_coor_dup[[tran_coor_col, col]].values))})
            df_coor_dup = df_coor_dup[~(df_coor_dup[f'{col}_DIST']=='')]

        # 不儲存距離超過 max_distance 的經緯度距離
        result = df_coor_dup[(df_coor_dup[[f'{col}_DIST' for col in target_coor_cols]]<max_distance).all(axis=1)]
        
        result.to_csv(os.path.join(output_folder, f'group{gp_id}_DIST.csv'), index=False)

# Step 4: Calculate customized index ===================================================================
def get_customized_index(distance_mat_folder:str, df_tran:pd.DataFrame, method:str, target_cols:list, target_value_col:str, id_col:str,
        start_date:str, end_date:str, time_freq:str, dist_threshold:int):

    regional_index = RegionalIndex(start_date, end_date, time_freq, dist_threshold)

    # 為了看進度，不使用雙 for
    task_ls = [(gp_file, col) for gp_file in os.listdir(distance_mat_folder) for col in target_cols]
    fill_result_dt_ls = []

    pre_gp_file = ''
    result_df = pd.DataFrame()
    gp_table = regional_index.date_table.copy()

    for gp_file, col in tqdm.tqdm(task_ls):
        gp = re.search('group(\d+)', gp_file)
        gp = int(gp[1]) if gp != None else ''

        if gp_file != pre_gp_file:
            df_distance = pd.read_csv(os.path.join(distance_mat_folder, gp_file), usecols=['land_id'] + target_cols)

        result, record = regional_index.get_index(
            df_distance, df_tran, 
            method=method, target_value_col=target_value_col, 
            dist_value_col=col, id_col=id_col)

        record.update({'file': gp_file})
        fill_result_dt_ls.append(record)

        # 控制: 當每個 group 的目標點 & 參考點結束時 
        if (gp_file == pre_gp_file) | (pre_gp_file==''):
            gp_table[col] = result
            if all([i in gp_table.columns for i in target_cols]):
                gp_table['group'] = gp
                result_df = result_df.append(gp_table)
        else:
            gp_table = regional_index.date_table.copy()
            gp_table[col] = result

    result_df.rename(columns={
            i:i.replace('_DIST','') for i in target_cols
        }, inplace=True)

    return result_df, pd.DataFrame(fill_result_dt_ls)

# Step 5: Create training data ===============================================================
def get_train_data(df:pd.DataFrame, id_dt:dict, datetime_col:str, cus_format:str, target_value_cols:list) -> pd.DataFrame:
    # 轉換成 datetime 格式
    df[datetime_col] = pd.to_datetime(df[datetime_col], format=cus_format)  
    df = df[[datetime_col] + target_value_cols]

    df.set_index(datetime_col, inplace=True)

    df.rename(columns=id_dt, inplace=True)

    return df

# Step 6: generate SE data ===================================================================



# main process =================================================
def main():
    # 參數設定 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    args = get_args()
    print("="*20 + f'\n{str(args)}\n'+ "="*20)

    # 主要參數 --------------
    output_proc = args['control']['output_proc_file']

    main_out_folder = args['output_folder']['main']
    proc_out_folder = args['output_folder']['proc']

    # 輸出資料夾 -----------
    build_folder(main_out_folder)
    if output_proc: 
        build_folder(proc_out_folder)

    config_path = os.path.join(main_out_folder, 'configures.yaml')

    if (os.path.exists(config_path)):
        print('load the record config')
        args = read_config(config_path)
    else:
        save_config(args, config_path)

    print(f'Config has written to the {config_path}')

    record = args['procces_record']

    main_output_path = os.path.join(main_out_folder, 'data.h5')

    if os.path.exists(main_output_path):
        print("data.h5 is already build at ({})".format(main_output_path))
        exit()

    # 讀取檔案 -------------
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
        land_gp = LandGroup(method=args['method']['1_group_method'])
        df_group = land_gp.main(
                df_target,
                distance_threshold=args['method']['1_distance_threshold'],
                id_col=args['column']['target']['id'],
                coordinate_col=args['column']['target']['coordinate'],
            )
        if output_proc:
            df_group.to_csv(output_file, index=False)

        args = update_config(args, config_path, 'procces_record', {'step1': True})
        args = update_config(args, config_path, 'output_files', {'1_target_land_group': output_file})
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


    # Step 2: Get reference point >>>>>>>>>>>>>>>>
    print("\nGet reference point...")
    output_file = os.path.join(proc_out_folder, '2_reference_point.csv')
    if (record['step2'] & output_proc):
        print("load record")
        df_refer_point = pd.read_csv(output_file)
    else:
        # get_reference_point = getattr(importlib.import_module('PropGman.method.reference_point'), args['method']['2_reference_point_func'])
        get_reference_point = getattr(reference_point, 
                        args['method']['2_reference_point_func'])
        df_refer_point = get_reference_point(
                df=df_group,
                target_coordinate_cols=args['column']['procces']['target_coordinate_cols'],
                distance=args['method']['2_reference_point_distance'],
                lat_per_100_meter=args['method']['2_lat_degree_per_100_meter'],
                long_per_100_meter=args['method']['2_long_degree_per_100_meter'] 
            )

        if output_proc:
            df_refer_point.to_csv(output_file, index=False)

        args = update_config(args, config_path, 'procces_record', {'step2': True})
        args = update_config(args, config_path, 'output_files', {'2_reference_point': output_file})
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


    # Step 3: Calculate distance matrix >>>>>>>>>>>>>>>>>
    print("\nCalculate distance matrix...")
    output_folder = os.path.join(proc_out_folder, '3_distance_matrix')
    build_folder(output_folder)
    if (record['step3'] & output_proc):
        print("check record")
        for gp in df_group['group_id'].unique():
            file_name = f'group{gp}_DIST.csv'
            assert file_name in os.listdir(output_folder), f'load faile: file {file_name} not found'
    else:
        get_distance_table(
            df_refer_point, df_tran, 
            tran_coor_col=args['column']['transaction']['coordinate'],
            target_coor_cols=args['column']['procces']['target_coordinate_cols'],
            group_id_col=args['column']['procces']['target_id_col'],
            tran_id_col=args['column']['transaction']['land_id'],
            max_distance=args['method']['3_max_distance'],
            output_folder=output_folder
        )
        args = update_config(args, config_path, 'procces_record', {'step3': True})
        args = update_config(args, config_path, 'output_files', {'3_distance_matrix': {'folder':output_folder, 'files':os.listdir(output_folder)}})
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


    # Step 4: Calculate customized Regional Index >>>>>>>>>
    print("\nCalculate customized Regional Index...")
    output_folder = os.path.join(proc_out_folder, '4_regional_index')
    build_folder(output_folder)
    if (record['step4'] & output_proc):
        print("check record")
        for file in args['output_files']['4_regional_index']['files']:
            assert file in os.listdir(output_folder), f'file {file} not found at {output_folder}'
    else:
        for method in args['method']['4_index_method']:
            print(f'method - {method}')
            output_file = os.path.join(output_folder, f'{method}.csv')
            if not os.path.exists(output_file):
                result_df, fillna_result = get_customized_index(
                    distance_mat_folder=args['output_files']['3_distance_matrix']['folder'], 
                    df_tran=df_tran, 
                    method=method, 
                    target_cols=[i + '_DIST' for i in args['column']['procces']['target_coordinate_cols']],
                    id_col=args['column']['transaction']['land_id'], 
                    target_value_col=args['column']['transaction']['value'], 
                    start_date=args['method']['4_index_start_date'], 
                    end_date=args['method']['4_index_end_date'], 
                    time_freq=args['method']['4_index_time_freq'], 
                    dist_threshold=args['method']['4_index_distance_threshold']
                )
                result_df.to_csv(output_file, index=False)
                fillna_result.to_csv(output_file.replace('.csv', '_fillna.csv'), index=False)
            else:
                print(f'file exist: {output_file}')

        args = update_config(args, config_path, 'procces_record', {'step4': True})
        args = update_config(args, config_path, 'output_files', {'4_regional_index': {'folder':output_folder, 'files':os.listdir(output_folder)}})
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


    # Step 5: Create training data >>>>>>>>>>>>>>>
    print("\nCreate training data...")
    output_folder = os.path.join(main_out_folder, 'train_data')
    build_folder(output_folder)
    if (record['step5'] & output_proc):
        print("check record")
        for file in args['output_files']['5_train_data']['files']:
            assert file in os.listdir(output_folder), f'file {file} not found at {output_folder}'
    else:
        id_table = pd.DataFrame(
                    [(i, col) for i, col in enumerate(args['column']['procces']['target_coordinate_cols'])],
                    columns=['id', 'columns']
            )
        id_table.to_csv(os.path.join(output_folder, 'id_table.csv'), index=False)
        for method in tqdm.tqdm(args['method']['4_index_method']):
            df_index = pd.read_csv(os.path.join(
                        args['output_files']['4_regional_index']['folder'], 
                        f'{method}.csv'
                    ))
            df_index['datetime'] = df_index['year'].astype(str) + '-' + df_index['month'].astype(str) 

            for gp in df_index['group'].unique():
                result = get_train_data(
                    df=df_index[df_index['group']==gp], 
                    datetime_col='datetime', 
                    cus_format='%Y-%m', # %Y 年、 %m 月、%d 日、%H 時、%M 分、%S 秒 
                    target_value_cols=args['column']['procces']['target_coordinate_cols'], 
                    id_dt={col:i for i, col in id_table.values}
                )
                result.to_hdf(os.path.join(output_folder, f'{method}_group{gp}.h5'), key='data', mode='w')

        args = update_config(args, config_path, 'procces_record', {'step5': True})
        args = update_config(args, config_path, 'output_files', {'5_train_data': {'folder':output_folder, 'files':os.listdir(output_folder)}})
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    exit()
    # Step 6: Generate SE data >>>>>>>>>>>>>>>>>>>
    print("\nGenerate SE data...")
    print("\nCreate training data...")
    output_folder = os.path.join(main_out_folder, 'SE_data')
    build_folder(output_folder)
    if (record['step6'] & output_proc):
        print("check record")
        for method in tqdm.tqdm(args['method']['4_index_method']):
            assert f'{method}.csv' in os.listdir(output_folder), f'file {method}.csv not found at {output_folder}'
    else:


        args = update_config(args, config_path, 'procces_record', {'step6': True})
        args = update_config(args, config_path, 'output_files', {'6_SE_data': {'folder':output_folder, 'files':os.listdir(output_folder)}})

    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


if __name__ == '__main__':
    main()