import httpx

numbers = 2000


def send_post_request(client, url, payload):
    response = client.post(url, json=payload)
    return response


def main():
    url = "http://localhost:8000/deviceTrustLevelModel"
    payload_template = {
        "deviceId": "device123",
        "appId": "app456",
        "targetIp": "192.168.0.1",
        "targetPort": 8080,
        "status": "active",
        "userId": "user789",
        "level": "high",
        "agreement": "agreement123",
        "logMessage": ""
    }

    # 读取日志文件，指定编码为 utf-8
    log_file_path = "../messages.log"
    with open(log_file_path, "r", encoding="utf-8") as file:
        log_lines = file.readlines()

    log_lines = log_lines[:numbers]

    with httpx.Client() as client:
        responses = []
        for log_message in log_lines:
            payload = payload_template.copy()
            if log_message == '':
                continue
            payload["logMessage"] = log_message.strip()
            response = send_post_request(client, url, payload)
            responses.append(response)

        for i, response in enumerate(responses):
            print(f"Response {i + 1}: {response.status_code}")
            try:
                response_json = response.json()
                print(f"Response JSON {i + 1}: {response_json}")
            except ValueError:
                print(f"Response {i + 1} is not valid JSON: {response.text}")


if __name__ == "__main__":
    main()
