# import torch
# from collections import Counter
#
#
# class Predicter():
#     def __init__(self, model, options):
#         self.device = options['device']
#         self.model = model
#         self.model_path = options['model_path']
#         self.window_size = options['window_size']
#         self.num_candidates = options['num_candidates']
#         self.num_classes = options['num_classes']
#         self.input_size = options['input_size']
#         self.test_data = options['test_data']
#
#         # Load the model
#         self.model.load_state_dict(torch.load(self.model_path)['state_dict'])
#         self.model.to(self.device)
#         self.model.eval()
#
#     def process_data(self, data):
#         window_size = self.window_size
#         hdfs = {}
#         for ln in data:
#             ln = list(map(lambda n: n - 1, map(int, ln.strip().split())))
#             ln = ln + [-1] * (window_size + 1 - len(ln))
#             hdfs[tuple(ln)] = hdfs.get(tuple(ln), 0) + 1
#         return hdfs
#
#     def predict(self):
#         test_data_processed = self.process_data(self.test_data)
#
#         for line in test_data_processed.keys():
#             for i in range(len(line) - self.window_size):
#                 seq0 = line[i:i + self.window_size]
#                 label = line[i + self.window_size]
#                 seq1 = [0] * self.num_classes
#                 log_counter = Counter(seq0)
#                 for key in log_counter:
#                     seq1[key] = log_counter[key]
#
#                 seq0 = torch.tensor(seq0, dtype=torch.float).view(
#                     -1, self.window_size, self.input_size).to(self.device)
#                 seq1 = torch.tensor(seq1, dtype=torch.float).view(
#                     -1, self.num_classes, self.input_size).to(self.device)
#                 label = torch.tensor(label).view(-1).to(self.device)
#                 output = self.model(features=[seq0, seq1], device=self.device)
#                 predicted = torch.argsort(output, 1)[0][-self.num_candidates:]
#                 if label not in predicted:
#                     return "异常"
#         return "正常"
