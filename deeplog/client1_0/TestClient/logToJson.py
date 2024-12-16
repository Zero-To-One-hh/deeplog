import json
import re

#解析日志信息为json格式
def parse_log_entry(log_entry):
    """Parse a single log entry and extract required information."""
    log_pattern = r'(\d+\.\d+\.\d+\.\d+).*\[(.*?)\] "(.*?)" \d+ \d+ "-" "(.*?)"'
    match = re.match(log_pattern, log_entry)

    if match:
        ip = match.group(1)
        timestamp = match.group(2)
        service = match.group(3)
        browser = match.group(4)
        return {
            "ip": ip,
            "timestamp": timestamp,
            "service": service,
            "browser": browser
        }
    return None

#解析日志文件
def parse_log_file(filename,jsonfile):
    """Parse the log file and return a list of entries, total logs count, and unique device count."""
    ip_set = set()
    total_logs = 0
    parsed_entries = []

    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            entry = parse_log_entry(line.strip())
            if entry:
                parsed_entries.append(entry)
                ip_set.add(entry["ip"])
                total_logs += 1
        # 将解析后的日志条目保存到 JSON 文件
    with open(jsonfile, 'w', encoding='utf-8') as json_file:
        json.dump({"data": parsed_entries}, json_file, ensure_ascii=False, indent=4)

    return total_logs, len(ip_set)


#更新日志统计数据
def update_statistics_in_file(stats_filename, total_logs, unique_devices):
    """Update log count and unique device count in an existing JSON file."""
    try:
        # 读取现有的 JSON 文件
        with open(stats_filename, 'r', encoding='gbk') as file:
            data = json.load(file)

        # 更新指定的字段
        data['totalCount'] = total_logs
        data['deviceCount'] = unique_devices

        # 将更新后的内容写回文件
        with open(stats_filename, 'w', encoding='gbk') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        print(f"Updated {stats_filename}: totalCount={total_logs}, deviceCount={unique_devices}")

    except FileNotFoundError:
        print(f"Error: {stats_filename} not found.")
    except json.JSONDecodeError:
        print(f"Error: Failed to parse {stats_filename} as JSON.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    log_file = 'generated_logs.txt'  # 这是您的日志文件
    stats_file = '../TrustApp/config/log_statistics.json'  # 这是已有的 JSON 文件
    jsonfile= 'parsed_logs.json'
    # 解析日志文件获取日志总数和设备数量
    total_logs, unique_devices = parse_log_file(log_file,jsonfile)

    # 更新 JSON 文件中的统计信息
    update_statistics_in_file(stats_file, total_logs, unique_devices)
