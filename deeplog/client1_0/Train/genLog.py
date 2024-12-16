# -*- coding: utf-8 -*-
import os
import random
from datetime import datetime, timedelta

import faker

# 初始化 faker 实例
fake = faker.Faker()

# 减少生成的 IP 和用户代理种类
sample_ips = ["192.168.0.1", "192.168.0.2", "192.168.0.3"]
sample_user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0"
]

# 模拟 Nginx 日志文件
def generate_log_entry():
    # 随机选择 IP 地址
    ip = random.choice(sample_ips)

    # 随机生成请求的 URI
    uri = f"/api/v1/{random.choice(['resource', 'login', 'data', 'user', 'status'])}"

    # 随机生成 HTTP 状态码
    status = random.choice([200, 301, 400, 401, 404, 500])

    # 随机生成响应体大小
    body_size = random.randint(100, 5000)

    # 随机选择 User-Agent
    user_agent = random.choice(sample_user_agents)

    # 随机生成 Referer
    referer = f"https://{fake.domain_name()}"

    # 时间戳（模拟近几天的时间）
    timestamp = datetime.now() - timedelta(days=random.randint(0, 30))
    timestamp_str = timestamp.strftime('%d/%b/%Y:%H:%M:%S +0000')

    # 生成完整的 Nginx 日志条目
    log_entry = f'{ip} - - [{timestamp_str}] "GET {uri} HTTP/1.1" {status} {body_size} "{referer}" "{user_agent}" "{fake.ipv4()}"\n'

    return log_entry


# 生成多个日志文件，每个文件包含指定数量的日志条目
def generate_multiple_log_files(directory="trainLog", num_files=5, num_entries=5000):
    # 创建文件夹，如果不存在
    if not os.path.exists(directory):
        os.makedirs(directory)

    # 生成多个日志文件
    for i in range(num_files):
        # 使用当前日期和文件编号命名文件
        date_str = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        filename = os.path.join(directory, f"nginx_log_{date_str}.txt")

        with open(filename, "w") as f:
            for _ in range(num_entries):
                log_entry = generate_log_entry()
                f.write(log_entry)
        print(f"日志文件生成完毕：{filename}, 包含 {num_entries} 条日志。")


# 生成多个模拟日志文件（每个文件5000条，共5个文件）
generate_multiple_log_files(num_files=5, num_entries=5000)
