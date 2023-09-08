import os
import time

from processor.helper import clean_file_name, ensure_dir

def get_size(path):
    human_str = 'n/a'
    if not os.path.isfile(path):
        return 0, human_str
    size = os.path.getsize(path)
    return size, convert_to_human_readable(size)

def convert_to_human_readable(size):
    if size < 1024:
        return f"{size} bytes"
    elif size < pow(1024,2):
        return f"{round(size/1024, 2)} KB"
    elif size < pow(1024,3):
        return f"{round(size/(pow(1024,2)), 2)} MB"
    elif size < pow(1024,4):
        return f"{round(size/(pow(1024,3)), 2)} GB"

def get_raw_file_name(post):
    date = post['timestamp'].split('T')[0]
    file_name = f"{date} {post['text']}"
    return file_name

def get_full_path(post, ext: str):
    file_name = get_raw_file_name(post)
    if '"' in file_name:
        print(f"WARNING: Newline in file name: {file_name}")
    directory = os.path.join(os.path.dirname(__file__), ".." , "output", post['poster_name'])
    full_path = os.path.join(directory, clean_file_name(f"{file_name}.{ext}"))
    return full_path

def get_temp_dir(profile_id):
    directory = os.path.join(os.path.dirname(__file__), ".." , "temp", profile_id)
    ensure_dir(directory)
    return directory

def get_temp_file_path(profile_id, file_name):
    directory = get_temp_dir(profile_id)
    full_path = os.path.join(directory, file_name)
    return full_path