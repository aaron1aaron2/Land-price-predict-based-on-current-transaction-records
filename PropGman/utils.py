# encoding: utf-8
"""
Author: 何彥南 (yen-nan ho)
Github: https://github.com/aaron1aaron2
Email: aaron1aaron2@gmail.com
Create Date: 2022.09.05
Last Update: 2022.09.05
Describe: 工具箱
"""
import sys
import json
import time

import yaml
from yaml.loader import SafeLoader

from pathlib import Path
from functools import wraps

def build_folder(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def saveJson(data, path):
    with open(path, 'w', encoding='utf-8') as outfile:  
        json.dump(data, outfile, indent=2, ensure_ascii=False)

def save_config(data, path):
    with open(path, 'w', encoding='utf8') as f:
        data = yaml.dump(data, f, sort_keys=False, default_flow_style=False, allow_unicode=True)

def read_config(path):
    with open(path, 'r', encoding='utf8') as f:
        data = yaml.load(f, Loader=SafeLoader)
    return data

def update_config(data, path, update_locat, update_dt):
    if type(update_locat) == str:
        data[update_locat].update(update_dt)
    elif len(update_locat) == 1:
        data[update_locat[0]].update(update_dt)
    else:
        d = data
        for key in update_locat[:-1]:
            d = d[key]
        d.update(update_dt)

    save_config(data, path)

    return data

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")

def timer(func):
    @wraps(func) # 讓屬性的 name 維持原本
    def wrap(*args, **kargs):
        t_start = time.time()
        value = func(*args, **kargs)
        t_end = time.time()
        t_count = t_end - t_start
        print(f'[timeuse] {round(t_count, 5)} seconds')
        return value
    return wrap