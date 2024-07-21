
# -*- coding: utf-8 -*-
import re

# 读取日志文件
with open('received_trust_level.log', 'r') as file:
    log_data = file.read()

# 提取 trustLevel 信息
trust_levels = re.findall(r'"trustLevel":"(Normal|Anomaly)"', log_data)

# 计算 Normal 的百分比
normal_count = trust_levels.count('Normal')
total_count = len(trust_levels)
normal_percentage = (normal_count / total_count) * 100 if total_count != 0 else 0

print(f"Normal 的百分比是: {normal_percentage:.2f}%")
