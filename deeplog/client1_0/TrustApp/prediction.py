# -*- coding: utf-8 -*-
from collections import Counter

import torch

from config import config
from logger import logger
# 假设模型位于 'models' 目录下的 'lstm.py' 文件中
from models import deeplog


def load_model():
    try:
        Model = deeplog(input_size=config['input_size'],
                        hidden_size=config['hidden_size'],
                        num_layers=config['num_layers'],
                        num_keys=config['num_classes'])
        Model.load_state_dict(torch.load(config['model_path'])['state_dict'])
        Model.to(config['device'])
        Model.eval()
        logger.info("模型加载成功")
        return Model
    except Exception as e:
        logger.error(f"加载模型时出错: {e}")
        raise

Model = load_model()

def predict_single_log(log):
    window_size = config['window_size']
    if len(log) != window_size + 1:
        raise ValueError(f"输入日志长度必须为 {window_size + 1}.")

    seq = list(map(lambda n: n - 1, log))
    seq0 = seq[:window_size]
    label = seq[window_size]
    seq1 = [0] * config['num_classes']
    log_counter = Counter(seq0)
    for key in log_counter:
        seq1[key] = log_counter[key]

    seq0 = torch.tensor(seq0, dtype=torch.float).view(-1, window_size, config['input_size']).to(config['device'])
    seq1 = torch.tensor(seq1, dtype=torch.float).view(-1, config['num_classes'], config['input_size']).to(config['device'])
    label = torch.tensor(label).view(-1).to(config['device'])
    output = Model(features=[seq0, seq1], device=config['device'])
    predicted = torch.argsort(output, 1)[0][-config['num_candidates']:]
    if label not in predicted:
        return "Anomaly"
    return "Normal"
