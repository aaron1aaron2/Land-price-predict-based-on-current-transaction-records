"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.07.25
Last Update: 2022.07.25
Describe: 獲取土地經緯度座標，來源 -> https://twland.ronny.tw/
"""

import os
import json
import argparse
import requests
import pandas as pd

from IPython import embed
# from tqdm import tqdm

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--file_path', type=str, default='data/sort_data/transaction_land.csv')
    parser.add_argument('--output_folder', type=str, default='data/coordinate_data')

    parser.add_argument('--landid_col', type=str, default='土地位置', help='土地位置與地號欄位名稱')
    parser.add_argument('--extract_pattern', type=str, 
                        default='(?P<county>\w+市)(?P<district>\w+區)(?P<section>\w+段)(?P<number>.+)地號', 
                        help='土地資訊切分 regex pattern。(須包含 county、district、section、number 四個資訊，可參考 default)')


    args = parser.parse_args()

    return args

def saveJson(data, path):
    with open(path, 'w', encoding='utf-8') as outfile:  
        json.dump(data, outfile, indent=2, ensure_ascii=False)

def main():
    # 參數
    args = get_args()
    print("="*20 + '\n' + str(args))
    saveJson(args.__dict__, os.path.join(args.output_folder, 'configures.json'))

    os.makedirs(args.output_folder, exist_ok=True)

    # 讀取資料
    assert os.path.exists(args.file_path), f"Input file could not be found at {args.file_path}"
    df = pd.read_csv(args.file_path, low_memory=False)

    assert args.landid_col in df.columns, f"{args.landid_col} attribute could not be found in input file"
    landid_df = df[args.landid_col].drop_duplicates().reset_index(drop=True)

    landid_extract_df = landid_df.str.extract(args.extract_pattern)
    landid_df[landid_extract_df.isna().any(axis=1)].to_csv(os.path.join(args.output_folder, 'pattern_miss.csv'))
    pd.DataFrame(landid_df).join(landid_extract_df).to_csv(os.path.join(args.output_folder, 'extract_result.csv'), index=False)

    embed()
    exit()



    pass

if __name__ == '__main__':
    main()

