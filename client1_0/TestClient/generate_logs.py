# -*- coding: utf-8 -*-
import json
import random
import datetime
import time
import requests
from pydantic import BaseModel


def generate_ipv4():
    """Generate random IPv4 address"""
    return '.'.join(str(random.randint(0, 255)) for _ in range(4))


def generate_request(url):
    """Generate a random HTTP request line using a specific URL"""
    methods = ["GET", "POST", "PUT", "DELETE"]
    protocol = "HTTP/1.1"
    method = random.choice(methods)
    return f"{method} {url} {protocol}"


def generate_user_agent():
    """Generate random user-agent"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    ]
    return random.choice(user_agents)


def generate_timestamp():
    """Generate timestamp in nginx log format"""
    return datetime.datetime.utcnow().strftime('%d/%b/%Y:%H:%M:%S +0000')


def generate_fixed_combinations():
    """Pre-generate combinations of source IP, destination IP, and URL"""
    combinations = []
    urls = ["/v1/app/list", "/v1/app/details", "/v1/app/update", "/v1/user/login", "/v1/order/create"]
    for _ in range(random.randint(5, 9)):  # Generate 5 to 9 combinations
        source_ip = generate_ipv4()
        dest_ip = generate_ipv4()
        url = random.choice(urls)
        combinations.append((source_ip, dest_ip, url))
    return combinations

def generate_entry(index, combinations):
    """Generate a single log entry using pre-defined combinations"""
    # Randomly choose one of the pre-generated combinations
    source_ip, dest_ip, url = random.choice(combinations)

    entry = {
        "time_local": generate_timestamp(),
        "remote_addr": source_ip,
        "remote_user": "",
        "request": generate_request(url),
        "status": str(random.choice([200, 404, 500, 301])),
        "body_bytes_sent": str(random.randint(500, 5000)),
        "http_referer": "https://www.referrer.com",
        "http_user_agent": generate_user_agent(),
        "http_x_forwarded_for": dest_ip
    }
    return entry


def send_log_entry_to_api(entry):
    """Send log entry to FastAPI endpoint"""
    url = "http://127.0.0.1:8000/deviceTrustLevelModel"  # 您可以根据需要修改接口URL
    headers = {'Content-Type': 'application/json'}

    # 将生成的日志作为请求体发送到接口
    response = requests.post(url, data=json.dumps(entry), headers=headers)
    if response.status_code == 200:
        print("请求成功:", response.json())
    else:
        print(f"请求失败，状态码: {response.status_code}, 错误信息: {response.text}")


def main():
    """Main function to simulate log printing and sending to API"""
    filename = "../result/output_log.txt"  # 您可以根据需要修改
    logs_per_second = 10  # 您可以根据需要修改
    total_logs = 2000  # 您可以根据需要修改

    index = 1
    combinations = generate_fixed_combinations()  # 预先生成源IP、目的IP和URL组合库

    with open(filename, 'a', encoding='utf-8') as f:
        while index <= total_logs:
            start_time = datetime.datetime.utcnow()
            for _ in range(min(logs_per_second, total_logs - index + 1)):
                entry = generate_entry(index, combinations)
                json_str = json.dumps(entry, ensure_ascii=False)
                f.write(json_str + '\n')

                # 发送日志到 FastAPI 接口
                send_log_entry_to_api(entry)

                index += 1
            # 等待1秒以模拟实时日志

    print(f"Log entries written to {filename}. Total: {total_logs}")


if __name__ == "__main__":
    main()
