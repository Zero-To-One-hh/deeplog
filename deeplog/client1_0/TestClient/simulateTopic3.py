from typing import Optional

from fastapi import FastAPI, Query

app = FastAPI()

# 预设的响应数据
mock_response_data = {
    "code": 1,
    "message": "success",
    "data": [
{
            "@timestamp": "2024-07-13T07:53:56.117Z",
            "gid": 116,
            "eth_src": "02:42:AC:11:00:03",
            "mpls": 0,
            "dst_addr": "172.17.0.2",
            "rule": "116:434:1",
            "timestamp": "05/29-16:38:58.578545",
            "service": "unknown",
            "pkt_gen": "raw",
            "rev": 1,
            "seconds": 1716971938,
            "ttl": 64,
            "proto": "TCP",
            "iface": "eth0",
            "icmp_seq": 16136,
            "src_ap": "172.17.0.3:0",
            "priority": 3,
            "eth_type": "0x800",
            "ip_len": 8,
            "icmp_type": 8,
            "msg": "DoS攻击告警，检测到FIN flood泛洪攻击",
            "attack_type": {
                "[message]": "DoS攻击告警"
            },
            "eth_len": 42,
            "src_addr": "172.17.0.3",
            "class": "none",
            "vlan": 0,
            "dst_ap": "172.17.0.2:0",
            "pkt_len": 28,
            "tos": 0,
            "icmp_code": 0,
            "ip_id": 13862,
            "sid": 434,
            "dir": "C2S",
            "icmp_id": 30464,
            "pkt_num": 297693,
            "action": "allow",
            "eth_dst": "02:42:AC:11:00:02",
            "log": {
                "file": {
                    "path": "/var/log/snort/alert_json.txt"
                }
            }
        },
        {
            "@timestamp": "2024-07-13T07:53:56.117Z",
            "mpls": 0,
            "timestamp": "05/29-16:38:58.578545",
            "action": "allow",
            "pkt_len": 28,
            "dst_ap": "172.17.0.2:0",
            "pkt_num": 297693,
            "seconds": 1716971938,
            "attack_type": {
                "[message]": "DoS攻击告警"
            },
            "log": {
                "file": {
                    "path": "/var/log/snort/alert_json.txt"
                }
            },
            "iface": "eth0",
            "class": "none",
            "msg": "DoS攻击告警，检测到UDP flood泛洪攻击",
            "vlan": 0,
            "eth_src": "02:42:AC:11:00:03",
            "eth_type": "0x800",
            "eth_len": 42,
            "eth_dst": "02:42:AC:11:00:02",
            "pkt_gen": "raw",
            "proto": "TCP",
            "tos": 0,
            "rule": "116:434:1",
            "src_ap": "172.17.0.3:0",
            "gid": 116,
            "ip_id": 13862,
            "icmp_id": 30464,
            "icmp_code": 0,
            "icmp_type": 8,
            "sid": 434,
            "ip_len": 8,
            "src_addr": "172.17.0.3",
            "dst_addr": "172.17.0.2",
            "rev": 1,
            "icmp_seq": 16136,
            "priority": 3,
            "service": "unknown",
            "ttl": 64,
            "dir": "C2S"
        },
        {
            "@timestamp": "2024-07-13T07:53:56.117Z",
            "rev": 1,
            "iface": "eth0",
            "class": "none",
            "src_addr": "172.17.0.3",
            "dst_ap": "172.17.0.2:0",
            "service": "unknown",
            "priority": 3,
            "seconds": 1716971938,
            "sid": 434,
            "icmp_type": 8,
            "eth_dst": "02:42:AC:11:00:02",
            "pkt_gen": "raw",
            "pkt_num": 297693,
            "icmp_id": 30464,
            "eth_src": "02:42:AC:11:00:03",
            "action": "allow",
            "vlan": 0,
            "ttl": 64,
            "log": {
                "file": {
                    "path": "/var/log/snort/alert_json.txt"
                }
            },
            "gid": 116,
            "timestamp": "05/29-16:38:58.578545",
            "icmp_code": 0,
            "proto": "TCP",
            "eth_len": 42,
            "tos": 0,
            "dir": "C2S",
            "msg": "DoS攻击告警，检测到ICMP flood泛洪攻击",
            "rule": "116:434:1",
            "attack_type": {
                "[message]": "DoS攻击告警"
            },
            "mpls": 0,
            "eth_type": "0x800",
            "icmp_seq": 16136,
            "ip_len": 8,
            "ip_id": 13862,
            "src_ap": "172.17.0.3:0",
            "dst_addr": "172.17.0.2",
            "pkt_len": 28
        },
        {
            "@timestamp": "2024-07-13T07:53:56.117Z",
            "action": "allow",
            "eth_dst": "02:42:AC:11:00:02",
            "dst_ap": "172.17.0.2:0",
            "msg": "DoS攻击告警，检测到Ping of Death攻击",
            "src_addr": "172.17.0.3",
            "seconds": 1716971938,
            "pkt_len": 28,
            "priority": 3,
            "ip_id": 13862,
            "pkt_gen": "raw",
            "eth_src": "02:42:AC:11:00:03",
            "src_ap": "172.17.0.3:0",
            "class": "none",
            "icmp_type": 8,
            "rule": "116:434:1",
            "ttl": 64,
            "icmp_seq": 16136,
            "ip_len": 8,
            "attack_type": {
                "[message]": "DoS攻击告警"
            },
            "log": {
                "file": {
                    "path": "/var/log/snort/alert_json.txt"
                }
            },
            "icmp_id": 30464,
            "rev": 1,
            "sid": 434,
            "dir": "C2S",
            "service": "unknown",
            "pkt_num": 297693,
            "dst_addr": "172.17.0.2",
            "gid": 116,
            "mpls": 0,
            "eth_type": "0x800",
            "proto": "TCP",
            "vlan": 0,
            "iface": "eth0",
            "icmp_code": 0,
            "eth_len": 42,
            "timestamp": "05/29-16:38:58.578545",
            "tos": 0
        },
        {
            "@timestamp": "2024-07-13T07:53:56.117Z",
            "tos": 0,
            "action": "allow",
            "priority": 3,
            "iface": "eth0",
            "icmp_type": 8,
            "vlan": 0,
            "msg": "DoS攻击告警，检测到RST flood泛洪攻击",
            "timestamp": "05/29-16:38:58.578545",
            "sid": 434,
            "log": {
                "file": {
                    "path": "/var/log/snort/alert_json.txt"
                }
            },
            "icmp_seq": 16136,
            "pkt_len": 28,
            "rule": "116:434:1",
            "seconds": 1716971938,
            "src_ap": "172.17.0.3:0",
            "eth_type": "0x800",
            "class": "none",
            "src_addr": "172.17.0.3",
            "rev": 1,
            "ttl": 64,
            "pkt_num": 297693,
            "pkt_gen": "raw",
            "gid": 116,
            "eth_len": 42,
            "ip_len": 8,
            "dst_addr": "172.17.0.2",
            "dst_ap": "172.17.0.2:0",
            "attack_type": {
                "[message]": "DoS攻击告警"
            },
            "icmp_id": 30464,
            "proto": "TCP",
            "eth_src": "02:42:AC:11:00:03",
            "dir": "C2S",
            "mpls": 0,
            "service": "unknown",
            "ip_id": 13862,
            "eth_dst": "02:42:AC:11:00:02",
            "icmp_code": 0
        }
    ]
}


# 模拟接口，用于接收查询参数
@app.get("/test")
async def get_mock_data(
        startTime: Optional[str] = Query(None),
        endTime: Optional[str] = Query(None),
        count: Optional[int] = Query(None)
):
    # 可以根据需要对参数进行处理和验证
    print(f"Received params - startTime: {startTime}, endTime: {endTime}, count: {count}")

    # 返回预设的响应数据
    return mock_response_data
if __name__ == "__main__":
    import uvicorn



    # 启动uvicorn服务器
    uvicorn.run(app, host="localhost", port=8011)