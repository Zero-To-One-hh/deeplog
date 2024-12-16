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



# 读取JSON文件
def load_json(filename="service_mapping.json"):
    with open(filename, "r") as f:
        return json.load(f)


# 解析多个 Nginx 日志文件
def parse_multiple_nginx_logs(log_folder, service_mapping=None):
    ip_user_agent_request_dict = defaultdict(list)

    # 创建 URL 到服务的反向映射字典
    url_to_service = {}
    for service, urls in service_mapping.items():
        for url in urls:
            url_to_service[url] = service

    # 获取日志文件夹中的所有日志文件
    log_files = [os.path.join(log_folder, f) for f in os.listdir(log_folder) if f.endswith('.txt')]
    print(log_files)
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

                    # 根据 URL 获取服务
                    service = url_to_service.get(request_uri, None)  # 如果 URL 没有匹配到，返回 None

                    if service:
                        # 使用 URL 对应的数字
                        request_number = url_to_number.get(request_uri, None)  # 获取对应的数字

                        if request_number is not None:
                            # 键为 IP + 服务 + 用户代理信息
                            key = f"{ip} {service} {user_agent}"

                            # 将数字添加到相应的键队列中
                            ip_user_agent_request_dict[key].append(request_number)
                        else:
                            print(f"URL not found in number mapping: {request_uri}")
                    else:
                        print(f"URL not found in service mapping: {request_uri}")
                else:
                    print(f"Line does not match: {repr(line)}")

    return ip_user_agent_request_dict
# 将解析后的队列内容按行存储到文件中
def save_requests_to_file(ip_user_agent_request_dict, output_filename="parsed_requests.txt"):
    with open(output_filename, "w") as f:
        for key, numbers in ip_user_agent_request_dict.items():
            # 将 URI 数字按空格分隔，并写入同一行
            numbers_str = ' '.join(map(str, numbers))
            f.write(f"{numbers_str}\n")

# 从 JSON 文件加载服务映射
service_mapping = load_json(filename="service_mapping.json")

# 从 JSON 文件加载URL映射
url_to_number = load_json(filename="url_mapping.json")

# 读取日志文件夹路径
log_folder = "trainLog"  # 日志文件夹路径

# 读取多个日志文件并解析
ip_service_user_agent_request_dict = parse_multiple_nginx_logs(log_folder=log_folder, service_mapping=service_mapping)
# 打印结果
for key, numbers in ip_service_user_agent_request_dict.items():
    print(f"{key}: {numbers[:5]}...") # 打印前5条请求数字，避免过多输出

# 将结果保存到文件
save_requests_to_file(ip_service_user_agent_request_dict)

print("解析结果已保存到文件 'parsed_requests.txt' 中。")





