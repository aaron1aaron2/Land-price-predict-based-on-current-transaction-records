# encoding: utf-8
"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.09.09
Last Update: 2022.09.09
Describe: 獲取所有時價登入土地與目標土地經緯度之間的直線距離。
"""
import tqdm
import pandas as pd

from geopy.distance import geodesic

def get_distance(x):
    """部分經緯度有問題"""
    try:
        lat1, long1 = x[0].split(',')
        lat2, long2 = x[1].split(',')

        if (abs(float(lat1)) <= 90) & (abs(float(lat2)) <= 90) & (float(long1)<180) & (float(long2)<180):
            return geodesic([lat1, long1],[lat2, long2]).meters
        else:
            return ''

    except:
        return ''