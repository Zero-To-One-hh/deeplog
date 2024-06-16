import os
import random
from random import shuffle

import pandas as pd
from pandas.core.frame import DataFrame


# 将数据写入到文件中
def write_data_to_file(data, file_path):
    with open(file_path, 'w') as f:
        for i, row in enumerate(data):
            if i < len(data) - 1:
                f.write(row + '\n')
            else:
                f.write(row)


# 读取数据
def data_read(filepath):
    fp = open(filepath, "r")
    datas = []  # 存储处理后的数据
    lines = fp.readlines()  # 读取整个文件数据
    i = 0  # 为一行数据
    for line in lines:
        row = line.strip()
        # row = line.strip('\n').split(' ')  # 去除两头的换行符，按空格分割
        datas.append(row)
        i = i + 1
    fp.close()
    return datas

train_file_path = "./train"
valid_file_path = "./valid"
test_file_path = "./test"

data=data_read("./data")

print("数据长度：",len(data))
max_len = 0
for i in range(len(data)):
    leng = len(data[i])
    # if leng>200:
    # print(i)
    # print(normal_all[i])
    max_len = max([max_len, leng])
print("最长数据行:",max_len)
#
#
random.seed(42)
#
shuffle(data)
#
train_data = data[:int(len(data)*0.7)]
valid_data = data[int(len(data)*0.7):int(len(data)*0.8)]
test_data = data[int(len(data)*0.8):]

write_data_to_file(train_data, train_file_path)
write_data_to_file(valid_data, valid_file_path)
write_data_to_file(test_data, test_file_path)

print("train_data:",len(train_data))
print("valid_data:",len(valid_data))
print("test_data:",len(test_data))
