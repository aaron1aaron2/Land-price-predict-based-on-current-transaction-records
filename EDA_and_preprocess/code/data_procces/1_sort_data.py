# encoding: utf-8
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

output = 'data/data_procces/1_sort_data'

os.makedirs(output, exist_ok=True)

# 處理交易資訊 ==============================
## 土地
transaction_df = pd.read_csv('data/data_procces/0_merge_data/h_lvr_land_a.csv', low_memory=False)

land_transaction_df = transaction_df[transaction_df["交易標的"] == "土地"]

# 處理亂碼
replace_dt = {
    '.+榔段上.+榔小段': '槺榔段上槺榔小段',
    '.+榔段下.+榔小段': '槺榔段下槺榔小段',
    '.+頭洲段.+頭洲小段': '犂頭洲段犂頭洲小段',
    '番婆.+段': '番婆坟段'
    }

for i,v in replace_dt.items():
    land_transaction_df['土地位置建物門牌'] = land_transaction_df['土地位置建物門牌'].str.replace(i, v)

land_transaction_df['土地位置'] = '桃園市' + land_transaction_df['鄉鎮市區'] + land_transaction_df['土地位置建物門牌']

# 移除空值
land_transaction_df = land_transaction_df[~land_transaction_df['土地位置'].isna()]
land_transaction_df = land_transaction_df[~land_transaction_df['單價元平方公尺'].isna()]

# 重複值
land_transaction_df.drop_duplicates(subset=["鄉鎮市區", "土地位置建物門牌", "交易年月日"], inplace=True)

# 日期問題(6 位的都有問題)
land_transaction_df = land_transaction_df[land_transaction_df["交易年月日"].astype("str").str.len() == 7]

# 抽取日期
land_transaction_df = land_transaction_df.join(
    land_transaction_df['交易年月日'].astype("str").str.extract('(?P<year>\d{3})(?P<month>\d{2})(?P<day>\d{2})')
    )
land_transaction_df = land_transaction_df[~((land_transaction_df.day == '00') | (land_transaction_df.month=='00'))]

land_transaction_df.to_csv(os.path.join(output, 'transaction_land.csv'), index=False)

# --------------------------------------------------- 以下為保留空間 ---------------------------------------------------

# 處理預售屋資訊 ==============================




# 處理租賃資訊 ==============================
## 土地
# rent_df = pd.read_csv('data/merge_data/h_lvr_land_c.csv', low_memory=False)

# land_rent_df = rent_df[rent_df["交易標的"] == "土地"]
# land_rent_df['土地位置'] = '桃園市' + land_rent_df['鄉鎮市區'] + land_rent_df['土地位置建物門牌']

# land_rent_df.to_csv(os.path.join(output, 'rent_land.csv'), index=False)
