# score_manager.py
import json
import math
import os
import threading
import time
import uuid  # 用于生成 UUID
from datetime import datetime


class SingletonMeta(type):
    """
    支持基于名称的多实例单例模式实现
    """
    _instance_lock = threading.Lock()
    _instances = {}

    def __call__(cls, *args, **kwargs):
        # 使用 name 参数作为键
        name = kwargs.get('name', None) or (args[0] if args else None)
        if not name:
            raise ValueError("必须提供 name 参数")

        with cls._instance_lock:
            key = (cls, name)
            if key not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[key] = instance
        return cls._instances[key]


class ScoresManager(metaclass=SingletonMeta):
    def __init__(self, name, scores_file_path, log_file_path, update_interval=10):
        # 使用 name 作为唯一标识
        self._instance_name = name

        # 防止同一个 name 的实例多次初始化
        if hasattr(self, '_initialized_' + name) and getattr(self, '_initialized_' + name):
            return
        setattr(self, '_initialized_' + name, True)

        self.scores_file_path = scores_file_path
        self.log_file_path = log_file_path
        self.update_interval = update_interval
        self.scores_lock = threading.Lock()
        self.scores = {"devices": {}, "browsers": {}, "services": {}}
        self.load_scores()

        # 启动定期保存线程
        self.save_thread = threading.Thread(target=self._save_scores_periodically, daemon=True)
        self.save_thread.start()

        # 启动定期回升线程
        self.restore_thread = threading.Thread(target=self._restore_scores_periodically, daemon=True)
        self.restore_thread.start()
        # 日志文件名（小写）
        # self.log_file_path = '/usr/local/zd/run/ai/scores_log.txt'
        self.score_decrement_ratio = 0.1  # 分数上升的比率

        # 确保日志目录存在
        log_dir = os.path.dirname(self.log_file_path)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

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
            # 在保存前对所有分数进行四舍五入保留两位小数
            scores_to_save = self._round_scores(self.scores)

            # 保存分数到文件
            with open(self.scores_file_path, 'w') as f:
                json.dump(scores_to_save, f, indent=4)

            # 生成日志信息
            log_entry = self._generate_log_entry()
            # 将日志信息写入文件，每次写入一行
            with open(self.log_file_path, 'a') as log_file:
                log_file.write(json.dumps(log_entry) + '\n')

    def _round_scores(self, scores_dict):
        """对分数进行四舍五入保留两位小数"""
        rounded_scores = {"devices": {}, "browsers": {}, "services": {}}

        for category in ['devices', 'browsers', 'services']:
            for entity_id, data in scores_dict.get(category, {}).items():
                rounded_scores[category][entity_id] = {
                    'score': round(data.get('score', 100.0), 2),
                    'last_reset': data.get('last_reset', '')
                }

        return rounded_scores

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
                "scoreType": "1",  # 假设 1 代表设备
                "name": device_id,
                "id": device_id,
                "score": str(round(data.get('score', 100), 2)),
                "last_reset": item_timestamp  # 增加时间戳
            })

        # 处理浏览器分数
        for browser_id, data in self.scores.get('browsers', {}).items():
            item_uuid = str(uuid.uuid4())
            item_timestamp = datetime.now().isoformat()
            data_list.append({
                "uuid": item_uuid,
                "scoreType": "0",  # 假设 0 代表浏览器
                "name": browser_id,
                "id": browser_id,
                "score": str(round(data.get('score', 100), 2)),
                "last_reset": item_timestamp  # 增加时间戳
            })

        # 处理服务分数
        for service_id, data in self.scores.get('services', {}).items():
            item_uuid = str(uuid.uuid4())
            item_timestamp = datetime.now().isoformat()
            data_list.append({
                "uuid": item_uuid,
                "scoreType": "2",  # 假设 2 代表服务
                "name": service_id,
                "id": service_id,
                "score": str(round(data.get('score', 100), 2)),
                "last_reset": item_timestamp  # 增加时间戳
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

    def update_device_score(self, device_id, score_decrement_ratio):
        self._update_entity_score('devices', device_id, 0.2)

    def update_browser_score(self, browser_id, score_decrement_ratio):
        self._update_entity_score('browsers', browser_id, 0.01)

    def update_service_score(self, service_id, score_decrement_ratio):
        self._update_entity_score('services', service_id, 0.1)

    def _update_entity_score(self, entity_type, entity_id, score_decrement_ratio = 0.2):
        with self.scores_lock:
            current_time = datetime.now()
            entity_scores = self.scores.get(entity_type, {})
            entity = entity_scores.get(entity_id, {"score": 100.0, "last_reset": ""})

            # 重置分数逻辑
            last_reset_str = entity.get('last_reset', '')
            if last_reset_str:
                try:
                    last_reset = datetime.strptime(last_reset_str, "%Y-%m-%dT%H:%M:%S.%f")
                except ValueError:
                    last_reset = datetime.fromisoformat(last_reset_str)
            else:
                last_reset = current_time
                self._set_last_reset(entity, current_time)

            reset_interval_seconds = 3 * 3600  # 或者从配置中获取

            if (current_time - last_reset).total_seconds() >= reset_interval_seconds:
                entity['score'] = 100.0
                self._set_last_reset(entity, current_time)

            # 非线性扣分（平方根扣分）
            current_score = entity.get('score', 100.0)
            decrement = (math.sqrt(100 - current_score) + 1) * score_decrement_ratio  # 根据当前分数计算扣分
            entity['score'] = max(0.0, current_score - decrement)
            self._set_last_reset(entity, current_time)
            entity_scores[entity_id] = entity
            self.scores[entity_type] = entity_scores

    def _set_last_reset(self, entity, current_time):
        entity['last_reset'] = current_time.strftime("%Y-%m-%dT%H:%M:%S.%f")

    def _restore_scores_periodically(self):
        while True:
            time.sleep(self.update_interval)
            with self.scores_lock:
                for entity_type in ['devices', 'browsers', 'services']:
                    for entity_id, data in self.scores.get(entity_type, {}).items():
                        current_score = data.get('score', 100)
                        if current_score < 100:
                            # 指数回升模拟
                            restoration = int((100 - current_score) * 0.005)  # todo 调整每次回升的速率
                            data['score'] = min(100, current_score + restoration)
                            self.scores[entity_type][entity_id] = data

    def _save_scores_periodically(self):
        while True:
            time.sleep(self.update_interval / 2)
            self.save_scores()
            time.sleep(self.update_interval / 2)
            # 这里可以添加其他需要定期执行的操作


#log_file_path = "/usr/local/zd/run/ai"
log_file_path = os.path.join(".", "logs", "scores")

# 创建三个不同的 ScoresManager 实例
scores_manager_all = ScoresManager(
    name="manager1",
    scores_file_path="./config/finalScores.json",
    log_file_path=os.path.join(log_file_path, "scores_log.txt")
)

scores_manager_for_log = ScoresManager(
    name="managerLog",
    scores_file_path="./config/forestScores.json",
    log_file_path=os.path.join(log_file_path, "scores_log_aerolog.txt")
)

scores_manager_for_netdata = ScoresManager(
    name="managerNetdata",
    scores_file_path="./config/aerologScores.json",
    log_file_path=os.path.join(log_file_path, "scores_log_random_forest.txt")
)
