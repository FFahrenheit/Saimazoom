import json

class User:
    name : str
    username : str
    password : str

    def __init__(self, name='', username='', password='', from_str = None, from_dict = None) -> None:
        if from_str is None and from_dict is None:
            self.name = name
            self.username = username
            self.password = password
        elif from_str is not None:
            content = json.loads(from_str)
            self.name = content.get("name", "")
            self.username = content.get("username", "")
            self.password = content.get("password", "")
        elif from_dict is not None:
            self.name = from_dict.get("name", "")
            self.username = from_dict.get("username", "")
            self.password = from_dict.get("password", "")


    def get_body(self) -> dict:
        return vars(self)