"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.08.14
Last Update: 2022.08.14
Describe: 設立對應的參考點。上下左右(3000公尺)的位置。關於範圍設定可以看 code/supplementary/m0__effective_range_select.py
"""
import os
import pandas as pd

from geopy.distance import geodesic


output_folder = 'data/method_procces/1_reference_point'
os.makedirs(output_folder, exist_ok=True)

df = pd.read_csv('data/method_procces/0_target_land_group/target_land_group.csv')