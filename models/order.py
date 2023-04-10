from models.base_model import BaseModel

#Definimos la clase Order, que hereda de BaseModel
class Order(BaseModel):
    # Definimos las propiedades de la orden con sus tipos de datos
    id: int
    status: str
    description: str
    total: float
    client: str

    # Constructor de la clase Order, que recibe argumentos para inicializar las propiedades de la orden
    def __init__(self, id=0, status="", description="", total=0, client="", from_dict=None) -> None:
        # Si se recibe un diccionario, se inicializan las propiedades a partir de él
        if from_dict != None:
            pass 
        
        # Inicializamos las propiedades con los argumentos recibidos
        self.id = id
        self.status = status
        self.description = description
        self.total = total
        self.client = client

    # Método que devuelve el cuerpo de una solicitud HTTP que se enviará para crear la orden
    def get_request_body(self):
        return {
            "client": self.client,
            "description": self.description,
            "total": self.total
        }