# -*- coding: utf-8 -*-
import httpx

# 设置 API 端点
API_URL = "http://127.0.0.1:8000/bj/searchTopic3"

def test_get_trust_level_result(start_time: str,
        end_time: str,
        count: int
                                ):
    # 构造请求参数
    params = {}
    if start_time is not None:
        params['start_time'] = start_time

    if end_time is not None:
        params['end_time'] = end_time

    if count is not None:
        params['count'] = count

    # 发送请求
    response = httpx.post(API_URL, params=params)

    # 检查响应状态码
    if response.status_code == 200:
        print(f"测试成功: ")
        print("返回数据:", response.json())
    else:
        print(f"测试失败:")
        print("状态码:", response.status_code)
        print("错误详情:", response.json())

# 运行测试
if __name__ == "__main__":
    start_time="2023-01-01"
    end_time="2023-01-02"
    count=1
    test_get_trust_level_result(start_time, end_time, count)
