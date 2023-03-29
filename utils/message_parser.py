import json
from utils.messages import Message, Status
from models.response import MessageResponse

SUBJECT_STR = "subject"
BODY_STR = "body"
STATUS_STR = "status"
MESSAGE_STR = "message"

def build_message(subject: Message, body:dict) -> str:
    request = {
        SUBJECT_STR: subject.value,
        BODY_STR: json.dumps(body)
    }
    return json.dumps(request)

def read_message(message: str) -> dict:
    message = message.decode()
    return json.loads(message)

def build_response(status: Status, message='', body={}) -> str:
    response = {
        STATUS_STR: status.value,
        MESSAGE_STR: message,
        BODY_STR: json.dumps(body)
    }
    return json.dumps(response)

def is_okay(message: dict):
    return SUBJECT_STR in message 

def process_response(message) -> MessageResponse:
    response = read_response(message)
    if STATUS_STR not in response:
        return MessageResponse(Status.MALFORMED.value)
    return MessageResponse(
        response.get(STATUS_STR),
        message=response.get(MESSAGE_STR, ''),
        body=json.loads(response.get(BODY_STR, {}))
    )

def read_response(message):
    message = message.decode()
    return json.loads(message)

def get_request_contents(message):
    return get_subject(message), get_body(message) 

def get_response_contents(message):
    return get_status(message), get_body(message)

def get_status(message: dict):
    return message.get(STATUS_STR, Status.ERROR.value) or Status.ERROR.value

def get_subject(message: dict) -> str:
    return message.get(SUBJECT_STR, "")

def get_message(message: dict) -> str:
    return message.get(MESSAGE_STR, "")

def get_body(message: dict) -> dict:
    return json.loads(message.get(BODY_STR, {}))

def is_response_okay(response):
    return response != None and response.get("status", "") == Status.OK.value

# Pruebas rapidas
# print(build_message(Message.LOGIN, "S"))
# print(read_message(build_message(Message.LOGIN, {"Hola": "123", "bcd":[123, 456]})))

