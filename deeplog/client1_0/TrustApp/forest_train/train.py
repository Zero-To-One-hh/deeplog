import csv
import logging
import pickle
from datetime import datetime

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from tqdm import tqdm

# 配置日志
log_filename = f'training_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

labeled_file = 'labeled_data.txt'

X = []
y = []

# 记录开始时间
logger.info(f"训练开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 读取数据
with open(labeled_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter='\t')
    headers = next(reader)
    label_index = len(headers) - 1
    feature_names = headers[:label_index]
    data_rows = list(reader)

# 分离特征与标签
for row in tqdm(data_rows, desc="Processing rows", ncols=100):
    y.append(int(row[label_index]))
    X.append(row[:label_index])

# 简单特征编码函数
def is_float(val):
    try:
        float(val)
        return True
    except:
        return False

encoders = []
X_encoded = []

# 特征编码
for col_idx in tqdm(range(len(feature_names)), desc="Encoding features", ncols=100):
    column_values = [row[col_idx] for row in X]
    if all(is_float(v) for v in column_values):
        encoded_col = list(map(float, column_values))
        encoders.append(None)
    else:
        unique_vals = list(set(column_values))
        val_to_int = {v: i for i, v in enumerate(unique_vals)}
        encoded_col = [val_to_int[v] for v in column_values]
        encoders.append(val_to_int)

    if len(X_encoded) == 0:
        X_encoded = [[val] for val in encoded_col]
    else:
        for i, val in enumerate(encoded_col):
            X_encoded[i].append(val)

X = X_encoded

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 训练alarmForest模型
logger.info("开始训练alarmForest模型...")
rf_clf = RandomForestClassifier(n_estimators=100, random_state=42)
rf_clf.fit(X_train, y_train)

# 训练DESTree模型
logger.info("开始训练DESTree模型...")
dt_clf = DecisionTreeClassifier(random_state=42)
dt_clf.fit(X_train, y_train)

# alarmForest预测和评估
logger.info("alarmForest模型评估结果:")
rf_pred = rf_clf.predict(X_test)
logger.info(f"准确率: {accuracy_score(y_test, rf_pred)}")
logger.info("分类报告:\n" + classification_report(y_test, rf_pred))

# DESTree预测和评估
logger.info("DESTree模型评估结果:")
dt_pred = dt_clf.predict(X_test)
logger.info(f"准确率: {accuracy_score(y_test, dt_pred)}")
logger.info("分类报告:\n" + classification_report(y_test, dt_pred))

# 保存模型
with open('random_forest_model.pkl', 'wb') as f:
    pickle.dump((rf_clf, encoders, feature_names), f)

with open('decision_tree_model.pkl', 'wb') as f:
    pickle.dump((dt_clf, encoders, feature_names), f)

logger.info("模型已保存为: random_forest_model.pkl 和 decision_tree_model.pkl")
logger.info(f"训练结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
