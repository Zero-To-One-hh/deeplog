#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys

sys.path.append('../')

from logdeep.models.lstm import deeplog, loganomaly, robustlog
from logdeep.tools.predict import Predicter
from logdeep.tools.train import Trainer
from logdeep.tools.utils import *

# Config Parameters

options = dict()
options['train_data'] = './data/Kylin/train'
options['val_data'] = './data/Kylin/valid'
options['test_data'] = './data/Kylin/test'
options['data_dir'] = './data/'
options['window_size'] = 10
options['device'] = "cpu"

# Smaple
options['sample'] = "sliding_window"
options['window_size'] = 10  # if fix_window

# Features
options['sequentials'] = True
options['quantitatives'] = False
options['semantics'] = False
options['feature_num'] = sum(
    [options['sequentials'], options['quantitatives'], options['semantics']])

# Model
options['input_size'] = 1
options['hidden_size'] = 64
options['num_layers'] = 2
options['num_classes'] = 676

# Train
options['batch_size'] = 2048
options['accumulation_step'] = 1

options['optimizer'] = 'adam'
options['lr'] = 0.001
options['max_epoch'] = 370
options['lr_step'] = (300, 350)
options['lr_decay_ratio'] = 0.1

import time

# str=time.strftime('%Y_%m_%d', time.localtime())
str = "2024_06_15"

options['resume_path'] = None
options['model_name'] = "deeplog"
options['save_dir'] = "./result/deeplog" + str + "/"

# Predict
options['model_path'] = "./result/deeplog" + str + "/deeplog_bestloss.pth"
options['num_candidates'] = 9

seed_everything(seed=1234)


def train():
    Model = deeplog(input_size=options['input_size'],
                    hidden_size=options['hidden_size'],
                    num_layers=options['num_layers'],
                    num_keys=options['num_classes'])
    trainer = Trainer(Model, options)
    trainer.start_train()


def predict():
    Model = deeplog(input_size=options['input_size'],
                    hidden_size=options['hidden_size'],
                    num_layers=options['num_layers'],
                    num_keys=options['num_classes'])
    predicter = Predicter(Model, options)
    predicter.predict_unsupervised()


# 未参考语义信息和频率信息
# 训练时使用的全是正常数据
# 预测时使用的既有正常也有异常数据
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['train', 'test'])
    args = parser.parse_args()
    if args.mode == 'train':
        train()
    else:
        predict()
