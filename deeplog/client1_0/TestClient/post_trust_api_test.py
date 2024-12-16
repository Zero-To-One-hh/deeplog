# -*- coding: utf-8 -*-
import httpx

# 设置 API 端点
API_URL = "http://127.0.0.1:8000/TrustLevelResult"

def test_get_trust_level_result(result_type=None):
    # 构造请求参数
    params = {}
    if result_type is not None:
        params['result_type'] = result_type

    # 发送请求
    response = httpx.post(API_URL, params=params)

    # 检查响应状态码
    if response.status_code == 200:
        print(f"测试成功: result_type={result_type}")
        print("返回数据:", response.json())
    else:
        print(f"测试失败: result_type={result_type}")
        print("状态码:", response.status_code)
        print("错误详情:", response.json())

# 运行测试
if __name__ == "__main__":
    print("测试不带 result_type 的请求：")
    test_get_trust_level_result()  # 不传入 result_type，默认返回所有类型的评分

    print("\n测试 result_type=0 (浏览器评分)：")
    test_get_trust_level_result(result_type=0)

    print("\n测试 result_type=1 (设备评分)：")
    test_get_trust_level_result(result_type=1)

    print("\n测试 result_type=2 (服务评分)：")
    test_get_trust_level_result(result_type=2)

    print("\n测试无效的 result_type=3：")
    test_get_trust_level_result(result_type=3)  # 测试无效的 result_type
