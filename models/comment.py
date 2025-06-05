from typing import List
from .user import User

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
