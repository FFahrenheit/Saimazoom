import json
from models.base_model import BaseModel

# Definimos la clase User que hereda de BaseModel
class User(BaseModel):
    # Definimos los atributos de la clase
    name : str
    username : str
    password : str

   # Definimos el constructor de la clase con valores por defecto y parámetros opcionales
    def __init__(self, name='', username='', password='', from_str=None, from_dict=None) -> None:
        # Si no se recibe un objeto from_str o from_dict, se inicializan los atributos con los valores recibidos
        if from_str is None and from_dict is None:
            self.name = name
            self.username = username
            self.password = password
        # Si se recibe un objeto from_str, se inicializan los atributos con los valores del objeto serializado
        elif from_str is not None:
            content = json.loads(from_str)
            self.name = content.get("name", "")
            self.username = content.get("username", "")
            self.password = content.get("password", "")
        # Si se recibe un objeto from_dict, se inicializan los atributos con los valores del diccionario
        elif from_dict is not None:
            self.name = from_dict.get("name", "")
            self.username = from_dict.get("username", "")
            self.password = from_dict.get("password", "") 