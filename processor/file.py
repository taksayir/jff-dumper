import os
import time

def get_size(path):
    if not os.path.isfile(path):
        return "n/a"
    size = os.path.getsize(path)
    if size < 1024:
        return f"{size} bytes"
    elif size < pow(1024,2):
        return f"{round(size/1024, 2)} KB"
    elif size < pow(1024,3):
        return f"{round(size/(pow(1024,2)), 2)} MB"
    elif size < pow(1024,4):
        return f"{round(size/(pow(1024,3)), 2)} GB"


def report_file_size(file_list: list):
    while True:
        final = "\r"
        for each in file_list:
            final += str(get_size(each).rjust(10)) + "\t"
        print(final, end="")
        time.sleep(1)
