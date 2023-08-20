import os
import curses
import sys

from dotenv import load_dotenv
from processor.file import get_temp_file_path
from processor.helper import load_json_from_file, save_json_to_file
from processor.post import get_posts
from processor.stream import execute_stream

def main(argv):
    load_dotenv()
    PROFILE_ID = os.getenv('PROFILE_ID')
    USER_HASH = os.getenv('USER_HASH')
    HIGHER_RESOLUTION_ONLY = os.getenv('HIGHER_RESOLUTION_ONLY') == 'true'
    PREFERED_RESOLUTION = os.getenv('PREFERED_RESOLUTION')


    cached_post_path = get_temp_file_path(PROFILE_ID, 'posts.json')
    if os.path.exists(cached_post_path):
        posts = load_json_from_file(cached_post_path)
    else:
        posts = get_posts(PROFILE_ID, USER_HASH)
        save_json_to_file(posts, cached_post_path)

    execute_stream(posts)


    # screen_threads.remove(x)

if __name__ == "__main__":
    main(sys.argv[1:])
