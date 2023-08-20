import hashlib
import logging
import os
import ffmpeg


def async_stream(hls_url: str, file_list: list):
    logging.info("Thread %s: starting", hls_url)
    hash_object = hashlib.md5(hls_url.encode('utf-8'))
    file_name = hash_object.hexdigest() + '.mp4'
    full_path = os.path.join(os.path.dirname(__file__), "../output/", file_name)
    file_list.append(full_path)
    stream = ffmpeg.input(hls_url).output(full_path).global_args('-loglevel', 'quiet').global_args('-y')
    ffmpeg.run(stream)
    logging.info("Thread %s: finishing", hls_url)
    file_list.remove(full_path)