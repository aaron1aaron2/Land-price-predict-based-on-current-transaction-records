"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.07.31
Last Update: 2022.07.31
Describe: 獲取土地經緯度座標，來源 「地籍圖資網路便民服務系統」。最新資料-> https://easymap.land.moi.gov.tw/
            本 script 為 2_get_coordinate.py 的替代方案，他有最新資料，但是據觀察大部分資料 2_get_coordinate.py 就可以爬取到。
            所以本方案先保留。
-----------------------------------
Issue: 
    1. [已解決] 擷取過程中回傳的地圖中心(經緯)
        a. 紀錄 network traffic: https://stackoverflow.com/questions/52633697/selenium-python-how-to-capture-network-traffics-response
        b. cookies 資訊: https://stackoverflow.com/questions/12737740/python-requests-and-persistent-sessions
        c. 使用 seleniumwire: https://www.linkedin.com/pulse/how-capture-http-requests-using-selenium-ash-sheng/
            - [未解決] 使用 seleniumwire 的 https 憑證問題
                a. 手動加入憑證: https://github.com/wkeeling/selenium-wire/issues/120
            - [未解決] 使用 seleniumwire 的載入速度問題 
        d. (current use) 直接用在 console 執行 move_lonlat 回傳當前經緯
            https://stackoverflow.com/questions/5585343/getting-the-return-value-of-javascript-code-in-selenium
"""

import re
import os
import json
import time
import argparse
import pandas as pd
import requests

from tqdm import tqdm

from selenium import webdriver
# from seleniumwire import webdriver

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
    parser.add_argument('--output_folder', type=str, default='data/procces/3_get_coordinate_newest')

    parser.add_argument('--special_section_dict', type=str, default='data/special_section_dict.txt')

    args = parser.parse_args()

    return args

def get_new_land_code(df, output, section_dt):
    result_path = os.path.join(output, 'crawler_result.csv')
    miss_path = os.path.join(output, 'crawler_miss.csv')

    print(f'Total tasks: {df.shape[0]}')
    # 爬蟲進度恢復
    if os.path.exists(result_path) | os.path.exists(miss_path):
        tmp = df['county'] + df['district'] + df['section'] + df['number']

        progress_df = pd.read_csv(result_path) if os.path.exists(result_path) else pd.DataFrame()
        miss_df = pd.read_csv(miss_path) if os.path.exists(miss_path) else pd.DataFrame()

        all_df = pd.concat([progress_df, miss_df])

        df = df[~tmp.isin(all_df['county'] + all_df['district'] + all_df['section'] + all_df['number'])]

        del tmp; del progress_df; del miss_df

        print(f'Current progress: {df.shape[0]}\n')

    land_addr_dt_ls = df.to_dict(orient="records")

    for i in tqdm(land_addr_dt_ls):
        main_ct = 0
        while main_ct < 3:
            error_info = ''
            try:
                browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=get_chrome_options())
                
                browser.implicitly_wait(10) # 隱式等待
                browser.get("https://easymap.land.moi.gov.tw/")
                
                # home to map
                entrance_btn = browser.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[1]/div[2]/a[1]")
                entrance_btn.send_keys(Keys.ENTER)
                time.sleep(0.1)

                # # 選擇搜尋服務類型 (使用網站預設)
                # type_select = Select(browser.find_element('name', 'landType'))
                # type_select.select_by_visible_text('以地號查詢')

                # 選擇縣市 city
                city_tar = browser.find_element('name', 'select_city')
                city_options = city_tar.find_elements(By.TAG_NAME, 'option')
                city = [ls_txt.text for ls_txt in city_options if ls_txt.text.find(i['county']) != -1]

                if len(city) == 0:
                    error_info = '找不到縣市'

                city_select = Select(city_tar)
                city_select.select_by_visible_text(city[0])
                time.sleep(0.2)

                # 選擇區 town | 重複 50 次嘗試，等待列表載入
                town = []; ct = 0
                while len(town) == 0:
                    town_tar = browser.find_element('name', 'select_town')
                    town_options = town_tar.find_elements(By.TAG_NAME, 'option')
                    town = [ls_txt.text for ls_txt in town_options if ls_txt.text.find(i['district']) != -1] 

                    time.sleep(0.2)

                    ct += 1
                    if ct > 50:
                        error_info = '找不到區'
                        break

                town_select = Select(town_tar)
                town_select.select_by_visible_text(town[0])
                time.sleep(0.2)

                # 選擇段 section | 重複 50 次嘗試，等待列表載入
                section = []; ct = 0
                while len(section) == 0:
                    section_tar = browser.find_element('name', 'select_sect')
                    section_options = [ls_txt.text for ls_txt in section_tar.find_elements(By.TAG_NAME, 'option')]
                    section_options_val = [ls_txt.get_attribute('value') for ls_txt in section_tar.find_elements(By.TAG_NAME, 'option')]

                    for pat, tar in section_dt.items():
                        section_options = [re.sub(pat, tar, ls_txt) for ls_txt in section_options]

                    section = [val for ls_txt, val in zip(section_options, section_options_val) if ls_txt.find(i['section']) != -1] 

                    time.sleep(0.2)

                    # 當已載入段但是查詢不到，直接視作 miss，跳出 retry
                    if (len(section_options) > 2) & (len(section) == 0):
                        error_info = '找不到段'
                        main_ct = 5
                        raise 

                    ct += 1
                    if ct > 50:
                        error_info = '找不到段'
                        break

                section_select = Select(section_tar)
                section_select.select_by_value(section[0])
                time.sleep(0.2)

                # 輸入舊地號
                ct = 0
                while ct < 10:
                    time.sleep(0.2)
                    landcode_tar = browser.find_element('name', 'landno')
                    landcode_tar.send_keys(i['number'])
                    if len(landcode_tar.get_attribute('value')) != 0:
                        break
                    ct += 1

                # 送出
                summit_button = browser.find_element('id', 'land_button')
                summit_button.send_keys(Keys.ENTER)
                time.sleep(0.5)

                # 查詢結果 table
                result_table = browser.find_element('id', "dlg_search_result")
                result_text = result_table.text

                # 直接取當前地圖中心經緯度
                browser.find_element('id', 'OpenLayers.Layer.Vector_42_vroot').click() # 點一下地圖
                coor_dt = browser.execute_script('return move_lonlat')

                # # 使用當前 session request，獲取中心點經緯度 (回應太慢，不穩定)
                # s = get_request_session(browser.get_cookies())
                # token_rp = s.post('https://easymap.land.moi.gov.tw/pages/setToken.jsp')
                # token = re.search('name="token" value="(.+)" />', token_rp.text)[1]

                # s = get_request_session(browser.get_cookies())
                # info = {
                #     'office': 'HE',
                #     'sectNo': section_code,
                #     'landNo': i['number'],
                #     'qryResult': '',
                #     'struts.token.name': 'token',
                #     'token': token
                # }
                # coordinate_rp = requests.post('https://easymap.land.moi.gov.tw/Map_json_getMapCenter', info)

                # 儲存查詢資訊
                if result_text.find('新地段 新地號') == -1:
                    i.update({'error_log': result_text})
                    output_csv(i, miss_path)
                else:
                    result = [i.split(' ', 1) for i in result_text.split('\n')]
                    result = [i for i in result if len(i)==2]
                    result = {i:v for i,v in result}
                    result['lat'] = coor_dt["lat"] if 'lat' in coor_dt else ''
                    result['long'] = coor_dt["lon"] if 'lon' in coor_dt else ''


                    i.update(result)

                    output_csv(i, result_path)

            except NoSuchElementException:
                exit()
                if main_ct >= 2:
                    i.update({'error_log': 'No Such Element'})
                    output_csv(i, miss_path)

            except Exception as e:
                if str(e).find('查無') != -1:
                    pat_match = re.search('(Alert Text: .+)', str(e))
                    alert_txt = pat_match[1].strip() if pat_match != None else str(e)
                    i.update({'error_log': f'{error_info} | {alert_txt}'})
                    output_csv(i, miss_path)
                    break
                if main_ct >= 2:
                    i.update({'error_log': f'{error_info} | {str(e)}'})
                    output_csv(i, miss_path)

            main_ct += 1
            browser.close()

def get_request_session(cookies):
    s = requests.Session()
    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'], path=cookie['path'])
    return s

def get_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--headless") # 無視窗
    chrome_options.add_argument("--incognito") # 無痕
    chrome_options.add_argument("--disable-software-rasterizer") # 無痕
    chrome_options.add_argument('--ignore-certificate-errors') # 無視憑證
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging']) # 忽略 log
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36")
    return chrome_options

def process_browser_log_entry(entry):
    response = json.loads(entry['message'])['message']
    return response

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

def read_dt(path):
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
