import json
from utils.messages import Message, Status
from models.response import MessageResponse

SUBJECT_STR = "subject"
BODY_STR = "body"
STATUS_STR = "status"
MESSAGE_STR = "message"

def build_message(subject: Message, body:dict) -> str:
    """
    Construye un mensaje a partir de un asunto y un cuerpo.
    
    Args:
        subject (Message): Asunto del mensaje.
        body (dict): Cuerpo del mensaje.
    
    Returns:
        str: Mensaje construido en formato JSON.
    """
    request = {
        SUBJECT_STR: subject.value,
        BODY_STR: json.dumps(body)
    }
    return json.dumps(request)


def read_message(message: str) -> dict:
    """
    Lee un mensaje y devuelve su contenido en forma de diccionario.
    
    Args:
        message (str): Mensaje en formato JSON.
    
    Returns:
        dict: Contenido del mensaje en forma de diccionario.
    """
    message = message.decode()
    return json.loads(message)


def build_response(status: Status, message='', body={}) -> str:
    """
    Construye una respuesta a partir de un estado, un mensaje y un cuerpo.
    
    Args:
        status (Status): Estado de la respuesta.
        message (str): Mensaje adicional.
        body (dict): Cuerpo de la respuesta.
    
    Returns:
        str: Respuesta construida en formato JSON.
    """
    response = {
        STATUS_STR: status.value,
        MESSAGE_STR: message,
        BODY_STR: json.dumps(body)
    }
    return json.dumps(response)


def is_okay(message: dict):
    """
    Comprueba si un mensaje tiene el formato correcto.
    
    Args:
        message (dict): Mensaje en formato JSON.
    
    Returns:
        bool: True si el mensaje tiene el formato correcto, False en caso contrario.
    """
    return SUBJECT_STR in message 


def process_response(message) -> MessageResponse:
    """
    Procesa una respuesta y devuelve su contenido en forma de objeto MessageResponse.
    
    Args:
        message: Mensaje en formato JSON.
    
    Returns:
        MessageResponse: Objeto MessageResponse creado a partir de la respuesta.
    """
    response = read_response(message)
    if STATUS_STR not in response:
        return MessageResponse(Status.MALFORMED.value)
    return MessageResponse(
        response.get(STATUS_STR),
        message=response.get(MESSAGE_STR, ''),
        body=json.loads(response.get(BODY_STR, {}))
    )


def read_response(message):
    """
    Lee una respuesta y devuelve su contenido en forma de diccionario.
    
    Args:
        message: Mensaje en formato JSON.
    
    Returns:
        dict: Contenido de la respuesta en forma de diccionario.
    """
    message = message.decode()
    return json.loads(message)


def get_request_contents(message):
    """
    Obtiene los contenidos de una petición.
    
    Args:
        message: Mensaje en formato JSON.
    
    Returns:
        Tuple[str, dict]: Tupla que contiene el asunto y el cuerpo de la petición.
    """
    return get_subject(message), get_body(message) 

def get_response_contents(message: str) -> tuple:
    """
    Obtiene el estado y cuerpo de una respuesta.

    Args:
        message (str): La respuesta en formato de cadena JSON.

    Returns:
        tuple: Una tupla que contiene el estado y el cuerpo de la respuesta.
    """
    return get_status(message), get_body(message)

def get_status(message: dict) -> str:
    """
    Obtiene el estado de un mensaje o respuesta.

    Args:
        message (dict): El mensaje o respuesta en formato de diccionario.

    Returns:
        str: El estado del mensaje o respuesta.
    """
    return message.get(STATUS_STR, Status.ERROR.value) or Status.ERROR.value

def get_subject(message: dict) -> str:
    """
    Obtiene el asunto de un mensaje.

    Args:
        message (dict): El mensaje en formato de diccionario.

    Returns:
        str: El asunto del mensaje.
    """
    return message.get(SUBJECT_STR, "")

def get_message(message: dict) -> str:
    """
    Obtiene el mensaje de una respuesta.

    Args:
        message (dict): La respuesta en formato de diccionario.

    Returns:
        str: El mensaje de la respuesta.
    """
    return message.get(MESSAGE_STR, "")

def get_body(message: dict) -> dict:
    """
    Obtiene el cuerpo de un mensaje o respuesta.

    Args:
        message (dict): El mensaje o respuesta en formato de diccionario.

    Returns:
        dict: El cuerpo del mensaje o respuesta.
    """
    return json.loads(message.get(BODY_STR, {}))

def is_response_okay(response) -> bool:
    """
    Comprueba si una respuesta tiene el estado correcto.

    Args:
        response (dict): La respuesta en formato de diccionario.
    Returns:
        bool: True si el estado de la respuesta es OK, False en caso contrario.
    """
    return response != None and response.get("status", "") == Status.OK.value
