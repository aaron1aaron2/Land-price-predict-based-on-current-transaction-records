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
    os.walk(args.output_folder)