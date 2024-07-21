import re
import pandas as pd
from tqdm import tqdm

para = {"template": "G:/item/deeplog/logparser/result/messages.log_templates.csv", "structured_file": "./test.csv"}
"""
后续可以将转义后的模板单独存放在一个文件中，这样可以提升一些速度
"""

# 读取日志条
def data_log(log):
    datas = []
    lines = log
    for line in tqdm(lines):
        row = line.strip("\n").split()
        t = [item.lstrip(" ") for item in row]
        datas.append(t)
    return datas


#转义特殊字符(除*号外)
def escape_special_characters(pattern):
    special_characters = ".*^$+?{}[]()|\\"
    escaped_pattern = ""
    for idx,char in enumerate(pattern):
        if char in special_characters:
            if char=='*':
                if idx>0 and pattern[idx-1]=='<' and pattern[idx+1]=='>':
                    escaped_pattern += char
                    continue
            escaped_pattern += "\\" + char
        else:
            escaped_pattern += char
    return escaped_pattern
def convert_template_to_regex(template):
    # template = template.replace('<*>', '.*')
    template = escape_special_characters(template)

    template = template.replace('<*>', '\S+')

    return template


# 读取模板并匹配
def match(BGL):
    template_df = pd.read_csv(para["template"])

    event = []
    event2id = {}

    for i in range(template_df.shape[0]):
        event_id = template_df.iloc[i, template_df.columns.get_loc("EventId")]
        event_template = template_df.iloc[i, template_df.columns.get_loc("EventTemplate")]
        # print(event_template)
        regex_template = convert_template_to_regex(event_template)
        # print(regex_template)
        event2id[regex_template] = event_id
        event.append(regex_template)

    error_log = []
    eventmap = []
    print("Matching...")
    for log in tqdm(BGL):
        log_event = " ".join(log[5:]).lstrip(' ')
        matched = False
        for item in event:
            # print(item)
            if re.fullmatch(r'' + item, log_event):
                eventmap.append(event2id[item])
                matched = True
                break
        if not matched:
            eventmap.append('error')
            # print(eventmap)
            error_log.append(log_event)
    return eventmap


def structure(BGL, eventmap):
    month = []
    day = []
    time = []
    for log in tqdm(BGL):
        month.append(log[0])  # 提取时间戳
        day.append(log[1])  # 提取时间戳
        time.append(log[2])  # 提取时间戳

    BGL_structured = pd.DataFrame(columns=["Month", "Day", "Time", "EventId"])
    BGL_structured["Month"] = month
    BGL_structured["Day"] = day
    BGL_structured["Time"] = time
    BGL_structured["EventId"] = eventmap
    # Remove logs which do not match the template
    # BGL_structured = BGL_structured[BGL_structured["EventId"] != "error"]
    BGL_structured.to_csv(para["structured_file"], index=None)


def process_data(log):
    logs = [
        log
    ]
    BGL = data_log(logs)
    eventId = match(BGL)
    print(eventId)
    structure(BGL, eventId)
    return int(re.findall(r'\d+', eventId[0])[0])