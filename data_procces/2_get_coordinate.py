"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.07.25
Last Update: 2022.07.29
Describe: 地號切分 + 獲取土地經緯度座標。土地位置來源 「地號 GeoJSON API」。2015 年的資料 -> https://twland.ronny.tw/
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
    parser.add_argument('--output_folder', type=str, default='data/procces/2_get_coordinate')

    parser.add_argument('--landid_col', type=str, default='土地位置', help='土地位置與地號欄位名稱')

    parser.add_argument('--extract_pattern', type=str, 
                        default='(?P<county>\w+市)(?P<district>\w{2}區)(?P<section>\w+段)(?P<number>.+)地號', 
                        help='土地資訊切分 regex pattern。須包含 county、district、section、number 四個資訊，可參考 default format。')

    args = parser.parse_args()

    return args

def extract_pattern(df:pd.DataFrame, pattern:str, output:str) -> pd.DataFrame:
    extract_df = df.str.extract(pattern)

    # 輸出檢查用資料
    df[extract_df.isna().any(axis=1)].to_csv(os.path.join(output, 'extract_miss.csv'))
    pd.DataFrame(df).join(extract_df).to_csv(os.path.join(output, 'extract_result.csv'), index=False)

    return extract_df

def get_coordinate(df:pd.DataFrame, output:str) -> None:
    result_path = os.path.join(output, 'crawler_result.csv')
    miss_path = os.path.join(output, 'crawler_miss.csv')

    print(f'Total tasks: {df.shape[0]}')
    # 爬蟲進度恢復
    if os.path.exists(result_path):
        tmp = df['county'] + df['district'] + df['section'] + df['number']

        progress_df = pd.read_csv(result_path)
        miss_df = pd.read_csv(miss_path)

        all_df = pd.concat([progress_df, miss_df])

        df = df[~tmp.isin(all_df['county'] + all_df['district'] + all_df['section'] + all_df['number'])]

        del tmp; del progress_df; del miss_df

        print(f'Current progress: {df.shape[0]}\n')

    # 爬蟲
    land_addr_dt_ls = df.to_dict(orient="records")
    for i in tqdm(land_addr_dt_ls):
        url = f"https://twland.ronny.tw/index/search?lands[]={i['county']},{i['section']},{i['number']}"
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

    assert args.landid_col in df.columns, f"{args.landid_col} attribute could not be found in input file"
    land_addr_df = df[args.landid_col].drop_duplicates().reset_index(drop=True)

    # 抽取土地資訊
    extract_df = extract_pattern(land_addr_df, args.extract_pattern, args.output_folder)

    # 爬取座標資料
    get_coordinate(extract_df, args.output_folder)

if __name__ == '__main__':
    main()

