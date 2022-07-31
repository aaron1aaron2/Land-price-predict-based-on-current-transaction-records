"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.07.28
Last Update: 2022.07.28
Describe: 將未爬取到的舊地號轉新地號，來源「桃園地政資訊服務網」 -> https://www.land.tycg.gov.tw/chaspx/SQry4.aspx/14
"""

import os
import json
import time
import argparse
import pandas as pd

from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException 

from webdriver_manager.chrome import ChromeDriverManager

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--file_path', type=str, default='data/procces/2_coordinate_data/crawler_miss.csv')
    parser.add_argument('--output_folder', type=str, default='data/procces/3_land_code_transform')

    args = parser.parse_args()

    return args

def get_new_land_code(df, output):
    result_path = os.path.join(output, 'crawler_result.csv')
    miss_path = os.path.join(output, 'crawler_miss.csv')

    chrome_options = Options()
    chrome_options.add_argument("--headless") # 無視窗
    chrome_options.add_argument("--incognito") # 無痕
    chrome_options.add_argument("--disable-software-rasterizer") # 無痕
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging']) # 忽略 log
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36")

    land_addr_dt_ls = df.to_dict(orient="records")

    for i in tqdm(land_addr_dt_ls):
        error_info = ''
        try:
            browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            
            browser.implicitly_wait(10) # 隱式等待

            browser.get("https://www.land.tycg.gov.tw/chaspx/SQry4.aspx/14")

            # 進入到互動 iframe
            browser.switch_to.frame(browser.find_element(By.XPATH, '//*[@title="新舊地建號查詢"]'))

            # 選擇搜尋服務類型
            type_select = Select(browser.find_element('name', 'searchtype'))
            type_select.select_by_visible_text('舊地號查新地號') # select.select_by_value('2')

            # 選擇區
            city_tar = browser.find_element('name', 'xcity')
            city_options = city_tar.find_elements(By.TAG_NAME, 'option')
            city = [ls_txt.text for ls_txt in city_options if ls_txt.text.find(i['district']) != -1] # 只取前兩字配對(市與區問題)

            if len(city) == 0:
                error_info = '找不到區'
            else:
                i.update({'district_match': city[0]})

            city_select = Select(city_tar)
            city_select.select_by_visible_text(city[0])
                
            # 選擇段
            area_tar = browser.find_element('name', 'xarea')
            area_options = area_tar.find_elements(By.TAG_NAME, 'option')
            area = [ls_txt.text for ls_txt in area_options if ls_txt.text.find(i['section']) != -1] # 只取前兩字配對(市與區問題)

            if len(area) == 0:
                error_info = '找不到段'
            else:
                i.update({'section_match': area[0]})

            area_select = Select(area_tar)
            area_select.select_by_visible_text(area[0])

            # 輸入舊地號
            landcode_tar = browser.find_element('name', 'xno')
            landcode_tar.send_keys(i['number'])

            # 送出
            summit_button = browser.find_element('id', 'btnSearch1')
            summit_button.send_keys(Keys.ENTER)

            # 儲存查詢資訊
            result_table = browser.find_element('id', "GridView1")
            col_names, result = [i.split(' ') for i in result_table.text.split('\n')]

            i.update({
                'number_match': result[1],
                'section_new': result[2],
                'number_new': result[3],
                'search_result': result_table.text.replace('\n', '|')
            })

            output_csv(i, result_path)

        except NoSuchElementException:
            i.update({'error_log': 'No Such Element'})
            output_csv(i, miss_path)

        except Exception as e:
            i.update({'error_log': f'{error_info} | {str(e)}'})
            output_csv(i, miss_path)

        browser.close()
        time.sleep(0.5)

def output_csv(data, path):
    pd.DataFrame([data]).to_csv(path, mode='a', index=False, header=not os.path.exists(path))

def saveJson(data, path, mode):
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
    df = pd.read_csv(args.file_path, low_memory=False).drop_duplicates()

    # 爬取座標資料
    coordinate_df = get_new_land_code(df, args.output_folder)

if __name__ == '__main__':
    main()

