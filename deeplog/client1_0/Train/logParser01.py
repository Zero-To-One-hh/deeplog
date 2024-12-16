# -*- coding: utf-8 -*-
import json
import os
import re
from collections import defaultdict

# 创建 Nginx 日志的正则表达式
log_pattern = re.compile(r'''
    (?P<remote_addr>\S+) \s+            # 客户端 IP 地址
    (?P<remote_user>[-\S]*) \s+          # 用户名，允许为 "-" 或 空
    (?P<dummy1>[-\S]*) \s+               # 第二个 "-" 字段，允许为空
    \[ (?P<time_local>[^\]]+) \] \s+    # 时间戳
    "(?P<request_method>\S+) \s+        # 请求方法
    (?P<request_uri>\S+) \s+            # 请求 URI
    HTTP/\S+" \s+                       # HTTP版本
    (?P<status>\d{3}) \s+               # 响应状态码
    (?P<body_bytes_sent>\d+) \s+        # 发送给客户端的字节数
    "(?P<http_referer>[^"]*)" \s+       # 来源页面 URL
    "(?P<http_user_agent>[^"]*)" \s+    # 用户代理信息
    "(?P<http_x_forwarded_for>[^"]*)"?  # X-Forwarded-For 信息，允许为空
''', re.VERBOSE)

# 读取 JSON 文件
def load_json(filename="url_mapping.json"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    else:
        return {}

# 保存 URL 映射到 JSON 文件
def save_json(data, filename="url_mapping.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# 提取 URL 路径，去除查询参数
def extract_path(url):
    # 找到 '?' 位置并截取，保留 '?' 前面的部分
    path = url.split('?')[0]
    return path

# 解析多个 Nginx 日志文件
def parse_multiple_nginx_logs(log_folder, url_mapping):
    ip_user_agent_request_dict = defaultdict(list)
    url_to_number = url_mapping
    next_number = len(url_mapping) + 1  # 为新的 URL 分配数字

    # 获取日志文件夹中的所有日志文件
    log_files = [os.path.join(log_folder, f) for f in os.listdir(log_folder) if f.endswith('.txt')]
    print("日志文件列表:", log_files)

    # 逐个文件解析
    for filename in log_files:
        print(f"正在解析文件: {filename}")
        with open(filename, "r") as f:
            for line in f:
                # 解析每一行日志
                match = log_pattern.match(line)
                if match:
                    ip = match.group('remote_addr')
                    user_agent = match.group('http_user_agent')
                    request_uri = match.group('request_uri')

                    # 提取 URL 路径（去除查询参数）
                    path = extract_path(request_uri)

                    # 如果 URL 未在映射中，则添加它
                    if path not in url_to_number:
                        url_to_number[path] = next_number
                        next_number += 1
                        print(f"新 URL 发现并映射: {path} -> {url_to_number[path]}")

                    # 获取 URL 对应的数字
                    request_number = url_to_number[path]

                    # 键为 IP + 用户代理信息
                    key = f"{ip} {user_agent}"

                    # 将数字添加到相应的键队列中
                    ip_user_agent_request_dict[key].append(request_number)

                else:
                    print(f"行不匹配: {repr(line)}")

    # 返回解析结果和更新后的 URL 映射
    return ip_user_agent_request_dict, url_to_number

# 将解析后的队列内容按行存储到文件中
def save_requests_to_file(ip_user_agent_request_dict, output_filename="parsed_requests.txt"):
    with open(output_filename, "w") as f:
        for key, numbers in ip_user_agent_request_dict.items():
            # 将 URI 数字按空格分隔，并写入同一行
            numbers_str = ' '.join(map(str, numbers))
            f.write(f"{numbers_str}\n")

# 读取日志文件夹路径
log_folder = "trainLog"  # 日志文件夹路径

# 从 JSON 文件加载 URL 映射
url_mapping = load_json(filename="url_mapping.json")

# 读取多个日志文件并解析
ip_user_agent_request_dict, updated_url_mapping = parse_multiple_nginx_logs(log_folder=log_folder, url_mapping=url_mapping)

# 打印结果
for key, numbers in ip_user_agent_request_dict.items():
    print(f"{key}: {numbers[:5]}...")  # 打印前5条请求数字，避免过多输出

# 将结果保存到文件
save_requests_to_file(ip_user_agent_request_dict)

# 更新 URL 映射并保存
save_json(updated_url_mapping)

print("解析结果已保存到文件 'parsed_requests.txt' 中，URL 映射已更新。")
