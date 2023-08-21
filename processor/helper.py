import json
import os
import re
from typing import Dict

def deEmojify(text):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'',text)

def save_json_to_file(json_data, file_name):
    ensure_dir(file_name)
    with open(file_name, 'w') as outfile:
        json.dump(json_data, outfile, indent=4, sort_keys=True)

def load_json_from_file(file_name):
    ensure_dir(file_name)
    with open(file_name) as json_file:
        data = json.load(json_file)
    return data

def clean_file_name(input_name, max_length=255):
    name, extension = input_name.rsplit('.', 1)
    cleaned_name = deEmojify(re.sub(r'[\\/:*?"<>|]', '_', name)).rstrip()
    cleaned_name = re.sub(r'\n', ' ', cleaned_name)
    cleaned_extension = re.sub(r'[\\/:*?"<>|]', '_', extension)
    max_name_length = max_length - len(cleaned_extension) - 1 
    cleaned_name = cleaned_name[:max_name_length]
    return f"{cleaned_name}.{cleaned_extension}"

def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_closest_resolution(post: Dict, preferred_resolution: int, higher_only: bool = False):
    key_mapper = {}
    for each in post['playlist']:
        number_only = re.sub("[^0-9]", "", each)
        if number_only == "":
            continue
        key_mapper[int(number_only)] = post['playlist'][each]
    
    resolution_keys = key_mapper.keys()
    prefered_resolution_keys = [x for x in resolution_keys if x >= preferred_resolution]

    if len(prefered_resolution_keys) == 0:
        return key_mapper[max(resolution_keys)]

    nearest_resolution_index = min(range(len(prefered_resolution_keys)), key=lambda i: abs(prefered_resolution_keys[i]-preferred_resolution))
    nearest_resolution = prefered_resolution_keys[nearest_resolution_index]
    return key_mapper[nearest_resolution]

def truncate_string(input_string, max_length):
    truncate_suffix = "..."
    if len(input_string) <= max_length:
        return input_string
    string_length = max_length - len(truncate_suffix)
    return input_string[:string_length] + truncate_suffix