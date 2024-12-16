# -*- coding: utf-8 -*-
import csv

input_file = './output.txt'
keywords_file = 'keywords.txt'
output_file = 'labeled_data.txt'

keywords = []
with open(keywords_file, 'r', encoding='utf-8') as kf:
    for line in kf:
        keyword = line.strip()
        if keyword:
            keywords.append(keyword)

with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-8', newline='') as f_out:
    reader = csv.reader(f_in, delimiter='\t')
    writer = csv.writer(f_out, delimiter='\t')

    headers = next(reader)  
    headers.append('risk_label')
    writer.writerow(headers)

    for row in reader:
        msg = row[1]

        risk_label = 0
        for kw in keywords:
            if kw in msg:
                risk_label = 1
                break

        new_row = row + [risk_label]
        writer.writerow(new_row)

print("输出文件为:", output_file)
