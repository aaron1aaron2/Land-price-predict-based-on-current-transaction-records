# encoding: utf-8
"""
Author: yen-nan ho
Contact: aaron1aaron2@gmail.com
GitHub: https://github.com/aaron1aaron2
Create Date: 2022.09.29
Last Update: 2022.09.29
"""
import torch
import argparse
import pandas as pd

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='output/test-hyper-parameter(amount)')
    parser.add_argument('--data', type=str, default='output/test-hyper-parameter(amount)')


    args = parser.parse_args()

    return args

if __name__ == '__main__':
    args = get_args()
    model = torch.load(args.model)