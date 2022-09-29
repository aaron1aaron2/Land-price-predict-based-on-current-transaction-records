# encoding: utf-8
"""
Author: yen-nan ho
Contact: aaron1aaron2@gmail.com
GitHub: https://github.com/aaron1aaron2
Create Date: 2022.09.29
Last Update: 2022.09.29
"""
import os
import json
import glob
import argparse
import pandas as pd

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--target_folder', type=str, default='output/test-hyper-parameter(amount)')
    parser.add_argument('--output', type=str, default=None)

    args = parser.parse_args()

    return args

if __name__ == '__main__':
    args = get_args()

    eval_ls = glob.glob(os.path.join(args.target_folder, '**', '*evaluation.json'), recursive=True)
    eval_result_ls = [json.load(open(i)) for i in eval_ls]

    result = pd.DataFrame(eval_result_ls)

    result = pd.concat([result, pd.DataFrame(eval_ls, columns=['file'])], axis=1)

    tmp = result['file'].str.replace(args.target_folder, '', regex=False)
    tmp = tmp.str.extract('(?P<tmp>.+).evaluation.json')['tmp'].str.strip('\\').str.split('\\', expand=True)

    tmp.columns = [f'layer{i+1}' for i in tmp.columns]

    result = tmp.join(result)

    if args.output:
        result.to_csv(args.output, index=False)
    else:
        result.to_csv(os.path.join(args.target_folder, 'result.csv'), index=False)
