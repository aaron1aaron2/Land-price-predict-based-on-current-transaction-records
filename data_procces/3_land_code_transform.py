"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.07.29
Last Update: 2022.08.02
Describe: 將未爬取到的舊地號轉新地號，來源「桃園地政資訊服務網」 -> https://www.land.tycg.gov.tw/chaspx/SQry4.aspx/14
-----------------------------------
Issue: 
    1. [已解決] invalid session id -> 當 selenium session 未正確關閉產生的
        a. quit() 與 close(): https://stackoverflow.com/questions/56483403/selenium-common-exceptions-webdriverexception-message-invalid-session-id-using
"""

import re
import os
import json
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

    parser.add_argument('--special_section_dict', type=str, default='data/special_section_dict.txt')

    args = parser.parse_args()

    return args

def get_new_land_code(df:pd.DataFrame, output:str, section_dt:dict) -> None:
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

    land_addr_dt_ls = df.to_dict(orient="records")

    for i in tqdm(land_addr_dt_ls):
        error_info = ''
        try:
            browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=get_chrome_options())
            
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

            city_select = Select(city_tar)
            city_select.select_by_visible_text(city[0])
                
            # 選擇段
            section_tar = browser.find_element('name', 'xarea')
            section_options = [ls_txt.text for ls_txt in section_tar.find_elements(By.TAG_NAME, 'option')]

            for pat, tar in section_dt.items():
                section_options = [re.sub(pat, tar, ls_txt) for ls_txt in section_options]

            section = [ls_txt for ls_txt in section_options if ls_txt.find(i['section']) != -1] # 只取前兩字配對(市與區問題)

            if len(section) == 0:
                error_info = '找不到段'

            section_select = Select(section_tar)
            section_select.select_by_value(re.search("\((\d+)\)", section[0])[1])

            # 輸入舊地號
            landcode_tar = browser.find_element('name', 'xno')
            landcode_tar.send_keys(i['number'])

            # 送出
            summit_button = browser.find_element('id', 'btnSearch1')
            summit_button.send_keys(Keys.ENTER)

            # 儲存查詢資訊
            result_table = browser.find_element('id', "GridView1")
            result_text = result_table.text

            if result_text.find('新地段 新地號') == -1:
                i.update({'error_log': result_text})
                output_csv(i, miss_path)
            else:
                _, result = [i.split(' ') for i in result_text.split('\n')]
                i.update({
                    'district_match': city[0],
                    'section_match': section[0],
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

        # session 偽證昂關閉時解決方法，當 close 無法正確關閉時使用 quit。
        try:
            browser.close() # 只關當前 tab、window，會有 session 衝突問題
        except:
            browser.quit() # 全部關閉，速度較慢。 
        
def get_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--headless") # 無視窗
    chrome_options.add_argument("--incognito") # 無痕
    chrome_options.add_argument("--disable-software-rasterizer") # 無痕
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging']) # 忽略 log
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36")

    return chrome_options

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

def read_dt(path:str) -> dict:
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()

    lines = [i.split(' ') for i in lines]
    dt = {i[0]:i[1].strip() for i in lines}

    return dt

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
    
    assert os.path.exists(args.special_section_dict), f"section dict could not be found at {args.special_section_dict}"
    section_dt = read_dt(args.special_section_dict)

    # 爬取座標資料
    get_new_land_code(df, args.output_folder, section_dt)

if __name__ == '__main__':
    main()
