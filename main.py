import logging
from threading import Thread
import threading
from processor.file import report_file_size
from processor.helper import load_json_from_file, save_json_to_file
from processor.post import get_posts
from processor.stream import async_stream, execute_stream
from dotenv import load_dotenv
import os

load_dotenv()

PROFILE_ID = os.getenv('PROFILE_ID')
USER_HASH = os.getenv('USER_HASH')


logging.getLogger().setLevel(logging.INFO)

# posts = get_posts(PROFILE_ID, USER_HASH)
# save_json_to_file(posts, 'posts.json')

posts = load_json_from_file('posts.json')
execute_stream(posts)


# screen_threads.remove(x)