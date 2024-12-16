# convert_data.py
# -*- coding: utf-8 -*-
import json

from deeplog.client1_0.TrustApp.alert_data import AlertData


def convert_json_to_training_data(json_file='./data.json', output_file='./forest_train'):
    """
    将JSON数据转换为训练格式并保存
    """
    try:
        # 读取JSON文件
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 检查数据格式
        if not isinstance(data, dict) or 'data' not in data:
            print("数据格式错误：缺少'data'字段")
            return False
            
        # 清空输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            # 写入表头
            headers = ['priority','msg', 'dir', 'attack_type', 'action', 'eth_len',
                      'dst_ap', 'eth_dst', 'dst_addr', 'src_addr', 'rule']
            f.write('\t'.join(headers) + '\n')
        
        # 处理每条数据
        success_count = 0
        for item in data['data']:
            try:
                alert = AlertData(item)
                alert.save_to_file(output_file)
                success_count += 1
            except Exception as e:
                print(f"处理数据时出错: {e}")
                continue
        
        print(f"成功转换 {success_count} 条数据")
        return True
        
    except FileNotFoundError:
        print(f"找不到文件: {json_file}")
        return False
    except json.JSONDecodeError:
        print(f"JSON解析错误: {json_file}")
        return False
    except Exception as e:
        print(f"转换过程出错: {e}")
        return False

if __name__ == "__main__":
    # 运行转换程序
    convert_json_to_training_data() 