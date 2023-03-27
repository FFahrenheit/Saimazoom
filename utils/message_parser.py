import json
from utils.messages import Message, Status


SUBJECT_STR = "subject"
BODY_STR = "body"
STATUS_STR = "status"

def build_message(subject: Message, body:dict) -> str:
    request = {
        SUBJECT_STR: subject.value,
        BODY_STR: json.dumps(body)
    }
    return json.dumps(request)

def read_message(message: str) -> dict:
    return json.loads(message)

def build_response(status: Status, body:str) -> str:
    request = {
        STATUS_STR: status.value,
        BODY_STR: body
    }
    return json.dumps(request)

def is_okay(message: dict):
    return SUBJECT_STR in message 

def read_response(message):
    message = message.decode()
    return json.loads(message)

def get_request_contents(message):
    return get_subject(message), get_body(message)

def get_response_contents(message):
    return get_status(message), get_body(message)


def get_status(message: dict):
    return message.get(STATUS_STR, Status.ERROR.value)

def get_subject(message: dict) -> str:
    return message.get(SUBJECT_STR, "")

def get_body(message: dict) -> dict:
    return message.get(BODY_STR, {})

def is_response_okay(response):
    return response != None and response.get("status", "") == Status.OK.value

# Pruebas rapidas
# print(build_message(Message.LOGIN, "S"))
# print(read_message(build_message(Message.LOGIN, {"Hola": "123", "bcd":[123, 456]})))

 