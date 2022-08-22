# encoding: utf-8
"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.08.22
Last Update: 2022.08.22
Describe: 集合所有方法步驟，可以一次性的透過參數設定整理資料。
"""
import yaml
from yaml.loader import SafeLoader




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