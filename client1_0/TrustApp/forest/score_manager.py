import json
import threading
import time
import uuid  # 用于生成 UUID
from datetime import datetime


class ScoresManager:
    def __init__(self, scores_file_path='../config/scores.json', update_interval=30):
        self.scores_file_path = scores_file_path
        self.update_interval = update_interval
        self.scores_lock = threading.Lock()
        self.scores = {"devices": {}, "browsers": {}, "services": {}}
        self.load_scores()
        # 启动定期更新线程
        self.update_thread = threading.Thread(target=self._update_scores_periodically, daemon=True)
        self.update_thread.start()
        # 启动定期保存线程
        self.save_thread = threading.Thread(target=self._save_scores_periodically, daemon=True)
        self.save_thread.start()
        # 日志文件名（小写）
        self.log_file_path = 'scores_log.txt'

    def load_scores(self):
        try:
            with self.scores_lock:
                with open(self.scores_file_path, 'r') as f:
                    self.scores = json.load(f)
        except FileNotFoundError:
            # 如果文件不存在，初始化空的分数字典
            self.scores = {"devices": {}, "browsers": {}, "services": {}}
        except json.JSONDecodeError:
            # 处理 JSON 解析错误
            self.scores = {"devices": {}, "browsers": {}, "services": {}}

    def save_scores(self):
        with self.scores_lock:
            # 保存分数到文件
            with open(self.scores_file_path, 'w') as f:
                json.dump(self.scores, f, indent=4)

            # 生成日志信息
            log_entry = self._generate_log_entry()
            # 将日志信息写入文件，每次写入一行
            with open(self.log_file_path, 'a') as log_file:
                log_file.write(json.dumps(log_entry) + '\n')

    def _generate_log_entry(self):
        # 生成外层 UUID
        log_uuid = str(uuid.uuid4())
        data_list = []

        # 处理设备分数
        for device_id, data in self.scores.get('devices', {}).items():
            item_uuid = str(uuid.uuid4())
            data_list.append({
                "uuid": item_uuid,
                "type": 1,  # 假设 1 代表设备
                "name": "device",
                "id": device_id,
                "score": data.get('score', 100)
            })

        # 处理浏览器分数
        for browser_id, data in self.scores.get('browsers', {}).items():
            item_uuid = str(uuid.uuid4())
            data_list.append({
                "uuid": item_uuid,
                "type": 0,  # 假设 0 代表浏览器
                "name": "browser",
                "id": browser_id,
                "score": data.get('score', 100)
            })

        # 处理服务分数
        for service_id, data in self.scores.get('services', {}).items():
            item_uuid = str(uuid.uuid4())
            data_list.append({
                "uuid": item_uuid,
                "type": 2,  # 假设 2 代表服务
                "name": "service",
                "id": service_id,
                "score": data.get('score', 100)
            })

        # 组装日志条目
        log_entry = {
            "uuid": log_uuid,
            "data": data_list
        }

        return log_entry

    def get_scores(self):
        with self.scores_lock:
            return self.scores.copy()

    def update_device_score(self, ip, score_decrement):
        with self.scores_lock:
            devices = self.scores.get('devices', {})
            device = devices.get(ip, {"score": 100, "last_reset": ""})
            device['score'] = max(0, device.get('score', 100) - score_decrement)
            device['last_reset'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            devices[ip] = device
            self.scores['devices'] = devices
            # 每次更新后保存分数
            self.save_scores()

    def _update_scores_periodically(self):
        while True:
            time.sleep(self.update_interval)
            self.load_scores()
            # 这里可以添加其他需要定期执行的操作

    def _save_scores_periodically(self):
        while True:
            time.sleep(self.update_interval)
            self.save_scores()
            # 这里可以添加其他需要定期执行的操作


# 创建 ScoresManager 的单例实例
scores_manager = ScoresManager()
