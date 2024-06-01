import base64
import os
import re
import json
from datetime import datetime
import requests

from bs4 import BeautifulSoup
from lxml import etree
from processor.helper import get_closest_resolution, second_to_duration
from processor.screen import draw_post_crawler, init_stdsrc

api_url = 'https://justfor.fans/ajax/getPosts.php?Type=One&UserID={userid}&PosterID={posterid}&StartAt={seq}&Page=Profile&UserHash4={hash}&SplitTest=0'
# api_url = 'https://justfor.fans/ajax/getPosts.php?UserID={userid}&Type=All&StartAt={seq}&Source=Home&UserHash4={hash}'
preferred_resolution = int(os.getenv('PREFERRED_RESOLUTION', '720'))

def parse_playlist(text):
    playlists_obj = "{" + text[text.find('{')+1:text.rfind('}')] + "}"
    playlists = json.loads(playlists_obj)
    return playlists

def parse_meta(text):
    quoted_params = re.findall('"([^"]*)"', text)[0]
    query_params = quoted_params.split("?")[1].split("&")
    data_dict = {}
    for item in query_params:
        key, value = item.split('=')
        data_dict[key] = value

    return {
        "post_id": data_dict['PostID'],
        "poster_name": data_dict['PosterName']
    }

def encode_post_id(post_id):
    parsed_post_id = int(post_id)
    number_bytes = parsed_post_id.to_bytes((parsed_post_id.bit_length() + 7) // 8, byteorder='big')
    alphanumeric_string = base64.b64encode(number_bytes).decode('utf-8')
    return alphanumeric_string

def get_page_posts(userid, user_hash, seq, poster_id):
    url = api_url.format(userid=userid, hash=user_hash, seq=seq, posterid=poster_id)
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.content, features="lxml")
    dom = etree.HTML(str(soup))
    posts = dom.xpath("/html/body/div[contains(@class, 'jffPostClass')]")

    parsed_posts = []
    for each in posts:
        playlist_els = each.xpath(".//div[@class='videoBlock']/a/@onclick")
        if len(playlist_els) == 0:
            continue
        playlist_raw = playlist_els[0]
        playlist = parse_playlist(playlist_raw)

        timestamp_els = each.xpath(".//div[@class='mbsc-card-subtitle']/text()")
        if len(timestamp_els) == 0:
            continue
        timestamp = timestamp_els[0].strip()

        text = "".join(each.xpath(".//div[@class='fr-view']//text()")).strip()
        
        meta_els = each.xpath(".//ul[contains(@class, 'postMenu')]/li/@onclick")
        if len(meta_els) == 0:
            continue
        meta_raw = meta_els[0]
        meta = parse_meta(meta_raw)

        duration_els = each.xpath(".//div[@class='post-video-runtime']/text()")
        if len(duration_els) == 0:
            continue
        duration_raw = duration_els[0].strip()
        duration_hours = int((re.findall(r"(\d+) hour", duration_raw) or ["0"]).pop())
        duration_minutes = int((re.findall(r"(\d+) minute", duration_raw) or ["0"]).pop())
        duration_seconds = int((re.findall(r"(\d+) second", duration_raw) or ["0"]).pop())
        total_seconds = duration_hours * 3600 + duration_minutes * 60 + duration_seconds

        [selected_resolution, url] = get_closest_resolution(playlist, preferred_resolution=preferred_resolution)

        try:
            timestamp_str = datetime.strptime(timestamp, "%B %d, %Y, %I:%M %p").isoformat()
        except Exception as e:
            timestamp_str = 'NA'
            print(f"Failed to parse timestamp: {timestamp}")
            print(e)
        
        parsed_posts.append({
            "id": meta['post_id'],
            "poster_name": meta['poster_name'],
            "text": text,
            "resolution": selected_resolution,
            "url": url,
            "duration": second_to_duration(total_seconds),
            "timestamp": timestamp_str
        })
    
    parsed_posts.sort(key=lambda x: x['timestamp'], reverse=True)

    return (parsed_posts, len(posts))

def get_posts(userid, user_hash, poster_id):
    stdscr = init_stdsrc()
    posts = []

    has_more = True
    seq = 0
    while has_more:
        [new_parsed_posts, new_posts_count] = get_page_posts(userid, user_hash, seq, poster_id)
        if new_posts_count == 0:
            has_more = False
        posts.extend(new_parsed_posts)
        seq += new_posts_count
        draw_post_crawler(stdscr, total_parsed_posts=seq, total_posts=len(posts))
        

    
    return posts