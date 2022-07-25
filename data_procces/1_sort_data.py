"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.07.25
Last Update: 2022.07.25
Describe: 各資料整理 & 特殊前處理
"""
import os
import pandas as pd

output = 'data/sort_data'

os.makedirs(output, exist_ok=True)

# 處理交易資訊 ==============================
transaction_df = pd.read_csv('data/merge_data/h_lvr_land_a.csv', low_memory=False)

# tran_build_df = pd.read_csv('data/merge_data/h_lvr_land_a_build.csv', low_memory=False)
# tran_land_df = pd.read_csv('data/merge_data/h_lvr_land_a_land.csv', low_memory=False)

transaction_df[transaction_df["交易標的"] == "土地"].to_csv(os.path.join(output, 'transaction_land.csv'), index=False)

# 處理預售屋資訊 ==============================




# 處理租賃資訊 ==============================
