import pandas as pd
# 定义月份映射字典
month_mapping = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}
def load_BGL():


    # load data
    bgl_structured = pd.read_csv("messages.log_structured.csv")
    # 映射月份为数字
    bgl_structured['Month'] = bgl_structured['Month'].map(month_mapping)
    print(bgl_structured['Month'])
    # 添加当前年份
    from datetime import datetime
    current_year = datetime.now().year
    # 组合日期和时间字段为datetime对象
    bgl_structured['Timestamp'] = pd.to_datetime(
                bgl_structured.apply(lambda row: f"{current_year}-{int(row['Month']):02d}-{int(row['Day']):02d} {row['Time']}", axis=1))
    # calculate the time interval since the start time
    bgl_structured["seconds_since"] = (bgl_structured['Timestamp']-bgl_structured['Timestamp'][0]).dt.total_seconds().astype(int)
    print(bgl_structured)
    return bgl_structured
load_BGL()