"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.08.16
Last Update: 2022.08.19
Describe: 設立對應的參考點。上下左右(3000公尺)的位置。
            1. 經緯度加減度數對應距離，由 google map 桃園市中心點為基準測試 -> (24.9605666,121.2188135)
            2. 關於範圍設定可以看 code/supplementary/m0__effective_range_select.py
"""
import os
import pandas as pd

from geopy.distance import geodesic


output_folder = 'data/method_procces/1_reference_point'
os.makedirs(output_folder, exist_ok=True)

df = pd.read_csv('data/method_procces/0_target_land_group/target_land_group.csv')

# 經緯度轉換距離測試 ---------------------------------------

test_coordinate = '24.9605666,121.2188135'
lat, long = test_coordinate.split(',') 


for i in [round(i*0.005, 3) for i in range(1, 20)]:
    geodesic(x['start_coordinate'].split(','),x['end_coordinate'].split(',')).meters


def get_reference(meter):
    pass
