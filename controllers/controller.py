from models.user import User
from controllers.api import API
from utils.queue_consumer import QueueConsumer
import config
import utils.message_parser as parser
from utils.messages import Message, Status

class Controller:
    def __init__(self) -> None:
        self.api = API()
        try:
            self.clientes_consumer = QueueConsumer(queue=config.queue_clientes, listener=self.entry_point_clientes)
        except:
            print("No se pudo crear la conexion al servidor de colas")
            exit(1)


    def entry_point_clientes(self, ch, method, props, body):
        print("[C] Mensaje recibido")

        message = parser.read_message(body)
        if not parser.is_okay(message):
            return parser.build_response(
                Status.ERROR,
                "Metodo no conocido"   
            )
        
        subject, body = parser.get_request_contents(message)

        print(subject)
        print(body)

        if subject == Message.REGISTRO.value:
           return self.registrar_usuario(body)  


    def registrar_usuario(self, body: dict) -> bool:
        if self.api.registrar_usuario(body):
            return parser.build_response(
                Status.OK,
                "Usuario registrado"
            )
        else:
            return parser.build_response(
                Status.ERROR,
                "No se pudo registrar el usuario"
            )
    
    def start_consuming(self):
        self.clientes_consumer.start_consuming()