#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import torch
from collections import Counter
from logdeep.models.lstm import deeplog
from logdeep.tools.utils import seed_everything

sys.path.append('../')

# Config Parameters
options = dict()
options['window_size'] = 10
options['device'] = "cpu"

# Model Parameters
options['input_size'] = 1
options['hidden_size'] = 64
options['num_layers'] = 2
options['num_classes'] = 676

# Predict Parameters
options['model_path'] = "../deeplog2024_06_15/deeplog_bestloss.pth"
options['num_candidates'] = 9

# Initialize seed for reproducibility
seed_everything(seed=1234)

# Initialize model globally
Model = deeplog(input_size=options['input_size'],
                hidden_size=options['hidden_size'],
                num_layers=options['num_layers'],
                num_keys=options['num_classes'])
Model.load_state_dict(torch.load(options['model_path'])['state_dict'])
Model.to(options['device'])
Model.eval()

def predict_single_log(log):
    window_size = options['window_size']
    seq = list(map(lambda n: n - 1, map(int, log.strip().split())))
    for i in range(len(seq) - window_size):
        seq0 = seq[i:i + window_size]
        label = seq[i + window_size]
        seq1 = [0] * options['num_classes']
        log_counter = Counter(seq0)
        for key in log_counter:
            seq1[key] = log_counter[key]

        seq0 = torch.tensor(seq0, dtype=torch.float).view(-1, window_size, options['input_size']).to(options['device'])
        seq1 = torch.tensor(seq1, dtype=torch.float).view(-1, options['num_classes'], options['input_size']).to(options['device'])
        label = torch.tensor(label).view(-1).to(options['device'])
        output = Model(features=[seq0, seq1], device=options['device'])
        predicted = torch.argsort(output, 1)[0][-options['num_candidates']:]
        if label not in predicted:
            return "Anomaly"
    return "Normal"

if __name__ == "__main__":
    # Example usage for prediction
    log_example = "1 2 3 4 5 6 7 8 9 10 11"  # Replace this with actual log input
    result = predict_single_log(log_example)
    print(result)
