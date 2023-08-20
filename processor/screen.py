import curses
import time

from processor.file import get_full_video_path, get_size

def init_stdsrc():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(False)
    if curses.has_colors():
        curses.start_color()
    return stdscr

def draw_post_crawler(stdscr, page, total_posts):
    stdscr.addstr(0, 0, "Loading posts...")
    stdscr.addstr(1, 0, f"Total posts: {total_posts}")
    stdscr.refresh()

def draw_post_stream(download_status):
    stdscr = init_stdsrc()
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Downloading posts...")
        stdscr.addstr(1, 0, f"Completed: {len(download_status['completed'])}")
        stdscr.addstr(2, 0, f"In progress: {len(download_status['in_progress'])}")
        stdscr.addstr(3, 0, f"Pending: {len(download_status['pending'])}")
        for index, each in enumerate(download_status['in_progress']):
            file_size = get_size(get_full_video_path(each)).rjust(10)
            display_text = each['text'][0:50] if len(each['text']) > 50 else each['text'][0:47] + "..."
            date = each['timestamp'].split('T')[0]
            stdscr.addstr(4 + index, 0, f"{each['id_raw']}   \t   {date}  \t  {display_text}  \t  {file_size}")
        stdscr.refresh()
        time.sleep(1)