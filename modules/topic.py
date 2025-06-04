from typing import Generator
import json

from utils.requests import requests_get
from models.item import Video

SEARCH_URL = "https://api.bilibili.com/x/web-interface/search/type"
class Topic:
    def __init__(self, name, keyword):
        self.name = name
        self.keyword = keyword
        self.videos = [video for video in self.fetch_videos()]

    def fetch_videos(self)->Generator[Video, None, None]:
        params = {
            'search_type': 'video',
            'keyword': self.keyword,
            'page': 1,
            'order': 'totalrank',
            'tids': 0
        }
        res = requests_get(SEARCH_URL, params=params)
        for item in res['data']['result']:
            video = Video()
            video.from_search_result(item)
            yield video

    def collect_comments(self):
        from modules.get_comments import get_all_comments
        for video in self.videos:
            comments = get_all_comments(video.avid)
            video.comments = comments
    def export_to_file(self):
        for video in self.videos:
            check_directory(f"output/{self.name}")
            sub_count = 0
            for comment in video.comments:
                sub_count += len(comment.children)
            with open(f"output/{self.name}/{video.bvid}.json", 'w', encoding='utf-8') as f:
                output = {
                    'name': self.name,
                    'video': video.to_json(),
                    'comments': [comment.to_json() for comment in video.comments],
                    'count': len(video.comments) + sub_count
                }
                json.dump(output, f, ensure_ascii=False, indent=4)

        
def check_directory(path):
    import os
    if not os.path.exists(path):
        os.makedirs(path)