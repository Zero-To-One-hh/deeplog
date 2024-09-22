# -*- coding: utf-8 -*-
import json
import random
import datetime
import time


def generate_mac():
    """Generate random MAC address"""
    mac = [random.randint(0x00, 0xff) for _ in range(6)]
    return ':'.join(f"{octet:02X}" for octet in mac)


def generate_ipv4():
    """Generate random IPv4 address"""
    return '.'.join(str(random.randint(0, 255)) for _ in range(4))


def generate_ipv6():
    """Generate random IPv6 address"""
    return ':'.join(f"{random.randint(0, 65535):x}" for _ in range(8))


def generate_ip():
    """Randomly generate either IPv4 or IPv6 address"""
    return generate_ipv4() if random.choice([True, False]) else generate_ipv6()


def generate_browser_id():
    """Generate random browser identifier"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (X11; Linux x86_64)",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
        "Mozilla/5.0 (Android 11; Mobile; rv:83.0)"
    ]
    return random.choice(user_agents)


def generate_service_id():
    """Generate random service identifier"""
    services = ["SERVICE_XYZ", "SERVICE_ABC", "SERVICE_DEF", "SERVICE_123", "SERVICE_GHI"]
    return random.choice(services)


def generate_log_id(index):
    """Generate unique log ID that can be converted to an integer"""
    # timestamp = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
    # return f"{timestamp}{index:06}"  # 移除 'LOG' 前缀，确保返回的字符串是数字
    return "1"



def generate_timestamp():
    """Generate ISO 8601 timestamp"""
    return datetime.datetime.utcnow().isoformat() + 'Z'


def generate_raw_log():
    """Generate raw log message"""
    messages = [
        "User accessed the service.",
        "Login successful.",
        "Error occurred.",
        "Transaction completed."
    ]
    return random.choice(messages)


# Pre-generate up to 10 combinations of browserId, deviceMac, and serviceId
def generate_fixed_combinations():
    combinations = []
    for _ in range(5):
        browser_id = generate_browser_id()
        device_mac = generate_mac()
        service_id = generate_service_id()
        combinations.append((browser_id, device_mac, service_id))
    return combinations


def generate_entry(index, combinations):
    """Generate a single log entry using pre-defined combinations"""
    # Randomly choose one of the pre-generated combinations
    browser_id, device_mac, service_id = random.choice(combinations)

    entry = {
        "browserId": browser_id,
        "logId": generate_log_id(index),
        "deviceMac": device_mac,
        "deviceIp": generate_ip(),
        "accessPort": random.randint(0, 65535),
        "serviceId": service_id,
        "accessedIp": generate_ip(),
        "rawLog": generate_raw_log(),
        "timestamp": generate_timestamp()
    }
    return entry


def main():
    """Main function to simulate log printing"""
    filename = "../result/output_log.txt"  # 您可以根据需要修改
    logs_per_second = 4     # 您可以根据需要修改
    total_logs = 1000        # 您可以根据需要修改

    index = 1
    combinations = generate_fixed_combinations()  # 预先生成组合

    with open(filename, 'a', encoding='utf-8') as f:
        while index <= total_logs:
            start_time = datetime.datetime.utcnow()
            for _ in range(min(logs_per_second, total_logs - index + 1)):
                entry = generate_entry(index, combinations)
                json_str = json.dumps(entry, ensure_ascii=False)
                f.write(json_str + '\n')
                index += 1
            # 等待1秒以模拟实时日志
            time.sleep(1 - (datetime.datetime.utcnow() - start_time).total_seconds())

    print(f"Log entries written to {filename}. Total: {total_logs}")


if __name__ == "__main__":
    main()
