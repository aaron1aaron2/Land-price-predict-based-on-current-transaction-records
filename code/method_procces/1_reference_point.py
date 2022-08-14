"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.08.14
Last Update: 2022.08.14
Describe: 設立對應的參考點
"""
import os
import pandas as pd

from sklearn.cluster import DBSCAN
from geopy.distance import geodesic


output_folder = 'data/method_procces/1_reference_point'
os.makedirs(output_folder, exist_ok=True)