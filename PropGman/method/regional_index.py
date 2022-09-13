# encoding: utf-8
"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.09.13
Last Update: 2022.09.13
Describe: 計算區域性指標
"""
import os
import tqdm
import pandas as pd
from PropGman.utils import timer


class RegionalIndex:
    def __init__(self, method:str, start_date:str, end_date:str, dist_threshold:int):
        super(RegionalIndex, self).__init__()

        self.method = method
        self.start_date = start_date
        self.end_date = end_date
        self.dist_threshold = dist_threshold
