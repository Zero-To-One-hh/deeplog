import random

# 定义可能的攻击消息和类型
attack_types_and_messages = {
    'DoS攻击告警': [
        "检测到SYN flood泛洪攻击",
        "检测到UDP flood泛洪攻击",
        "检测到ICMP flood泛洪攻击"
    ],
    'SQL注入告警': [
        "检测到SQL注入攻击尝试",
        "检测到SQL盲注攻击",
        "检测到SQL批量注入攻击"
    ],
    '漏洞利用告警': [
        "检测到远程代码执行攻击",
        "检测到缓冲区溢出攻击",
        "检测到文件包含漏洞攻击"
    ],
    '暴力破解告警': [
        "检测到密码暴力破解攻击",
        "检测到账户爆破攻击",
        "检测到弱口令攻击"
    ],
    '恶意扫描告警': [
        "检测到端口扫描行为",
        "检测到漏洞扫描行为",
        "检测到资产探测行为"
    ]
}

# 生成10个IP地址
ip_addresses = [f"192.168.1.{i}" for i in range(1, 11)]

# 生成MAC地址
def generate_mac():
    return ":".join([f"{random.randint(0,255):02x}" for _ in range(6)])

# 生成数据
def generate_data(num_records=50):
    data = []
    for _ in range(num_records):
        priority = random.randint(1, 5)
        attack_type = random.choice(list(attack_types_and_messages.keys()))
        msg = random.choice(attack_types_and_messages[attack_type])
        src_ip = random.choice(ip_addresses)
        dst_ip = random.choice(ip_addresses)
        while dst_ip == src_ip:  # 确保源IP和目标IP不同
            dst_ip = random.choice(ip_addresses)
            
        record = {
            'priority': priority,
            'msg': msg,
            'dir': 'C2S',
            'attack_type': attack_type,
            'action': 'allow',
            'eth_len': 42,
            'dst_ap': f"{dst_ip}:0",
            'eth_dst': generate_mac(),
            'dst_addr': dst_ip,
            'src_addr': src_ip,
            'rule': '116:434:1'
        }
        data.append(record)
    return data

# 生成数据并写入文件
data = generate_data(50000)
with open('./output.txt', 'w', encoding='utf-8') as f:
    for record in data:
        line = f"{record['priority']}\t{record['msg']}\t{record['dir']}\t{record['attack_type']}\t{record['action']}\t{record['eth_len']}\t{record['dst_ap']}\t{record['eth_dst']}\t{record['dst_addr']}\t{record['src_addr']}\t{record['rule']}\n"
        f.write(line)
    print("数据生成完成，已写入output.txt")