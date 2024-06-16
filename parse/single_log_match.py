import re
import pandas as pd
from tqdm import tqdm

para = {"bgl": "bgl/bgl2_100k", "template": "bgl/templates.csv", "structured_file": "bgl/single_log.csv"}


def match(log, template_file):
    # match event to the template
    template = pd.read_csv(template_file)

    event = []
    event2id = {}

    # 建立对应关系event_template->id
    for i in range(template.shape[0]):
        event_id = template.iloc[i, template.columns.get_loc("EventId")]
        event_template = template.iloc[i, template.columns.get_loc("EventTemplate")]
        event2id[event_template] = event_id
        event.append(event_template)

    log_event = " ".join(log[9:])
    for i, item in enumerate(event):
        if re.match(r'' + item, log_event) and re.match(r'' + item, log_event).span()[1] == len(log_event):
            return event2id[item]
    return 'error'


def structure(log, event_id, output_file):
    # extract label and time
    label = log[0]
    time = log[4]

    new_data = pd.DataFrame(columns=["label", "time", "event_id"])
    new_data = new_data.append({"label": label, "time": time, "event_id": event_id}, ignore_index=True)
    # Remove logs which do not match the template (very few logs ...)
    new_data = new_data[(-new_data["event_id"].isin(["error"]))]

    # Append to existing CSV file
    try:
        existing_data = pd.read_csv(output_file)
        updated_data = pd.concat([existing_data, new_data])
    except FileNotFoundError:
        updated_data = new_data

    updated_data.to_csv(output_file, index=None)


def process_log(S, template_file=para["template"], output_file=para["structured_file"]):
    # Split the log string into columns
    log = S.strip().split()

    # Match and structure the log
    event_id = match(log, template_file)
    structure(log, event_id, output_file)


if __name__ == "__main__":
    # Example log string S
    S = "- 1117989506 2005.06.05 R30-M0-N1-C:J05-U01 1025-06-15-09.38.26.892021 R3-M0-N1-C:J05-U01 RAS KERNEL INFO generating core.1587"

    # Process the log string S
    process_log(S, para["template"], para["structured_file"])  #todo 更改模板文件
