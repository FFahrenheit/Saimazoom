from utils.messages import Status
from models.base_model import BaseModel

"""
Formato base de respuesta de un mensaje
"""
class MessageResponse(BaseModel):
    status: Status     # Atributo que representa el estado de la respuesta
    message: str       # Atributo que representa el mensaje de la respuesta
    body: dict         # Atributo que representa el cuerpo de la respuesta

    def __init__(self, status: Status, message='', body={}) -> None:
        #Constructor de la clase MessageResponse.
        self.status = status
        self.message = message
        self.body = body