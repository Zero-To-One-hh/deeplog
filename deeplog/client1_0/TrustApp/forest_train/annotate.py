import csv
import random

input_file = './output.txt'
output_file = 'labeled_data.txt'

with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-8', newline='') as f_out:
    reader = csv.reader(f_in, delimiter='\t')
    writer = csv.writer(f_out, delimiter='\t')
    
    headers = next(reader)  # 原始数据的表头
    # 在标注后的文件中增加一列risk_label
    headers.append('risk_label')
    writer.writerow(headers)
    
    for row in reader:
        # row顺序对应: priority, msg, dir, attack_type, action, eth_len, dst_ap, eth_dst, dst_addr, src_addr, rule
        priority = int(row[0])
        msg = row[1]

        # 标注逻辑：如果priority >= 3或msg中包含"告警"
        if (priority >= 4 or '攻击' in msg):
            # 满足条件时，有75%的概率标注为1，25%的概率标注为0
            risk_label = 1 if random.random() < 0.9456 else 0
        else:
            risk_label = 0

        new_row = row + [risk_label]
        writer.writerow(new_row)

print("标注完成，结果已写入:", output_file)
