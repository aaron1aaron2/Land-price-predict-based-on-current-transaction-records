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
## 土地
transaction_df = pd.read_csv('data/merge_data/h_lvr_land_a.csv', low_memory=False)

land_transaction_df = transaction_df[transaction_df["交易標的"] == "土地"]
land_transaction_df['土地位置'] = '桃園市' + land_transaction_df['鄉鎮市區'] + land_transaction_df['土地位置建物門牌']

# 處理亂碼
{'榔段上榔小段': '槺榔段上槺榔小段',
'榔段下榔小段': '槺榔段下槺榔小段',
'番婆段': '番婆坟段'}


land_transaction_df.to_csv(os.path.join(output, 'transaction_land.csv'), index=False)
# 處理預售屋資訊 ==============================




# 處理租賃資訊 ==============================
## 土地
rent_df = pd.read_csv('data/merge_data/h_lvr_land_c.csv', low_memory=False)

land_rent_df = rent_df[rent_df["交易標的"] == "土地"]
land_rent_df['土地位置'] = '桃園市' + land_rent_df['鄉鎮市區'] + land_rent_df['土地位置建物門牌']

land_rent_df.to_csv(os.path.join(output, 'rent_land.csv'), index=False)
