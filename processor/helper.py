import json
import os
import re
from typing import Dict

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
    cleaned_name = re.sub(r'[\\/:*?"<>|]', '_', name)
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
    if higher_only:
        resolution_keys = [x for x in resolution_keys if x >= preferred_resolution]

    if len(resolution_keys) == 0:
        max_resolution = max(key_mapper.keys())
        resolution_keys = [max_resolution]

    nearest_resolution_index = min(range(len(resolution_keys)), key=lambda i: abs(resolution_keys[i]-preferred_resolution))
    nearest_resolution = resolution_keys[nearest_resolution_index]
    return key_mapper[nearest_resolution]