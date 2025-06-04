from typing import List
class User:
    def __init__(self, uid : int| str, name: str):
        if isinstance(uid, str):
            uid = int(uid)
        self.uid = uid
        self.name = name

class Comment:
    def __init__(self,rpid:int,oid:int,user:User,text:str) -> None:
        self.text = text
        self.author = user
        self.children:List[Comment] = []
        self.rpid = rpid
        self.oid = oid
    
    def to_json(self):
        return {
            'text': self.text,
            'author': {
                'uid': self.author.uid,
                'name': self.author.name
            },
            'count': len(self.children),
            'children': [child.to_json() for child in self.children],
            'rpid': self.rpid,
            'oid': self.oid
        }

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

