from typing import List
from .user import User
from .comment import Comment

class Video:
    def __init__(self):
        self.avid = 0
        self.bvid = ''
        self.title = ''
        self.description = ''
        self.owner = User(0, '')
        self.comments: List[Comment] = []

    def from_search_result(self, data: dict):
        self.bvid = data['bvid']
        self.avid = data['aid']
        self.title = data['title']
        self.description = data['description']
        self.owner = User(data['mid'], data['author'])

    def to_json(self):
        return {
            'avid': self.avid,
            'bvid': self.bvid,
            'title': self.title,
            'description': self.description,
            'owner': {
                'uid': self.owner.uid,
                'name': self.owner.name
            }
        }