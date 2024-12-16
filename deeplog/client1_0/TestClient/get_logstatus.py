# -*- coding: utf-8 -*-
import httpx

# 设置 API 端点
API_URL = "http://127.0.0.1:8000/bj/LogStatus"

def test_get_logStatus():

    # 发送请求
    response = httpx.get(API_URL)

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
    test_get_logStatus()
