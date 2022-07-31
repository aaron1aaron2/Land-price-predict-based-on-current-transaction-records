"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.07.29
Last Update: 2022.07.31
Describe: 獲取土地經緯度座標，來源 「地籍圖資網路便民服務系統」。最新資料-> https://easymap.land.moi.gov.tw/
"""

import re
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
