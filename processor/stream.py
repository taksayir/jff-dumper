from datetime import datetime
import os
import subprocess
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

user_agent ='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

sema = threading.Semaphore(value=5)
is_sequential = True

def execute_stream(posts: list):
    if is_sequential:
        for post in posts:
            async_stream(post, is_sequential)
        return
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

def download_video(post, user_agent, full_video_path, full_meta_path, metadata):
    if os.path.exists(full_video_path):
        os.remove(full_video_path)

    stream = (
        ffmpeg
        .input(post['url'], user_agent=user_agent)
        .output(full_video_path, vcodec='copy')
        .global_args('-loglevel', 'debug')
        .global_args('-y')
    )

    cmd = ffmpeg.compile(stream)
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for line in process.stdout:
            print(line, end='')  # Print each line as it comes
        process.stdout.close()
        process.wait()

        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd)
    except subprocess.CalledProcessError as ex:
        print(f"Error occurred: {ex}")
        raise ex

    metadata['status'] = 'done'
    metadata['completed_at'] = datetime.now().isoformat()
    save_json_to_file(metadata, full_meta_path)


def async_stream(post, is_sequential = False):
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
        if is_sequential:
            download_video(post, user_agent, full_video_path, full_meta_path, metadata)
        else:
            stream = ffmpeg.input(post['url'], user_agent=user_agent).output(full_video_path, vcodec='copy').global_args('-loglevel', 'debug').global_args('-y')
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