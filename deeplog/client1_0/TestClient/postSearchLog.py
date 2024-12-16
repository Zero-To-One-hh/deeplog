# -*- coding: utf-8 -*-
import httpx

# 设置 API 端点
API_URL = "http://127.0.0.1:8000/bj/searchLog"

def test_get_log(
        pageSize: int,
        pageNum: int
        ):
    # 构造请求参数
    params = {}
    if pageSize is not None:
        params['pageSize'] = pageSize

    if pageNum is not None:
        params['pageNum'] = pageNum

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
    pageSize = 1
    pageNum=20
    test_get_log(pageSize, pageNum)