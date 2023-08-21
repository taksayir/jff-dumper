import curses
from datetime import datetime
import os
import time
from spinners import Spinners

from processor.file import get_full_path, get_size
from processor.helper import display_string, get_relative_time, load_json_from_file

def init_stdsrc():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(False)
    if curses.has_colors():
        curses.start_color()
    return stdscr

def draw_post_crawler(stdscr, total_parsed_posts, total_posts):
    stdscr.addstr(0, 0, "Loading posts...")
    stdscr.addstr(2, 0, f"Parsed posts: {total_parsed_posts}")
    stdscr.addstr(3, 0, f"Total posts: {total_posts}")
    stdscr.refresh()

def draw_post_stream(download_status):
    stdscr = init_stdsrc()
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Downloading...")

        current_row = 2

        # Completed
        stdscr.addstr(current_row, 0, f"Completed: {len(download_status['completed'])}")
        current_row += 1
        completed_posts = []
        for post in download_status['completed'][0:5]:
            meta_path = get_full_path(post, "json")
            metadata = load_json_from_file(meta_path)
            full_path = get_full_path(post, "mp4")
            file_name = full_path.split(os.sep)[-1]
            file_size = get_size(full_path)
            completed_ago = get_relative_time(metadata['completed_at'])
            final_string = "\t".join([
                display_string(file_name, 50),
                display_string(metadata['resolution'], 10),
                display_string(metadata['duration'], 15),
                display_string(completed_ago, 15)
            ])
            completed_posts.append({
                "completed_at": metadata['completed_at'],
                "display_text": final_string
            })
        completed_posts.sort(key=lambda x: x['completed_at'], reverse=True)
        for post in completed_posts[0:3]:
            stdscr.addstr(current_row, 2, "✓ " + final_string)
            current_row += 1

        # In progress
        current_row += 1
        stdscr.addstr(current_row, 0, f"In progress: {len(download_status['in_progress'])}")
        current_row += 1
        for post in download_status['in_progress']:
            full_path = get_full_path(post, "mp4")
            file_size = get_size(full_path)
            file_name = full_path.split(os.sep)[-1]
            final_string = "\t".join([
                display_string(file_name, 50),
                display_string(post['resolution'], 10),
                display_string(post['duration'], 15),
                display_string(file_size, 15)
            ])
            progress_icon = Spinners.arc.value['frames'][int(time.time() * 10) % len(Spinners.arc.value['frames'])]
            stdscr.addstr(current_row, 2, progress_icon + " " + final_string)
            current_row += 1

        # Pending
        current_row += 1
        stdscr.addstr(current_row, 0, f"Pending: {len(download_status['pending'])}")
        
        stdscr.refresh()
        time.sleep(0.1)