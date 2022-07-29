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
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from webdriver_manager.chrome import ChromeDriverManager

from IPython import embed

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--file_path', type=str, default='data/procces/2_coordinate_data/crawler_miss.csv')
    parser.add_argument('--output_folder', type=str, default='data/procces/3_land_code_transform')

    args = parser.parse_args()

    return args

def get_new_land_code(df):
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # 無視窗
    chrome_options.add_argument("--incognito") # 無痕
    chrome_options.add_argument("--disable-software-rasterizer") # 無痕
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging']) # 忽略 log
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36")

    land_addr_dt_ls = df.to_dict(orient="records")

    for i in land_addr_dt_ls:
        try:
            embed()
            exit()
            browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            
            browser.implicitly_wait(10) # 隱式等待

            browser.get("https://www.land.tycg.gov.tw/chaspx/SQry4.aspx/14")
            count = 1                  
            while count < 3:
                # 進入到互動 iframe
                browser.switch_to.frame(browser.find_element(By.XPATH, '//*[@title="新舊地建號查詢"]'))

                # 選擇搜尋服務類型
                type_select = Select(browser.find_element('name', 'searchtype'))
                type_select.select_by_visible_text('舊地號查新地號')
                # select.select_by_value('2')
                
                city_select = Select(browser.find_element('name', 'xcity'))
                city_select.select_by_visible_text('桃園區') #桃園區(01)
                
                time.sleep(0.5)
                htmlstring = browser.page_source
                soup_map = BeautifulSoup(htmlstring, 'lxml')

                count+=1

            soup_map_clear = soup_map.find(class_="section-popular-times-container")

        except:
            print('error')
        
        browser.close()

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
    coordinate_df = get_new_land_code(df)

if __name__ == '__main__':
    main()

