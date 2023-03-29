from utils.messages import Message, Status

class MessageResponse:
    status: Status
    message: str
    body: dict

    def __init__(self, status: Status, message='', body={}) -> None:
        self.status = status
        self.message = message
        self.body = body