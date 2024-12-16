# alert_data.py
# -*- coding: utf-8 -*-

class AlertData:
    """告警数据类，用于封装和处理单条告警数据"""
    
    def __init__(self, data_item: dict):
        # 基本信息
        self.timestamp = data_item.get('@timestamp', '')
        self.msg = data_item.get('msg', '')
        self.priority = data_item.get('priority', 0)
        
        # 网络信息
        self.src_addr = data_item.get('src_addr', '')
        self.dst_addr = data_item.get('dst_addr', '')
        self.src_ap = data_item.get('src_ap', '')
        self.dst_ap = data_item.get('dst_ap', '')
        self.eth_src = data_item.get('eth_src', '')
        self.eth_dst = data_item.get('eth_dst', '')
        
        # 协议信息
        self.proto = data_item.get('proto', '')
        self.service = data_item.get('service', '')
        
        # 攻击相关
        self.action = data_item.get('action', '')
        self.attack_type = data_item.get('attack_type', {}).get('[message]', '')
        
        # 其他信息
        self.rule = data_item.get('rule', '')
        self.sid = data_item.get('sid', 0)
        self.gid = data_item.get('gid', 0)
        
        # 添加 dir 字段
        self.dir = data_item.get('dir', '')
        # 添加 eth_len 字段
        self.eth_len = data_item.get('eth_len', 0)

    def __str__(self):
        """返回告警数据的字符串表示"""
        return (f"告警信息: {self.msg}\n"
                f"源地址: {self.src_addr} ({self.eth_src})\n"
                f"目标地址: {self.dst_addr} ({self.eth_dst})\n"
                f"协议: {self.proto}\n"
                f"优先级: {self.priority}")

    def get_risk_info(self):
        """获取风险相关信息"""
        return {
            'msg': self.msg,
            'src_addr': self.src_addr,
            'eth_src': self.eth_src,
            'timestamp': self.timestamp,
            'priority': self.priority
        } 

    def to_training_format(self):
        """将告警数据转换为训练格式"""
        return {
            "priority":self.priority,
            'msg': self.msg,
            'dir': self.dir,
            'attack_type': self.attack_type,
            'action': self.action,
            'eth_len': self.eth_len,
            'dst_ap': self.dst_ap,
            'eth_dst': self.eth_dst,
            'dst_addr': self.dst_addr,
            'src_addr': self.src_addr,
            'rule': self.rule
        }

    # def save_to_file(self, filepath='@forest_train'):
    #     """保存训练数据到文件"""
    #     training_data = self.to_training_format()
    #     try:
    #         with open(filepath, 'a', encoding='utf-8') as f:
    #             data_str = '\t'.join(str(v) for v in training_data.values())
    #             f.write(data_str + '\n')
    #         return True
    #     except Exception as e:
    #         print(f"保存训练数据时出错: {e}")
    #         return False