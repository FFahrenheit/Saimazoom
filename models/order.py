from models.base_model import BaseModel

class Order(BaseModel):
    id: int
    status: str
    description: str
    total: float
    client: str

    def __init__(self, id=0, status="", description="", total=0, client="", from_dict=None) -> None:
        if from_dict != None:
            pass 

        self.id = id
        self.status = status
        self.description = description
        self.total = total
        self.client = client

    def get_request_body(self):
        return {
            "client": self.client,
            "description": self.description,
            "total": self.total
        }