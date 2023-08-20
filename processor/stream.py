import hashlib
import os
import threading
import ffmpeg

from processor.file import report_file_size
from processor.helper import clean_file_name, ensure_dir

file_list = []
sema = threading.Semaphore(value=5)

def execute_stream(posts: list):
    threads = list()
    screen_threads = list()
    for post in posts:
        x = threading.Thread(target = async_stream, args = (post, ))
        threads.append(x)
        x.start()

    report_thread = threading.Thread(target = report_file_size, args = (file_list, ), daemon=True)
    report_thread.start()

    for index, thread in enumerate(threads):
        thread.join()


def async_stream(post):
    sema.acquire()

    file_name = f"{post['timestamp']} {post['id']} {post['text']}.mp4"
    directory = os.path.join(os.path.dirname(__file__), "../output/", post['poster_name'])
    full_path = os.path.join(directory, clean_file_name(file_name))
    ensure_dir(full_path)

    hls_url = post['playlist']['540p']
    file_list.append(full_path)
    stream = ffmpeg.input(hls_url).output(full_path).global_args('-loglevel', 'quiet').global_args('-y')
    ffmpeg.run(stream)
    file_list.remove(full_path)
    
    sema.release()