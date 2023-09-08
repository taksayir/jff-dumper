from datetime import datetime
import os
import threading
import time
import ffmpeg

from processor.file import get_full_path
from processor.helper import ensure_dir, load_json_from_file, save_json_to_file
from processor.screen import draw_post_stream

download_status = {
    "completed": [],
    "in_progress": [],
    "pending": []
}

sema = threading.Semaphore(value=20)

def execute_stream(posts: list):
    threads = list()
    for post in posts:
        post_thread = threading.Thread(target = async_stream, args = (post, ), daemon=True)
        threads.append(post_thread)
        post_thread.start()
        time.sleep(0.01)

    report_thread = threading.Thread(target = draw_post_stream, args = (download_status, ), daemon=True)
    report_thread.start()

    for post_thread in threads:
        post_thread.join()


def read_or_init_meta(post, meta_path):
    if os.path.exists(meta_path):
        metadata = load_json_from_file(meta_path)
        return metadata

    metadata = post
    metadata['status'] = 'pending'
    metadata['completed_at'] = None
    save_json_to_file(metadata, meta_path)
    return metadata


def async_stream(post):
    full_video_path = get_full_path(post, "mp4")
    full_meta_path = get_full_path(post, "json")
    download_status['pending'].append(post)

    sema.acquire()

    metadata = read_or_init_meta(post, full_meta_path)

    download_status['pending'].remove(post)
    download_status['in_progress'].append(post)

    is_done = metadata['status'] == 'done'
    should_download = not is_done

    if should_download:
        stream = ffmpeg.input(post['url']).output(full_video_path, vcodec='copy').global_args('-loglevel', 'quiet').global_args('-y')
        if os.path.exists(full_video_path):
            os.remove(full_video_path)
        try:
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
        except ffmpeg.Error as ex:
            print('stdout:', ex.stdout.decode('utf8'))
            print('stderr:', ex.stderr.decode('utf8'))
            raise ex
        metadata['status'] = 'done'
        metadata['completed_at'] = datetime.now().isoformat()
        save_json_to_file(metadata, full_meta_path)

    download_status['in_progress'].remove(post)
    download_status['completed'].append(post)

    sema.release()

def prepare_stream(posts):
    for post in posts:
        full_path = get_full_path(post, "mp4")
        directory = ensure_dir(full_path)
    return directory