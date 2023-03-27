from enum import Enum

class Message(Enum):
    REGISTRO = "RegistroCliente"
    LOGIN = "LoginCliente"


class Status(Enum):
    ERROR = "Error"
    OK = "Ok"