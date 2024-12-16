# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
logger = logging.getLogger(__name__)

# 示例数据（模拟数据库数据）
sample_data = [
    {
        "seconds": "1689318506",
        "action": "allow",
        "class": "none",
        "dir": "C2S",
        "dst_addr": "172.17.0.2",
        "dst_ap": "172.17.0.2:0",
        "eth_dst": "02:42:AC:11:00:02",
        "eth_src": "02:42:26:C6:CD:EF",
        "iface": "eth0",
        "msg": "ICMP Traffic Detected",
        "priority": "0",
        "src_addr": "172.31.236.213",
        "src_ap": "172.31.236.213:0",
        "@timestamp": "07/14-15:08:26.989941"
    },
    # 可以添加更多的模拟数据
]

# 请求模型
class Topic3Request(BaseModel):
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    count: Optional[int] = 100

# 时间格式解析函数
def parse_time(time_str: Optional[str]) -> datetime:
    try:
        if time_str:
            if len(time_str) == 10:  # 仅日期
                return datetime.strptime(time_str, "%Y-%m-%d")
            else:  # 日期 + 时间
                return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        return None
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format. Use 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'")

# 课题三告警信息展示接口
@app.post("/bj/searchTopic3")
async def search_topic3(request: Topic3Request):
    try:
        # 处理默认时间
        end_time = parse_time(request.endTime) or datetime.now()
        start_time = parse_time(request.startTime) or (end_time - timedelta(days=1))

        # 验证 count 参数（最大值10000）
        count = min(request.count, 10000)

        # 过滤数据
        filtered_data = []
        for entry in sample_data:
            event_time = datetime.fromtimestamp(int(entry["seconds"]))
            if start_time <= event_time <= end_time:
                filtered_data.append(entry)

        # 限制返回条数
        filtered_data = filtered_data[:count]

        return {
            "code": "200",
            "message": "OK",
            "data": filtered_data
        }

    except HTTPException as e:
        logger.error(f"请求错误: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"内部服务器错误: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
