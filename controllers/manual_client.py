from enum import Enum
from utils.ui import UIConsole
from models.user import User
from utils.queue_producer import QueueProducer
import config
import utils.message_parser as parser
from utils.messages import Message, Status
from getpass import getpass

# class syntax
class OptionsMain(Enum):
    REGISTRO = 0
    LOGIN = 1
    SALIR = 2
    PROBAR_RPC = 3


class ManualClient:
    def __init__(self) -> None:
        self.ui = UIConsole()
        try:
            self.producer = QueueProducer(queue=config.queue_clientes)
        except:
            print("No fue posible establecer la conexion con el servidor de colas")
            exit(1)
    
    def menu(self):
        options = ["Registrarse", "Iniciar Sesión", "Salir"]
        selected = 0

        while selected != OptionsMain.SALIR.value:
            selected = self.ui.get_option_menu(options)
            
            if selected == OptionsMain.REGISTRO.value:
                self.registro_cliente()
            elif selected == OptionsMain.LOGIN.value:
                print("Login")



    def registro_cliente(self):
        usuario = User()
        usuario.name = input("Ingrese nombre del cliente: ")
        usuario.username = input("Ingrese nombre de usuario: ")
        usuario.password = getpass("Ingrese contraseña: ")

        message = parser.build_message(Message.REGISTRO, usuario.get_body())
        response = self.producer.call(message, time_limit=3)

        content = parser.read_response(response)
        status, body = parser.get_response_contents(content)

        if status == Status.OK.value:
            print(f"EXITO: { body }")
        else:
            print(f"ERROR: { body }")

        self.ui.wait()