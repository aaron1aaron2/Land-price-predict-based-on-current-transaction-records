# encoding: utf-8
"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.08.05
Last Update: 2022.08.05
Describe: 獲取所有時價登入土地與目標土地經緯度之間的直線距離。
"""


# 距離上的偏誤
df_AB = df.groupby(df[group]).apply(lambda x:pd.DataFrame(list(itertools.combinations(x[id_col], 2))))
df.drop([group], axis=1, inplace=True)

#資料合併
df_AB = df_AB.rename(columns={0:'start_id',1:'end_id'})

df_start = df.rename(columns={
        '{}'.format(coor_col):'start_coordinate',
        '{}'.format(id_col):'start_id'
        })

df_AB = pd.merge(df_AB, df_start, on=['start_id'],how='left')

df_end = df_start.rename(columns={
        'start_coordinate':'end_coordinate',
        'start_id':'end_id'
    })

df_AB = pd.merge(df_AB, df_end, on=['end_id'], how='left')

#配合 geopy的資料格式
df_AB['linear_distance'] = df_AB.apply(lambda x:geodesic(x['start_coordinate'].split(','),x['end_coordinate'].split(',')).meters,axis=1)
# df_AB['linear_distance'] = df_AB.apply(lambda x:geodesic(x['start_coordinate'].split(','),x['end_coordinate'].split(',')).kilometers,axis=1)
