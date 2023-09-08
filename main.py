import os
import sys

from dotenv import load_dotenv
from processor.file import get_temp_file_path
from processor.helper import load_json_from_file, save_json_to_file
from processor.post import get_posts
from processor.stream import execute_stream, prepare_stream

def main(argv):
    load_dotenv()
    profile_id = os.getenv('PROFILE_ID')
    user_hash = os.getenv('USER_HASH')


    cached_post_path = get_temp_file_path(profile_id, 'posts.json')
    if os.path.exists(cached_post_path):
        posts = load_json_from_file(cached_post_path)
    else:
        posts = get_posts(profile_id, user_hash)
        save_json_to_file(posts, cached_post_path)
    
    # posts = get_posts(profile_id, user_hash)
    prepare_stream(posts)
    execute_stream(posts)


if __name__ == "__main__":
    main(sys.argv[1:])
