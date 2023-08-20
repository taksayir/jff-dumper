import logging
from threading import Thread
from processor.file import report_file_size
from processor.post import get_posts
from processor.stream import async_stream
from dotenv import load_dotenv

load_dotenv()

PROFILE_ID = os.getenv('PROFILE_ID')
USER_HASH = os.getenv('USER_HASH')


file_list = []
logging.getLogger().setLevel(logging.INFO)

posts = get_posts(PROFILE_ID, USER_HASH, 0)
print(posts)
# threads = list()
# screen_threads = list()
# for each in posts:
#     hls_url = each['playlist']['540p']
#     x = Thread(target = async_stream, args = (hls_url, file_list))
#     threads.append(x)
#     x.start()

# x = Thread(target = report_file_size, args = (file_list, ))
# screen_threads.append(x)
# x.start()

# for index, thread in enumerate(threads):
#     thread.join()

# screen_threads.remove(x)