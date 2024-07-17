import pandas as pd
import logging

# 配置日志记录
logging.basicConfig(filename='comparison_log.log', level=logging.INFO, format='%(asctime)s - %(message)s')


def read_csv_content(file_path, max_lines=1751, encoding='utf-8'):
    df = pd.read_csv(file_path, encoding=encoding, nrows=max_lines)
    return df


def read_text_content(file_path, max_lines=1751, encoding='utf-8'):
    with open(file_path, 'r', encoding=encoding) as file:
        content = []
        for i in range(max_lines):
            try:
                content.append(next(file).strip())
            except StopIteration:
                break
    return content


def compare_files(file1_path, file2_path, max_lines=1000, encoding='utf-8'):
    df1 = read_csv_content(file1_path, max_lines, encoding)
    file2_lines = read_text_content(file2_path, max_lines, encoding)

    # 提取文件1中的EventId列中的数字
    df1['EventNumber'] = df1['EventId'].str.extract(r'E(\d+)')

    # 文件2中的数字
    file2_numbers = [line for line in file2_lines]

    min_length = min(len(df1), len(file2_numbers))

    is_corresponding = True
    for i in range(min_length):
        if df1['EventNumber'].iloc[i] != file2_numbers[i]:
            logging.info(
                f"行 {i + 1} 不匹配: 文件1的E后数字是 {df1['EventNumber'].iloc[i]}, 文件2的数字是 {file2_numbers[i]}")
            is_corresponding = False

    if is_corresponding:
        print("文件1和文件2中的E后的数字是对应关系")
    else:
        print("文件1和文件2中的E后的数字不是对应关系，详情请查看comparison_log.log")


# 指定文件路径
file1_path = 'messages.log_structured.csv'
file2_path = 'event_ids.txt'

# 比较文件前1000行
compare_files(file1_path, file2_path, max_lines=1751, encoding='utf-8')
