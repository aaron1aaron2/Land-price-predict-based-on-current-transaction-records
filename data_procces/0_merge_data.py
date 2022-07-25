"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.07.18
Last Update: 2022.07.23
Describe: 
"""
import os
import zipfile
import glob
import pandas as pd

from tqdm import tqdm

doc_fils = ['manifest.csv', 'build.ttt', 'schema-build.csv', 'schema-land.csv', 'schema-main.csv', 'schema-park.csv']

output = 'data/merge_data'
path = 'data/rawdata/歷年時價登入'

os.makedirs(output, exist_ok=True)
zip_fils = sorted(glob.glob(os.path.join(path, '*.zip')))
for zfile in tqdm(zip_fils):
    f_in_zfile = zipfile.ZipFile(zfile, 'r')
    file_ls = list(filter(lambda x: x not in doc_fils, f_in_zfile.namelist()))

    # 只取桃園(h)
    file_ls = [i for i in file_ls if i.find('h_')!=-1]

    # fileinfo_df = pd.read_csv(zip_fils.open('manifest.csv'), usecols=['name', 'description'])
    # file_arr = fileinfo_df[fileinfo_df.name.isin(file_ls)].values

    for file_name  in file_ls :
        df = pd.read_csv(f_in_zfile.open(file_name), low_memory=False)
        df.drop(0, inplace=True)

        tmp = df.columns.to_list()
        df['file'] = zfile
        df['year_s'] = df['file'].str.extract('(\d+-\d)\.zip')

        df = df[['year_s'] + tmp]

        output_path = os.path.join(output, file_name)
        df.to_csv(output_path, mode='a', index=False, header=not os.path.exists(output_path))
