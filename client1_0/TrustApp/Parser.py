import os
import json

# 从 config 目录读取配置文件
config_path = os.path.join(os.path.dirname(__file__), 'config', 'url_mapping.json')


def load_url_config():
    with open(config_path, 'r') as file:
        return json.load(file)


url_config = load_url_config()


def parse_url(url: str):
    # 使用配置文件的逻辑解析 URL，返回 serviceId 和 logId
    for key, value in url_config.items():
        if url.startswith(key):
            return value['serviceId'], value['logId']
    raise ValueError("无法从URL解析出serviceId和logId")
