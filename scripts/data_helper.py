# encoding: utf-8
"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.08.22
Last Update: 2022.08.22
Describe: 集合所有方法步驟，可以一次性的透過參數設定整理訓練所需資料。
"""
import os
import json
import argparse
import pandas as pd

import yaml
from yaml.loader import SafeLoader
from pathlib import Path

from IPython import embed


def get_args():
    parser = argparse.ArgumentParser(add_help=False)

    # file path
    parser.add_argument('--config_path', type=str, default='configs/Basic.yaml')
    parser.add_argument('--file_path', type=str, default='data/basic/transaction.csv')
    parser.add_argument('--id_file_path', type=str, default='data/basic/target.csv')
    parser.add_argument('--output_folder', type=str, default='data/train_data/basic')

    # columns use
    parser.add_argument('--id_col', type=str, default='sno') 
    parser.add_argument('--value_col', type=str, default='sbi')
    parser.add_argument('--date_col', type=str, default='date')
    parser.add_argument('--time_col', type=str, default='time')

    # other setting
    parser.add_argument('--with_csv', dest='with_csv', action='store_true', help='順便輸出csv')
    parser.add_argument('--no-csv', dest='with_csv', action='store_false', help='不輸出csv')
    parser.add_argument('--useid_th', default=1,
                        help='unuse id')

    parser.set_defaults(with_csv=True)

    args = vars(parser.parse_args())
    config = read_config(args['config_path'])['data_helper']
    args.update(config)

    return args


def build_folder(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def saveJson(data, path):
    with open(path, 'w', encoding='utf-8') as outfile:  
        json.dump(data, outfile, indent=2, ensure_ascii=False)

def save_config(data, path):
    with open(path, 'w') as f:
        data = yaml.dump(data, f, sort_keys=False, default_flow_style=False)

def read_config(path):
    with open(path, 'r') as f:
        data = yaml.load(f, Loader=SafeLoader)
    return data

def main():
    # 參數設定
    args = get_args()
    print("="*20 + '\n' + str(args))
    build_folder(args.output_folder)

    # saveJson(args.__dict__, os.path.join(args.output_folder, 'configures.json'))
    save_config(args.__dict__, os.path.join(args.output_folder, 'configures.yaml'))

    output_path = os.path.join(args.output_folder, 'data.h5')

    if os.path.exists(output_path):
        print("data.h5 is already build at ({})".format(output_path))
        exit()

    print("building data.h5 at ({})".format(output_path))

    # 讀取檔案
    df_info = pd.read_csv(args.id_file_path)
    df = pd.read_csv(args.file_path, dtype=str)
    col_reads = [args.id_col, args.value_col, args.date_col, args.time_col]
    if args.group != None:
        col_reads.append(args.group_col)
        group_use_ls = args.group.split(',')
        df = df[df[args.group_col].isin(group_use_ls)]
        df_info = df_info[df_info[args.group_col].isin(group_use_ls)]

    df[args.id_col] = df[args.id_col].astype(int)

    # 移除 act 小於 usid_th 的站點，因為未使用
    total_timestep = df[df[args.id_col] == df[args.id_col].unique()[0]].shape[0]
    act_stat = df.groupby([args.id_col])['act'].apply(lambda x: x.astype(int).sum())
    act_stat_df = pd.DataFrame({args.id_col:act_stat.index, 'act_ct':act_stat}).reset_index(drop=True)
    act_stat_df['act_ct'] = act_stat_df['act_ct']/total_timestep

    use_id = act_stat_df.loc[act_stat_df['act_ct'] >= args.useid_th, args.id_col]

    df = df[df[args.id_col].isin(use_id)]
    df_info = df_info[df_info[args.id_col].isin(use_id)]

    # 要給予從0開始的新 id
    id_table = df.loc[:, [args.id_col]].drop_duplicates()
    id_table.reset_index(drop=True, inplace=True)
    id_table['new_id'] = id_table.index

    df_info = df_info.merge(id_table, how='left')

    df_info.to_csv(os.path.join(args.output_folder,'spot_info_id_table.csv'), index=False)

    df = df.merge(id_table, how='left')

    # 轉換成 datetime 格式
    df['datetime'] = df[args.date_col] + '.' + df[args.time_col]
    df['datetime'] = pd.to_datetime(df['datetime'], format=r'%Y.%m.%d.%H%M%S')  

    # 將表扭曲成 row(datetime), columns(id), value
    df_pvt = df.pivot(index='datetime', columns='new_id', values=args.value_col)
    df_pvt.to_hdf(os.path.join(args.output_folder, 'data.h5'), key='data', mode='w')
    if args.with_csv:
        df_pvt.to_csv(os.path.join(args.output_folder, 'data.csv'))
    
    print(f'Successful output data to ({output_path})')
if __name__ == '__main__':
    main()





# Example ==================================================
# Open the file and load the file
"""
with open('Basic.yaml') as f:
    data = yaml.load(f, Loader=SafeLoader)
    print(data)

user_details = {'UserName': 'Alice',
                'Password': 'star123*',
                'phone': 3256,
                'AccessKeys': ['EmployeeTable',
                               'SoftwaresList',
                               'HardwareList'],
                'dict_test':{
                    'a': True,
                    'b': False,
                    'c': [1, 2, 3]
                }}

UserName: Alice
Password: star123*
phone: 3256
AccessKeys:
- EmployeeTable
- SoftwaresList
- HardwareList
dict_test:
  a: true
  b: false
  c:
  - 1
  - 2
  - 3


with open('UserDetails.yaml', 'w') as f:
    data = yaml.dump(user_details, f, sort_keys=False, default_flow_style=False)

"""