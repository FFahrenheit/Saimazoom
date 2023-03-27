import json

class User:
    name : str
    username : str
    password : str

    def __init__(self, name='', username='', password='', from_str = None) -> None:
        if from_str is None:
            self.name = name
            self.username = username
            self.password = password
        else:
            content = json.loads(from_str)
            self.name = content.get("name", "")
            self.username = content.get("username", "")
            self.password = content.get("password", "")


    def get_body(self) -> str:
        return {
            "name": self.name, 
            "username": self.username,
            "password": self.password,
        }