import json
import os
import re

def save_json_to_file(json_data, file_name):
    with open(file_name, 'w') as outfile:
        json.dump(json_data, outfile, indent=4, sort_keys=True)

def load_json_from_file(file_name):
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