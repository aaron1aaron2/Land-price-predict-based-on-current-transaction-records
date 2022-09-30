# encoding: utf-8
"""
Author: yen-nan ho
Contact: aaron1aaron2@gmail.com
GitHub: https://github.com/aaron1aaron2
Create Date: 2022.09.29
Last Update: 2022.09.29
"""
import json
import torch
import argparse
import pandas as pd
import numpy as np

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='output/basic/model.pkl')
    parser.add_argument('--config', type=str, default='output/basic/configures.json')
    parser.add_argument('--data', type=str, default='data/example.csv')
    parser.add_argument('--target', type=str, default='2018-2') # 答案是: 72274.79166666667

    args = parser.parse_args()

    return args

if __name__ == '__main__':
    args = get_args()

    config = json.load(open(args.config))
    mean, std = config['mean'], config['std']

    DEVICE = config['device']

    model = torch.load(args.model)

    # input
    data = pd.read_csv(args.data)
    X = np.array(data[['group_center', 'refer_point1', 'refer_point2', 'refer_point3', 'refer_point4']].values, dtype='float32')
    X = torch.from_numpy(X)
    X = torch.unsqueeze(X , 0) # [資料筆數, his_筆數, 參考+目標點的數量]
    X = torch.FloatTensor(X)

    # TE 
    time = pd.DatetimeIndex(data.year.astype(str) + '-' + data.month.astype(str))
    time = time.append(pd.DatetimeIndex([args.target])) # 加入預測的時間點

    dayofweek = torch.reshape(torch.tensor(time.weekday), (-1, 1))
    timeofday = (time.hour * 3600 + time.minute * 60 + time.second) \
                // 1440*60
                
    timeofday = torch.reshape(torch.tensor(timeofday), (-1, 1))
    TE = torch.cat((dayofweek, timeofday), -1)
    TE = torch.unsqueeze(TE , 0) # (num_sample, num_his + num_pred, 2)
    X, TE = X.to(DEVICE), TE.to(DEVICE)

    with torch.no_grad():
        pred = model(X, TE)

        pred = pred*std + mean

        pred = pred.detach().cpu().clone()

    print('[Our predict]\n'f'{args.target}: {float(pred)}')

