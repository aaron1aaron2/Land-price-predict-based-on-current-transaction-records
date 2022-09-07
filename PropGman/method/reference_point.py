# encoding: utf-8
"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.08.31
Last Update: 2022.08.31
Describe: 建立參考點的 function，可以放在這。
"""
import pandas as pd

from functools import partial

from PropGman.utils import timer

@timer
def UDLR(df:pd.DataFrame, distance:int, long_per_100_meter:float, lat_per_100_meter:float) -> pd.DataFrame:
    """
    上下左右固定距離(公尺)的位置:
    """
    # 產生各群的參考點 ---------------------------------------
    def get_reference(coordinate, target_meter, long_per_100_meter, lat_per_100_meter):
        lat, long = coordinate.split(',')

        lat_degree = target_meter*lat_per_100_meter/100
        long_degree = target_meter*long_per_100_meter/100

        result = {
            'group_center': coordinate,
            'refer_point1': f'{float(lat)+lat_degree},{long}',
            'refer_point2': f'{float(lat)-lat_degree},{long}',
            'refer_point3': f'{lat},{float(long)+long_degree}',
            'refer_point4': f'{lat},{float(long)-long_degree}'
        }


        return result

    result_ls = list(map(partial(
            get_reference, 
            target_meter=distance, 
            long_per_100_meter=long_per_100_meter, 
            lat_per_100_meter=lat_per_100_meter
        ), df['group_center'].unique()))

    df = df.merge(pd.DataFrame(result_ls), how='left')

    return df