# score_manager.py
import json
import threading
import time
import uuid  # 用于生成 UUID
from datetime import datetime


class SingletonMeta(type):
    """
    线程安全的单例模式实现
    """
    _instance_lock = threading.Lock()
    _instances = {}

    def __call__(cls, *args, **kwargs):
        with cls._instance_lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class ScoresManager(metaclass=SingletonMeta):
    def __init__(self, scores_file_path='./config/scores.json', update_interval=10):
        # 防止多次初始化
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True

        self.scores_file_path = scores_file_path
        self.update_interval = update_interval
        self.scores_lock = threading.Lock()
        self.scores = {"devices": {}, "browsers": {}, "services": {}}
        self.load_scores()
        # 启动定期更新线程
        #self.update_thread = threading.Thread(target=self._update_scores_periodically, daemon=True)
        #self.update_thread.start()
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
        # 生成外层 UUID 和时间戳
        log_uuid = str(uuid.uuid4())
        log_timestamp = datetime.now().isoformat()
        data_list = []

        # 处理设备分数
        for device_id, data in self.scores.get('devices', {}).items():
            item_uuid = str(uuid.uuid4())
            item_timestamp = datetime.now().isoformat()
            data_list.append({
                "uuid": item_uuid,
                "type": 1,  # 假设 1 代表设备
                "name": "device",
                "id": device_id,
                "score": data.get('score', 100),
                "timestamp": item_timestamp  # 增加时间戳
            })

        # 处理浏览器分数
        for browser_id, data in self.scores.get('browsers', {}).items():
            item_uuid = str(uuid.uuid4())
            item_timestamp = datetime.now().isoformat()
            data_list.append({
                "uuid": item_uuid,
                "type": 0,  # 假设 0 代表浏览器
                "name": "browser",
                "id": browser_id,
                "score": data.get('score', 100),
                "timestamp": item_timestamp  # 增加时间戳
            })

        # 处理服务分数
        for service_id, data in self.scores.get('services', {}).items():
            item_uuid = str(uuid.uuid4())
            item_timestamp = datetime.now().isoformat()
            data_list.append({
                "uuid": item_uuid,
                "type": 2,  # 假设 2 代表服务
                "name": "service",
                "id": service_id,
                "score": data.get('score', 100),
                "timestamp": item_timestamp  # 增加时间戳
            })

        # 组装日志条目，增加外层时间戳
        log_entry = {
            "uuid": log_uuid,
            "timestamp": log_timestamp,  # 外层增加时间戳
            "data": data_list
        }

        return log_entry

    def get_scores(self):
        with self.scores_lock:
            return self.scores.copy()

    def update_device_score(self, device_id, score_decrement):
        self._update_entity_score('devices', device_id, score_decrement)

    def update_browser_score(self, browser_id, score_decrement):
        self._update_entity_score('browsers', browser_id, score_decrement)

    def update_service_score(self, service_id, score_decrement):
        self._update_entity_score('services', service_id, score_decrement)

    def _update_entity_score(self, entity_type, entity_id, score_decrement):
        with self.scores_lock:
            current_time = datetime.now()
            entity_scores = self.scores.get(entity_type, {})
            entity = entity_scores.get(entity_id, {"score": 100, "last_reset": ""})

            # 重置分数逻辑
            last_reset_str = entity.get('last_reset', '')
            if last_reset_str:
                try:
                    # 修改后的代码，匹配日期时间格式
                    last_reset = datetime.strptime(last_reset_str, "%Y-%m-%dT%H:%M:%S.%f")
                except ValueError:
                    # 如果解析失败，尝试使用 ISO 格式解析
                    last_reset = datetime.fromisoformat(last_reset_str)
            else:
                last_reset = current_time
                # 更新实体的 last_reset 字段，以统一日期时间格式
                entity['last_reset'] = current_time.strftime("%Y-%m-%dT%H:%M:%S.%f")

            reset_interval_seconds = 3 * 3600  # 或者从配置中获取

            if (current_time - last_reset).total_seconds() >= reset_interval_seconds:
                entity['score'] = 100
                entity['last_reset'] = current_time.strftime("%Y-%m-%dT%H:%M:%S.%f")

            # 减少分数
            entity['score'] = max(0, entity.get('score', 100) - score_decrement)
            entity['last_reset'] = current_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
            entity_scores[entity_id] = entity
            self.scores[entity_type] = entity_scores

    def _update_scores_periodically(self):
        while True:
            time.sleep(self.update_interval)
            self.load_scores()
            # 这里可以添加其他需要定期执行的操作

    def _save_scores_periodically(self):
        while True:
            time.sleep(self.update_interval/2)
            self.save_scores()
            time.sleep(self.update_interval/2)
            # 这里可以添加其他需要定期执行的操作


# 创建 ScoresManager 的单例实例
scores_manager = ScoresManager()
