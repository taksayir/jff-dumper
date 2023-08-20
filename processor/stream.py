import hashlib
import os
import threading
import ffmpeg

from processor.file import get_full_meta_path, get_full_video_path
from processor.helper import ensure_dir, get_closest_resolution, load_json_from_file, save_json_to_file
from processor.screen import draw_post_stream

download_status = {
    "completed": [],
    "in_progress": [],
    "pending": []
}

sema = threading.Semaphore(value=10)

def execute_stream(posts: list):
    threads = list()
    for post in posts:
        post_thread = threading.Thread(target = async_stream, args = (post, ))
        threads.append(post_thread)
        post_thread.start()

    report_thread = threading.Thread(target = draw_post_stream, args = (download_status, ), daemon=True)
    report_thread.start()

    for index, post_thread in enumerate(threads):
        post_thread.join()


def read_or_init_meta(post, meta_path):
    if os.path.exists(meta_path):
        metadata = load_json_from_file(meta_path)
        return metadata

    metadata = {
        'text': post['text'],
        'model': post['poster_name'],
        'timestamp': post['timestamp'],
        'id': post['id_raw'],
        'playlist': post['playlist'],
        'status': 'downloading'
    }
    save_json_to_file(metadata, meta_path)
    return metadata


def async_stream(post):
    full_path = get_full_video_path(post)
    full_meta_path = get_full_meta_path(post)
    download_status['pending'].append(post)

    sema.acquire()
    ensure_dir(full_path)

    metadata = read_or_init_meta(post, full_meta_path)
    is_done = metadata['status'] == 'done'

    download_status['pending'].remove(post)
    download_status['in_progress'].append(post)

    if not is_done:
        hls_url = get_closest_resolution(post, preferred_resolution=1080, higher_only=True)
        stream = ffmpeg.input(hls_url).output(full_path).global_args('-loglevel', 'quiet').global_args('-y')
        ffmpeg.run(stream)

        metadata['status'] = 'done'
        save_json_to_file(metadata, full_meta_path)

    download_status['in_progress'].remove(post)
    download_status['completed'].append(post)

    sema.release()