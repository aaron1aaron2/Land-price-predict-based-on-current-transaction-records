# encoding: utf-8
"""
Author: yen-nan ho
Contact: aaron1aaron2@gmail.com
GitHub: https://github.com/aaron1aaron2
Create Date: 2022.09.26
Last Update: 2022.09.26
"""
import os
import glob
import argparse
import pandas as pd

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_folder', type=str, default='output/test-hyper-parameter(amount)',
                        help='a time step is mins')


    args = parser.parse_args()

    return args

if __name__ == '__main__':
    args = get_args()
    from IPython import embed
    embed()
    exit()
    eval_ls = glob.glob(os.path.join(args.output_folder, '**', '*evaluation.json'), recursive=True)
    eval_ls