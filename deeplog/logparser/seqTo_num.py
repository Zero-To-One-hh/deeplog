#再次处理序列化文件

import pandas as pd
import re

# 定义CSV文件的路径
file_path = './result/messages_sequence.csv'
output_file_path='./result/data'

# 将CSV文件加载到DataFrame中
df = pd.read_csv(file_path, header=None, skiprows=1)

# 从每行提取数字数据
numeric_data = df[0].apply(lambda x: re.findall(r'\d+', x))

# # 显示数字数据
# for i, row in enumerate(numeric_data):
#     print(f"第 {i+1} 行: {row}")
#     print(type(row))
#     break

# 将提取的数字数据写入到新的文件中
with open(output_file_path, 'w') as f:
    for i,row in enumerate(numeric_data):
        # 将数字部分用空格隔开
        row_data = ' '.join(row)
        #写入到文件中
        if len(row) > 0:
            if i < len(numeric_data) - 1:
                # 对于非最后一行，添加换行符
                f.write(row_data+ '\n')
            else:
                # 对于最后一行，不添加换行符
                f.write(row_data)