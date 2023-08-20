from bs4 import BeautifulSoup
import requests
from lxml import etree
import json

api_url = 'https://justfor.fans/ajax/getPosts.php?UserID={userid}&Type=All&StartAt={seq}&Source=Home&UserHash4={hash}'

def get_playlist(text):
    playlists_obj = "{" + text[text.find('{')+1:text.rfind('}')] + "}"
    playlists = json.loads(playlists_obj)
    return playlists

def get_posts(userid, hash, seq):
    url = api_url.format(userid=userid, hash=hash, seq=seq)
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.content)
    dom = etree.HTML(str(soup))
    posts = dom.xpath("/html/body/div[contains(@class, 'jffPostClass')]")
    
    parsed_posts = []
    for each in posts:
        playlist_raw = each.xpath(".//div[@class='videoBlock']/a/@onclick")[0]
        playlist = get_playlist(playlist_raw)
        text = "".join(each.xpath(".//div[@class='fr-view']//text()")).strip()
        parsed_posts.append({
            "playlist": playlist,
            "text": text
        })
    return parsed_posts