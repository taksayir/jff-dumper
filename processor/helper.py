from datetime import datetime
import json
import os
import re
from cleantext import clean

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
    cleaned_name = clean(name, no_emoji=True, lower=False, no_line_breaks=True)
    cleaned_name = re.sub(r'[\\/:*?"<>|]', '_', cleaned_name).rstrip()
    cleaned_name = cleaned_name.replace("\n", " ")
    cleaned_name = cleaned_name.replace('"', " ")
    cleaned_extension = re.sub(r'[\\/:*?"<>|]', '_', extension)
    max_name_length = max_length - len(cleaned_extension) - 1 
    cleaned_name = cleaned_name[:max_name_length]
    return f"{cleaned_name}.{cleaned_extension}"

def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def get_closest_resolution(playlist, preferred_resolution: int):
    key_int_mapper = {}
    for each in playlist:
        number_only = re.sub("[^0-9]", "", each)
        if number_only == "":
            continue
        key_int_mapper[int(number_only)] = each
    
    all_resolutions = list(key_int_mapper.keys())
    filtered_resolutions = [x for x in all_resolutions if x >= preferred_resolution]

    if len(filtered_resolutions) > 0:
        selected_resolution_index = min(range(len(filtered_resolutions)), key=lambda i: abs(filtered_resolutions[i]-preferred_resolution))
        selected_resolution = filtered_resolutions[selected_resolution_index]
    else:
        selected_resolution = max(all_resolutions)

    selected_original_resolution = key_int_mapper[selected_resolution]

    return (selected_original_resolution, playlist[selected_original_resolution])

def truncate_string(input_string, max_length):
    truncate_suffix = "..."
    if len(input_string) <= max_length:
        return input_string
    string_length = max_length - len(truncate_suffix)
    return input_string[:string_length] + truncate_suffix

def display_string(input_string, max_length, is_left_aligned=False):
    truncated = truncate_string(input_string, max_length)
    if is_left_aligned:
        return truncated.ljust(max_length)
    return truncated.rjust(max_length)

def second_to_duration(seconds):
    months = int(seconds / (30 * 24 * 3600))
    days = int(seconds / (24 * 3600))
    hours = int(seconds / 3600)
    minutes = int(seconds / 60)
    seconds = int(seconds % 60)

    duration_array = []
    months_string = f"{months}M" if months > 0 else None
    days_string = f"{days}d" if days > 0 else None
    hours_string = f"{hours}h" if hours > 0 else None
    minutes_string = f"{minutes}m" if minutes > 0 else None
    seconds_string = f"{seconds}s" if seconds > 0 else None
    duration_array = [months_string, days_string, hours_string, minutes_string, seconds_string]
    duration_array = [x for x in duration_array if x is not None]

    return "".join(duration_array[0:2])


def get_relative_time(timestamp):
    now = datetime.now()
    post_time = datetime.fromisoformat(timestamp)
    diff = now - post_time
    return second_to_duration(diff.total_seconds()) + " ago"