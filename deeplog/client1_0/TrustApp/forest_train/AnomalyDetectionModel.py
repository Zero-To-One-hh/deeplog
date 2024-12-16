# -*- coding: utf-8 -*-
import pickle


class AnomalyDetectionModel:
    def __init__(self, model_file='random_forest_model.pkl'):
        self.model_file = model_file
        self.clf = None
        self.encoders = None
        self.feature_names = None
        self.load_model()

    def load_model(self):
        """加载训练好的模型"""
        try:
            with open(self.model_file, 'rb') as f:
                self.clf, self.encoders, self.feature_names = pickle.load(f)
            print("模型加载成功！")
        except FileNotFoundError:
            print(f"模型文件 {self.model_file} 未找到！")
            raise
        except Exception as e:
            print(f"加载模型时出错: {e}")
            raise

    def encode_data(self, data):
        """将数据编码为训练时的特征格式"""
        encoded_data = []

        for col_idx in range(len(self.feature_names)):
            column_values = [row[col_idx] for row in data]

            if self.encoders[col_idx] is None:  # 数值型
                encoded_col = list(map(float, column_values))
            else:  # 字符串型进行映射
                encoded_col = [self.encoders[col_idx].get(val, -1) for val in column_values]  # 处理未知值

            encoded_data.append(encoded_col)

        # 转置数据，适合模型输入
        return list(zip(*encoded_data))

    def predict(self, new_data):
        """对新数据进行预测"""
        X_new = self.encode_data(new_data)
        y_pred = self.clf.predict(X_new)

        return y_pred

    def evaluate_model(self, test_data, test_labels):
        """评估模型"""
        X_test = self.encode_data(test_data)
        y_pred = self.clf.predict(X_test)

        from sklearn.metrics import classification_report, accuracy_score
        print("Accuracy:", accuracy_score(test_labels, y_pred))
        print("Classification Report:")
        print(classification_report(test_labels, y_pred))


# 测试代码
if __name__ == "__main__":
    # 加载模型实例
    model = AnomalyDetectionModel('random_forest_model.pkl')

    # 示例数据，格式与训练数据相同
    new_data = [
        ['3', 'DoS攻击警报检测到RST flood攻击', 'C2S', 'DoS攻击警报', 'allow', '42', '172.17.0.2:0',
         '02:42:AC:11:00:02', '172.17.0.2', '172.17.0.3', '116:434:1'],
        ['1', '正常流量', 'C2S', '正常', 'allow', '60', '172.17.0.5:0', '02:42:AC:11:00:03', '172.17.0.5', '172.17.0.6',
         '116:434:2']
    ]

    # 预测
    predictions = model.predict(new_data)
    for i, pred in enumerate(predictions):
        print(f"数据: {new_data[i]}, 预测结果: {pred}")

