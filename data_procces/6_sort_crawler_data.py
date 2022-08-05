"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.08.04
Last Update: 2022.08.04
Describe: 爬蟲資料整理，與交易資料整合
"""
import os
import pandas as pd


output_folder = 'data/procces/6_sort_crawler_data'
os.makedirs(output_folder, exist_ok=True)

cols = ['year', 'month', 'day', '鄉鎮市區', '土地位置建物門牌', '土地移轉總面積平方公尺', '都市土地使用分區', 
        '非都市土地使用分區', '非都市土地使用編定', '交易筆棟數', '總價元', '單價元平方公尺']
transaction_df = pd.read_csv('data/procces/1_sort_data/transaction_land.csv', usecols=cols,low_memory=False)

coordinate_result_df = pd.read_csv('data/procces/2_get_coordinate/crawler_result.csv', low_memory=False)
coordinate_miss_df = pd.read_csv('data/procces/2_get_coordinate/crawler_miss.csv', low_memory=False)

land_code_tran_df = pd.read_csv('data/procces/3_land_code_transform/crawler_result.csv', low_memory=False)

coordinate_new_result_df = pd.read_csv('data/procces/4_get_coordinate(newcode)/crawler_result.csv', low_memory=False)

coordinate_all_df = pd.concat([coordinate_result_df, coordinate_miss_df])
coordinate_all_df.rename(columns={'xcenter': 'long', 'ycenter': 'lat'}, inplace=True)
del coordinate_miss_df; del coordinate_result_df

coordinate_all_df = coordinate_all_df.merge(land_code_tran_df[['county', 'district', 'section', 'number', 'section_new', 'number_new']], how='left')
del land_code_tran_df

coordinate_all_df = coordinate_all_df.merge(coordinate_new_result_df[['county', 'district', 'section', 'number', 'xcenter', 'ycenter']], how='left')
del coordinate_new_result_df

coordinate_all_df['long'] = coordinate_all_df.apply(lambda df: df['long'] if pd.isna(df['xcenter']) else df['xcenter'], axis=1)
coordinate_all_df['lat'] = coordinate_all_df.apply(lambda df: df['lat'] if pd.isna(df['ycenter']) else df['xcenter'], axis=1)

coordinate_all_df.drop(['xcenter', 'ycenter'], axis=1, inplace=True)

coordinate_all_df['land_id'] = coordinate_all_df.reset_index(drop=True).index + 1

coordinate_all_df.to_csv(os.path.join(output_folder, 'coordinate_all.csv'), index=False)

pat_extract = ('桃園市' + transaction_df['鄉鎮市區']  + transaction_df['土地位置建物門牌']
                ).str.extract('(?P<county>\w+市)(?P<district>\w{2}區)(?P<section>\w+段)(?P<number>.+)地號')

pat_extract = pat_extract.merge(coordinate_all_df[['county', 'district', 'section', 'number', 'long', 'lat', 'land_id']], how='left')

transaction_df = pat_extract.join(transaction_df)
transaction_df.drop(['鄉鎮市區', '土地位置建物門牌'], axis=1, inplace=True)

transaction_df.drop_duplicates(inplace=True)
transaction_df.to_csv(os.path.join(output_folder, 'transaction_coordinate_all.csv'), index=False)

transaction_df[~transaction_df['lat'].isna()].to_csv(os.path.join(output_folder, 'transaction_coordinate_use.csv'), index=False)
transaction_df[transaction_df['lat'].isna()].to_csv(os.path.join(output_folder, 'transaction_coordinate_miss.csv'), index=False)