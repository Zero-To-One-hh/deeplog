#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import time

# Nginx日志格式
log_format = '{ip} - {user} [{datetime}] "{method} {url} {protocol}" {status} {size} "{referer}" "{user_agent}"'

# 攻击样本
attack_patterns = [
    "1' OR '1'='1",  # SQL注入
    "<script>alert('XSS')</script>",  # XSS攻击
    "../../../../etc/passwd",  # 目录遍历攻击
    "DROP TABLE users;",  # SQL删除命令
    "<img src='x' onerror='alert(1)'>",  # XSS图片标签
]

# 异常行为样本
abnormal_patterns = [
    "/login?username=admin&password=wrongpass",  # 暴力破解尝试
    "/login?username=admin&password=admin",  # 重复登录成功
    "/admin/unauthorized",  # 非法访问
    "/login?username=guest&password=guest",  # 暴力破解尝试
    "/login?username=admin&password=wrongpassword",  # 重复登录失败
]

# 模拟 IP 地址（限制为10个地址）
ip_list = [
    "192.168.0.1", "192.168.0.2", "192.168.0.3", "192.168.0.4", "192.168.0.5",
    "10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4", "10.0.0.5"
]


# 模拟请求方法
def generate_method():
    return random.choice(["GET", "POST", "PUT", "DELETE"])


# 模拟 HTTP 状态码
def generate_status():
    return random.choice([200, 301, 302, 400, 403, 404, 500])


# 模拟用户代理
def generate_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15.7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ]
    return random.choice(user_agents)


# 模拟异常行为的URL（如重复登录）
def generate_abnormal_url():
    abnormal_url = random.choice(abnormal_patterns)
    # print("abnormal_url: ", abnormal_url)
    return abnormal_url


# 模拟时间戳
def generate_datetime():
    return time.strftime('%d/%b/%Y:%H:%M:%S +0000', time.gmtime())


# 生成模拟异常日志
def generate_abnormal_log():
    ip = random.choice(ip_list)
    user = "-"  # 假设无用户
    datetime = generate_datetime()
    method = generate_method()

    # 使用异常行为的 URL
    url = generate_abnormal_url()

    protocol = "HTTP/1.1"
    status = generate_status()
    size = random.randint(200, 5000)  # 假设返回的响应大小
    referer = "-"  # 无referer
    user_agent = generate_user_agent()

    return log_format.format(ip=ip, user=user, datetime=datetime, method=method, url=url, protocol=protocol,
                             status=status, size=size, referer=referer, user_agent=user_agent)


# 生成指定数量的异常日志
def generate_abnormal_logs(num_logs):
    abnormal_logs = [generate_abnormal_log() for _ in range(num_logs)]
    return "\n".join(abnormal_logs)


if __name__ == "__main__":
    num_logs = 100  # 生成100条异常日志
    abnormal_logs = generate_abnormal_logs(num_logs)

    # 将异常日志保存到文件
    with open("nginx_abnormal_logs.txt", "w") as f:
        f.write(abnormal_logs)

    print(f"已生成 {num_logs} 条异常日志并保存到 nginx_abnormal_logs.txt")
