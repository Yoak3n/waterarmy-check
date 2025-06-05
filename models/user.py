class User:
    def __init__(self, uid : int| str, name: str):
        if isinstance(uid, str):
            uid = int(uid)
        self.uid = uid
        self.name = name