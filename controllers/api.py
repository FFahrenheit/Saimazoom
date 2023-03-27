from controllers.database import Database
from models.user import User

class API:
    def __init__(self) -> None:
        self.db = Database()

    def registrar_usuario(self, body: dict) -> bool:
        usuario = User(from_str=body)

        return self.db.insert_record(f"INSERT INTO user(name, username, password) VALUES (?, ?, ?)", 
                                     (usuario.name, usuario.username, usuario.password))
    