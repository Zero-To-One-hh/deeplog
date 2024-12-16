# -*- coding: utf-8 -*-
import threading
import time

from config import config
from database import save_scores
from logger import logger


def periodic_save_scores():
    save_interval = config.get('save_interval_seconds', 600)
    while True:
        time.sleep(save_interval)
        save_scores()
        logger.info("分数已定期保存。")

def start_background_tasks():
    save_thread = threading.Thread(target=periodic_save_scores, daemon=True)
    save_thread.start()
