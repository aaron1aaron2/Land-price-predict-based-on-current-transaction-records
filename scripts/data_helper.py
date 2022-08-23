# encoding: utf-8
"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.08.22
Last Update: 2022.08.22
Describe: 集合所有方法步驟，可以一次性的透過參數設定整理資料。
"""
import argparse

import yaml
from yaml.loader import SafeLoader

def get_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--config_path', type=str, default='configs/Basic.yaml')

    config = read_config(parser.parse_known_args()[0].config_path)

    # 讀取並合併 config 檔
    full_parser = argparse.ArgumentParser(parents=[parser])
    for k, v in config.items():
        full_parser.add_argument(f'--{k}', default=v)

    return full_parser.parse_args()

def read_config(path):
    with open(path, 'r') as f:
        data = yaml.load(f, Loader=SafeLoader)
    return data

args = get_args()














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