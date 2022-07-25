"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.07.24
Last Update: 2022.07.24
Describe: 獲取土地經緯度座標，來源 -> https://twland.ronny.tw/
"""
import re
import os
import glob
import pandas as pd

from tqdm import tqdm

path = 'data/merge_data'

file_ls = glob.glob(os.path.join(path, '*.csv'))

file_ls = [i for i in file_ls if re.search('h_lvr_land_\w\.csv', i)]