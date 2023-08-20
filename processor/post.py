import base64
import re
import json
from datetime import datetime
import requests

from bs4 import BeautifulSoup
from lxml import etree

from processor.screen import draw_post_crawler, init_stdsrc

api_url = 'https://justfor.fans/ajax/getPosts.php?UserID={userid}&Type=All&StartAt={seq}&Source=Home&UserHash4={hash}'

def get_playlist(text):
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

def get_page_posts(userid, user_hash, seq):
    url = api_url.format(userid=userid, hash=user_hash, seq=seq)
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
        playlist = get_playlist(playlist_raw)

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

        parsed_posts.append({
            "id": encode_post_id(meta['post_id']),
            "id_raw": meta['post_id'],
            "poster_name": meta['poster_name'],
            "playlist": playlist,
            "text": text,
            "timestamp": datetime.strptime(timestamp, "%B %d, %Y, %I:%M %p").isoformat()
        })
    return parsed_posts

def get_posts(userid, user_hash):
    stdscr = init_stdsrc()
    posts = []

    has_more = True
    seq = 0
    while has_more:
        new_posts = get_page_posts(userid, user_hash, seq)
        if len(new_posts) == 0:
            has_more = False
        posts.extend(new_posts)
        seq = len(posts)
        draw_post_crawler(stdscr, seq, len(posts))
        

    
    return posts