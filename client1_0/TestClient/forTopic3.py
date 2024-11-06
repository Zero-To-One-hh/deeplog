# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import base64

app = Flask(__name__)

# 模拟的数据（通常您会从数据库或其他数据源获取）
sample_data = [
    {
        "seconds": "1689318506",
        "action": "allow",
        "class": "none",
        "b64_data": "hoYAUFL3Fn4AAAAAoAJyENoCAAACBAW0BAIICglHPsEAAAAAAQMDBw==",
        "dir": "C2S",
        "dst_addr": "172.17.0.2",
        "dst_ap": "172.17.0.2:0",
        "eth_dst": "02:42:AC:11:00:02",
        "eth_len": "102",
        "eth_src": "02:42:26:C6:CD:EF",
        "eth_type": "0x800",
        "gid": "1",
        "icmp_code": "1",
        "icmp_id": "0",
        "icmp_seq": "0",
        "icmp_type": "3",
        "iface": "eth0",
        "ip_id": "40102",
        "ip_len": "68",
        "msg": "ICMP Traffic Detected",
        "mpls": "0",
        "pkt_gen": "raw",
        "pkt_len": "88",
        "pkt_num": "476232",
        "priority": "0",
        "proto": "ICMP",
        "rev": "0",
        "rule": "1:10000001:0",
        "service": "unknown",
        "sid": "10000001",
        "src_addr": "172.31.236.213",
        "src_ap": "172.31.236.213:0",
        "tos": "192",
        "ttl": "64",
        "vlan": "0",
        "timestamp": "07/14-15:08:26.989941"
    },
    # 可以添加更多模拟数据
]

@app.route('/apispace/public/snort/list/bytime', methods=['GET'])
def get_snort_data():
    try:
        # 获取请求参数
        start_time_str = request.args.get('startTime')
        end_time_str = request.args.get('endTime')
        count_str = request.args.get('count')

        # 设置默认的开始和结束时间
        if not end_time_str:
            end_time = datetime.now()
        else:
            try:
                end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    end_time = datetime.strptime(end_time_str, '%Y-%m-%d')
                except ValueError:
                    return jsonify({"code": "500", "message": "结束时间格式错误", "data": []})

        if not start_time_str:
            start_time = end_time - timedelta(days=1)
        else:
            try:
                start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    start_time = datetime.strptime(start_time_str, '%Y-%m-%d')
                except ValueError:
                    return jsonify({"code": "500", "message": "开始时间格式错误", "data": []})

        # 处理count参数
        max_count = 10000
        if count_str:
            try:
                count = int(count_str)
                if count > max_count:
                    count = max_count
            except ValueError:
                return jsonify({"code": "500", "message": "count参数必须是数字", "data": []})
        else:
            count = max_count

        # 过滤数据（这里使用模拟数据，实际情况应从数据库查询并过滤）
        filtered_data = []
        for item in sample_data:
            event_time = datetime.fromtimestamp(int(item['seconds']))
            if True:
                filtered_data.append(item)
                if len(filtered_data) >= count:
                    break

        return jsonify({
            "code": "200",
            "message": "OK",
            "data": filtered_data
        })
    except Exception as e:
        return jsonify({"code": "500", "message": str(e), "data": []})

if __name__ == '__main__':
    # 运行Flask应用，监听所有公网IP地址的8000端口
    app.run(host='0.0.0.0', port=8003)
