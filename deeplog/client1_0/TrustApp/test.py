# -*- coding: utf-8 -*-
import os
import subprocess

# 文件夹路径
folderPath = r"C:\Users\DELL\Desktop\aerolog\client1_0\deeplog2024_06_15"

# 打开文件夹
if os.path.isdir(folderPath):
    if os.name == 'nt':  # Windows
        os.startfile(folderPath)
    elif os.name == 'posix':  # Linux / macOS
        subprocess.run(['xdg-open', folderPath])
