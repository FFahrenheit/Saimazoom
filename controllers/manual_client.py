from enum import Enum
from utils.ui import UIConsole
from models.user import User
from models.order import Order
from utils.rpc_queue_producer import QueueProducer
import config
import utils.message_parser as parser
from utils.messages import Message, Status
from getpass import getpass
from random import randint
import threading

# class syntax
class OptionsMain(Enum):
    LOGIN = 0
    REGISTRO = 1
    SALIR = 2

class OptionsLogged(Enum):
    HACER_PEDIDO = 0
    VER_PEDIDOS = 1
    DETALLES_PEDIDOS = 2
    CANCELAR_PEDIDOS = 3
    CERRAR_SESION = 4
class OptionsOrder(Enum):
    CONTINUAR_PEDIDO = 0
    TERMINAR_PEDIDO = 1
    CANCELAR_PEDIDO = 2

class ManualClient:
    def __init__(self) -> None:
        self.ui = UIConsole()
        try:
            self.producer = QueueProducer(queue=config.queue_clientes)
        except:
            print("No fue posible establecer la conexion con el servidor de colas")
            exit(1)
    
    def menu(self):    
        options = ["Iniciar Sesión", "Registrarse", "Salir"]
        selected = 0

        while selected != OptionsMain.SALIR.value:
            selected = self.ui.get_option_menu(options)
            
            if selected == OptionsMain.REGISTRO.value:
                self.registro_cliente()
            elif selected == OptionsMain.LOGIN.value:
                if self.login():
                    self.menu_logged()
    
    def menu_logged(self):
        options = ["Hacer pedido", "Ver pedidos", "Detalles de pedidos", "Cancelar pedidos", "Cerrar sesion"]
        selected = 0

        while selected != OptionsLogged.CERRAR_SESION.value:
            selected = self.ui.get_option_menu(
                options, 
                f"Hola {self.user.name}, seleccione una opcion del menu:"
            )

            if selected == OptionsLogged.HACER_PEDIDO.value:
                self.hacer_pedido()
            elif selected == OptionsLogged.VER_PEDIDOS.value:
                self.ver_pedidos()
            elif selected == OptionsLogged.CANCELAR_PEDIDOS.value:
                self.cancelar_pedido()
            elif selected == OptionsLogged.DETALLES_PEDIDOS.value:
                self.detalles_pedidos()
    
    def cancelar_pedido(self):
        messagge = parser.build_message(Message.VIEW_ORDERS, {"client": self.user.username}) 
        self.ui.wait_queue()

        response = self.producer.call(messagge)
        # En este punto ya tenemos respuesta
        response_object = parser.process_response(response)         #Respuesta parseada

        if response_object.status == Status.OK.value:
            print("Ordenes: ")
            orders = response_object.body.get("orders", [])
            if len(orders) == 0:
                self.ui.wait("No hay ordenes registradas")

            else:
                options = [f"Orden #{orden['id']} - {orden['status']}" for orden in orders]
                selected = self.ui.get_option_menu(
                    options=options,
                    prompt="Seleccione la orden que desea cancelar: "
                )

                order_id = orders[selected].get('id', None)
                messagge = parser.build_message(Message.CANCEL_ORDER, {"order_id": order_id}) 

                self.async_wait(messagge)
        else:
            self.ui.wait("No se pudieron obtener los datos de la orden")

    def detalles_pedidos(self):
        messagge = parser.build_message(Message.VIEW_ORDERS, {"client": self.user.username}) 
        self.ui.wait_queue()

        response = self.producer.call(messagge)
        # En este punto ya tenemos respuesta
        response_object = parser.process_response(response)         #Respuesta parseada

        if response_object.status == Status.OK.value:
            print("Ordenes: ")
            orders = response_object.body.get("orders", [])
            if len(orders) == 0:
                print("No hay ordenes registradas")
            else:
                options = [f"Orden #{orden['id']} - {orden['status']}" for orden in orders]
                selected = self.ui.get_option_menu(
                    options=options,
                    prompt="Seleccione una de las ordenes a continuacion"
                )

                order_id = orders[selected].get('id', 1)
                messagge = parser.build_message(Message.VIEW_ORDER, {"order_id": order_id}) 
                response = self.producer.call(messagge)
                # En este punto ya tenemos respuesta
                response_object = parser.process_response(response)         #Respuesta parseada

                if response_object.status == Status.OK.value:
                    order = response_object.body.get('order', {})
                    print(f"Orden #{order.get('id', 1)}")
                    print(f"Articulos: ")
                    articulos = order.get('description').split('\r')
                    [ print("\t* " + articulo) for articulo in articulos]
                    print(f"Eventos: ")
                    for evento in order.get('events'):
                        print(f"\t{evento.get('time', 'ND')}\t{evento.get('status', '---')}")
                    print(f"Total ${order.get('total', 0):.2f}€")

                else:
                    print("No se pudieron obtener los detalles de la orden")

        self.ui.wait()
            
    def ver_pedidos(self):
        messagge = parser.build_message(Message.VIEW_ORDERS, {"client": self.user.username}) 
        self.ui.wait_queue()

        response = self.producer.call(messagge)
        # En este punto ya tenemos respuesta
        response_object = parser.process_response(response)         #Respuesta parseada

        if response_object.status == Status.OK.value:
            print("Ordenes: ")
            orders = response_object.body.get("orders", [])
            if len(orders) == 0:
                print("No hay ordenes registradas")
            else:
                print("ID\tEstado\t\tTotal\tDescripcion")
                for order in orders:
                    order_object = Order()
                    order_object.from_dict(order)
                    description = order_object.description.replace('\r', ', ')
                    print(f"{order_object.id}\t{order_object.status}\t{order_object.total:.2f}€\t{description}")
        else:
            print(f"Error: {response_object.message}")

        self.ui.wait()
        

    def hacer_pedido(self):
        options=["Añadir Articulo", "Terminar pedido", "Cancelar pedido"]
        order = Order(client=self.user.username)
        listo = 0
        
        selected = 0
        total = 0
        articulos = []

        while selected == OptionsOrder.CONTINUAR_PEDIDO.value:
            articulo = input(f"Inserte articulo { len(articulos)+1 }: ")
            articulos.append(articulo)
            precio = randint(20, 5000) / 100
            total += precio

            while listo == 0:
                selected = self.ui.get_option_menu(
                    options, 
                    f"{ articulo } agregado\n\t+{precio:.2f}€\nTotal:\t{total:.2f}€"+
                    "\nSeleccione una opcion del menu:"
                )
                listo = 3
            if selected == OptionsOrder.TERMINAR_PEDIDO.value:
                listo = 1
            if selected == OptionsOrder.CANCELAR_PEDIDO.value:
                listo = 2
            if selected == OptionsOrder.CONTINUAR_PEDIDO.value:
                listo = 0
            
        if listo == 1:
            order.description = "\r".join(articulos)
            order.total = total
            message = parser.build_message(Message.CREATE_ORDER, order.get_request_body())
            self.async_wait(message)
        if listo == 2:
            print("Pedido abortado")
            self.ui.wait()


    def login(self):
        payload = dict()
        payload['username'] = input("Nombre de usuario: ")
        payload['password'] = getpass("Contraseña: ")

        message = parser.build_message(Message.LOGIN, payload)
        self.ui.wait_queue()
        
        response = self.producer.call(message)
        response = parser.process_response(response)

        if response.status == Status.OK.value:
            status = True        
            self.user = User(from_dict=response.body)
            print(f"Exito: {response.message}")
        else:
            status = False
            print(f"Error: {response.message}")

        self.ui.wait()
        return status


    def registro_cliente(self):
        usuario = User()
        usuario.name = input("Ingrese nombre del cliente: ")
        usuario.username = input("Ingrese nombre de usuario: ")
        usuario.password = getpass("Ingrese contraseña: ")

        message = parser.build_message(Message.REGISTRO, usuario.get_body())
        self.async_wait(message)

    def async_wait(self, message):
        wait = threading.Thread(target=self.async_call, args=(message,))
        wait.daemon = True
        wait.start()
        self.ui.wait("Datos enviados para validar, presione enter para continuar...")

    def async_call(self, message):
        producer = QueueProducer(queue=config.queue_clientes)
        
        response = producer.call(message)
        response = parser.process_response(response)

        if response.status == Status.OK.value:
            self.ui.notify(f"EXITO: { response.message }")
        else:
            self.ui.notify(f"ERROR: { response.message }")
