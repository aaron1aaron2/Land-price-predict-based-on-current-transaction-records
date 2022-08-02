"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.08.02
Last Update: 2022.08.02
Describe: 爬蟲部分大致上和 2_get_coordinate.py 功能依樣，這部分是爬取上步驟轉完的新地號
"""

import os
import json
import time
import argparse
import requests
import pandas as pd

from tqdm import tqdm

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--file_path', type=str, default='data/procces/1_sort_data/transaction_land.csv')
    parser.add_argument('--output_folder', type=str, default='data/procces/2_coordinate_data')

    parser.add_argument('--county_col', type=str, default='county')
    parser.add_argument('--district_col', type=str, default='district')
    parser.add_argument('--section_col', type=str, default='section_new')
    parser.add_argument('--number_col', type=str, default='number_new')

    args = parser.parse_args()

    return args

def get_coordinate(df:pd.DataFrame, output:str, county:str, district:str, section:str, number:str) -> None:
    result_path = os.path.join(output, 'crawler_result.csv')
    miss_path = os.path.join(output, 'crawler_miss.csv')

    print(f'Total tasks: {df.shape[0]}')
    # 爬蟲進度恢復
    if os.path.exists(result_path):
        tmp = df[county] + df[district] + df[section] + df[number]

        progress_df = pd.read_csv(result_path)
        miss_df = pd.read_csv(miss_path)

        all_df = pd.concat([progress_df, miss_df])

        df = df[~tmp.isin(all_df[county] + all_df[district] + all_df[section] + all_df[number])]

        del tmp; del progress_df; del miss_df

        print(f'Current progress: {df.shape[0]}\n')

    # 爬蟲
    land_addr_dt_ls = df.to_dict(orient="records")
    for i in tqdm(land_addr_dt_ls):
        url = f"https://twland.ronny.tw/index/search?lands[]={i[county]},{i[section]},{i[number]}"
        r = requests.get(url)

        if r.status_code != 200:
            print(f'error! \ {i}')
            exit()

        try:
            respond_data = r.json()

            properties = respond_data["features"][0]["properties"]

            saveJson(properties, 
                    path=os.path.join(output, 'record.json'),
                    mode='append_row')

            coordinate_dt = {k:v for k,v in properties.items() if k in ['xcenter', 'ycenter']}

            if len(coordinate_dt)==2:
                i.update(coordinate_dt)
                output_csv(i, result_path)
            else:
                output_csv(i, miss_path)

        except:
            output_csv(i, miss_path)

        time.sleep(0.5)

def output_csv(data:dict, path:str) -> None:
    pd.DataFrame([data]).to_csv(path, mode='a', index=False, header=not os.path.exists(path))
    
def saveJson(data:dict, path:str, mode:str) -> None:
    if mode == 'nor_write':
        with open(path, 'w', encoding='utf-8') as outfile:  
            json.dump(data, outfile, indent=2, ensure_ascii=False)
    if mode == 'append_row':
        with open(path, 'a', encoding='utf-8') as outfile:  
            json.dump(data, outfile, ensure_ascii=False)
            outfile.write('\n')

def main():
    # 參數處理
    args = get_args()
    print("="*20 + '\n' + str(args) + '\n')

    os.makedirs(args.output_folder, exist_ok=True)

    saveJson(args.__dict__, 
            path=os.path.join(args.output_folder, 'configures.json'),
            mode='nor_write')

    # 讀取資料
    assert os.path.exists(args.file_path), f"Input file could not be found at {args.file_path}"
    df = pd.read_csv(args.file_path, low_memory=False)

    # 爬取座標資料
    get_coordinate(df, args.output_folder, args.county_col, args.district_col, args.section_col, args.number_col)

if __name__ == '__main__':
    main()

