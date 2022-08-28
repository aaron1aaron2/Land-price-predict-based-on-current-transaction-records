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
import sys
import json
import argparse
import pandas as pd

import yaml
from yaml.loader import SafeLoader
from pathlib import Path


def get_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--config_path', type=str, default='configs/Basic.yaml')

    parser.add_argument('--file_path', type=str, default='data/youbike_sort/data.csv')
    parser.add_argument('--id_file_path', type=str, default='data/youbike_sort/spot_info.csv')
    parser.add_argument('--output_folder', type=str, default='data/train_data/')
    parser.add_argument('--id_col', type=str, default='sno') 
    parser.add_argument('--value_col', type=str, default='sbi')
    parser.add_argument('--date_col', type=str, default='date')
    parser.add_argument('--time_col', type=str, default='time')

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

def read_config(path):
    with open(path, 'r') as f:
        data = yaml.load(f, Loader=SafeLoader)
    return data

def main():
    args = get_args()

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