"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.08.16
Last Update: 2022.08.17
Describe: 觀察範圍內，有效的交易點
"""
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from geopy.distance import geodesic

output_folder = 'data/data_procces/9_effective_range_select'
os.makedirs(output_folder, exist_ok=True)

df_tar = pd.read_csv('data/method_procces/0_target_land_group/group_list.csv')
df_tran = pd.read_csv('data/data_procces/8_time_range_select/transaction_all.csv')
df_tran = df_tran[df_tran['使用分區']=='住']

tran_land = df_tran[['long', 'lat', 'land_id']].drop_duplicates()
tran_land['tran_land_center'] = tran_land['lat'].astype(str) + ',' +  tran_land['long'].astype(str)
tran_land.drop(['lat', 'long'], axis=1, inplace=True)
tran_land['land_id'] = tran_land['land_id'].astype(int)

two_point_df = pd.DataFrame()
for gp_id in df_tar['group_id'].to_list():
    tmp = tran_land.copy()
    tmp['group_id'] = gp_id
    two_point_df = pd.concat([two_point_df, tmp])

two_point_df = two_point_df.merge(df_tar, how='left')

# 測試 ---------------------
# def get_distance(x):
#     try:
#         return geodesic(x['tran_land_center'].split(','),x['group_center'].split(',')).meters
#     except:
#         return ''

# tmp = two_point_df.head(60000).apply(lambda x: get_distance(x), axis=1) # 16.2 s/60000 筆
# --------------------------


def get_distance(x):
    """部分經緯度有問題"""
    try:
        return geodesic(x[0].split(','),x[1].split(',')).meters
    except:
        return ''

two_point_df['linear_distance']  = list(map(get_distance, two_point_df[['tran_land_center', 'group_center']].values)) #  11.9 s/60000 筆 

# 移除經緯度有問題的部分
two_point_df = two_point_df[~(two_point_df['linear_distance']=='')]

two_point_tran_df = two_point_df.merge(df_tran)


for d in [1000, 2000, 3000, 4000, 5000]:
    df = two_point_tran_df.copy()
    df = df[df['linear_distance'] <= d]

    gb_ct = df.groupby(['year', 'month', 'group_id']).count()['day'].reset_index()

    tmp = gb_ct[["year", "month", "day"]].astype(int)
    tmp['day'] = 1

    gb_ct['year-month'] = pd.to_datetime(tmp)
    gb_ct.rename(columns={'day': 'count'}, inplace=True)

    gb_ct_sort = gb_ct.pivot(index='year-month', columns='group_id', values='count')
    gb_ct_sort.to_csv(
        os.path.join(output_folder, f'one_month_distance({d}).csv')
    )
    gb_ct_sort.describe().round(2).to_csv(
        os.path.join(output_folder, f'one_month_distance({d})_describe.csv')
    )

    # 畫圖
    # for id_ls in [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11]]:
    #     plt.clf()
    #     plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
    #     sns.lineplot(x='year-month', y='count', hue='group_id', data=gb_ct[gb_ct['group_id'].isin(id_ls)], palette='Set2')
    #     plt.tight_layout()
    #     # plt.show()
    #     plt.savefig(os.path.join(output_folder, f"transaction_plot_year-month_dist{d}_id{'.'.join([str(i) for i in id_ls])}.png"))
