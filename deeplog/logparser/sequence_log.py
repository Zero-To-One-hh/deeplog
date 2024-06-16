import os
import pandas as pd
import numpy as np
para = {"window_size":0.5,"step_size":0.2,"structured_file":"./result/messages.log_structured.csv","Log_sequence":'./result/messages_sequence.csv'}

# 定义月份映射字典
month_mapping = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}
def load_Log():
    structured_file = para["structured_file"]
    # load data
    log_structured = pd.read_csv(structured_file)
    # 映射月份为数字
    log_structured['Month'] = log_structured['Month'].map(month_mapping)

    # 添加当前年份
    from datetime import datetime
    current_year = datetime.now().year
    # 组合日期和时间字段为datetime对象
    log_structured['Timestamp'] = pd.to_datetime(
                log_structured.apply(lambda row: f"{current_year}-{int(row['Month']):02d}-{int(row['Day']):02d} {row['Time']}", axis=1))
    # calculate the time interval since the start time
    log_structured["seconds_since"] = (log_structured['Timestamp']-log_structured['Timestamp'][0]).dt.total_seconds().astype(int)
    # print(bgl_structured)
    return log_structured


def log_sampling(log_structured):

    time_data,event_mapping_data = log_structured['seconds_since'].values,log_structured['EventId']
    log_size = len(time_data)
    # split into sliding window
    start_time = time_data[0]
    start_index = 0
    end_index = 0
    start_end_index_list = []
    # get the first start, end index, end time
    for cur_time in time_data:
        if cur_time < start_time + para["window_size"]*3600:
            end_index += 1
            end_time = cur_time
        else:
            start_end_pair = tuple((start_index,end_index))
            start_end_index_list.append(start_end_pair)
            break
    while end_index < log_size:
        start_time = start_time + para["step_size"]*3600
        end_time = end_time + para["step_size"]*3600
        for i in range(start_index,end_index):
            if time_data[i] < start_time:
                i+=1
            else:
                break
        for j in range(end_index, log_size):
            if time_data[j] < end_time:
                j+=1
            else:
                break
        start_index = i
        end_index = j
        start_end_pair = tuple((start_index, end_index))
        start_end_index_list.append(start_end_pair)
    # start_end_index_list is the  window divided by window_size and step_size, 
    # the front is the sequence number of the beginning of the window, 
    # and the end is the sequence number of the end of the window
    inst_number = len(start_end_index_list)
    print('there are %d instances (sliding windows) in this dataset'%inst_number)

    # get all the log indexs in each time window by ranging from start_index to end_index

    expanded_indexes_list=[[] for i in range(inst_number)]
    expanded_event_list=[[] for i in range(inst_number)]

    for i in range(inst_number):
        start_index = start_end_index_list[i][0]
        end_index = start_end_index_list[i][1]
        for l in range(start_index, end_index):
            expanded_indexes_list[i].append(l)
            expanded_event_list[i].append(event_mapping_data[l])
    #=============get labels and event count of each sliding window =========#

    # labels = []
    #
    # for j in range(inst_number):
    #     label = 0   #0 represent success, 1 represent failure
    #     for k in expanded_indexes_list[j]:
    #         # If one of the sequences is abnormal (1), the sequence is marked as abnormal
    #         if label_data[k]:
    #             label = 1
    #             continue
    #     labels.append(label)
    # assert inst_number == len(labels)
    # print("Among all instances, %d are anomalies"%sum(labels))

    Log_sequence = pd.DataFrame(columns=['sequence'])
    Log_sequence['sequence'] = expanded_event_list
    # BGL_sequence['label'] = labels
    Log_sequence.to_csv(para["Log_sequence"],index=None)

if __name__ == "__main__":
    log_structured = load_Log()
    log_sampling(log_structured)
