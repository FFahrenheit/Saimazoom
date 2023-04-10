from utils.rpc_queue_producer import QueueProducer
import config
import utils.message_parser as parser
from utils.messages import Message, Status
from models.user import User
import threading
from models.order import Order
from random import randint, random
import time
import os

class AutoClient:
    def __init__(self) -> None:
        #self.ui = UIConsole()
        try:
            # Se inicializa un objeto QueueProducer que se conecta a la cola de mensajes del servidor
            self.producer = QueueProducer(queue=config.queue_clientes)
        except:
            #si no se puede conectar al servidor sale del programa
            print("No fue posible establecer la conexion con el servidor de colas")
            exit(1)
    
    def inicio(self):
        # en esta seccion, intentara logear un usuario, si no es posible creara el usuario para los datos en cuestion(ver config.py)
        if self.login():
            print("Login correcto")
        else:
            self.reg_client()
            if self.login():
                pass
            else:
                print("ERROR")

        while True:
            #se inicia el proceso de pedidos
            self.hacer_pedido()   
            
            #se mostraran los pedidos en un bucle infinito para su constante actualizacion
            for i in range(config.create_frequency):
                time.sleep(1)
                os.system('cls' if os.name=='nt' else 'clear')
                self.ver_pedidos() 
        
    #funcion encargada para hacer pedidos
    def hacer_pedido(self):
        #se inicializan los diferentes objetos y variables
        order = Order(client = self.user.username)
        articulos = []
        total = 0
        
        #2 bucles que se encargan de realizar el numero de pedidos declarados en config.py
        for j in range(config.n_pedidos):
            for i in range(config.n_prods):
                articulo = f"{config.prod_name}_{j+1}_{i+1}"
                articulos.append(articulo)
                total += randint(20,5000) /100
            order.description = "\r".join(articulos)
            order.total = total
            # Se crea un mensaje para enviar el pedido a la cola del servidor
            message = parser.build_message(Message.CREATE_ORDER, order.get_request_body())
            self.async_wait(message)
            #se vacia el array para volver a procesar otra orden
            articulos.clear()
            print("Orden enviada....")
            time.sleep(1.5)

    def ver_pedidos(self):
        # Construye un mensaje que indica que se quieren ver los pedidos del cliente actual
        messagge = parser.build_message(Message.VIEW_ORDERS, {"client": self.user.username}) 
        # Envía el mensaje al servidor y espera su respuesta
        response = self.producer.call(messagge)
        # Procesa la respuesta obtenida y la guarda en una variable
        response_object = parser.process_response(response)         #Respuesta parseada
        
        # Si la respuesta indica que todo ha ido bien, muestra los pedidos
        if response_object.status == Status.OK.value:
            print("Ordenes: ")
            orders = response_object.body.get("orders", [])
            if len(orders) == 0:
                print("No hay ordenes registradas")
            else:
                print(f"{'ID':<5}{'Estado':<25}{'Total':<10}{'Descripcion'}")
                for order in orders:
                    order_object = Order()
                    order_object.from_dict(order)
                    description = order_object.description.replace('\r', ', ')
                    price = f"{order_object.total:.2f}€"
                    print(f"{order_object.id:<5}{order_object.status:<25}{price:<10}{description}")

                # Probabilidad de cancelar un pedido 
                should_cancel = random() < config.p_cancelar
                print(f"Should cancel: {should_cancel}")
                if should_cancel:
                    bottom_limit = 0 if len(orders) < 4 else len(orders) - 4
                    selected = randint(bottom_limit, len(orders) - 1)
                    order_id = orders[selected].get('id', None)
                    messagge = parser.build_message(Message.CANCEL_ORDER, {"order_id": order_id}) 
                    print(f"CANCELANDO PEDIDO #{order_id}...")
                    self.async_wait(messagge)
                    time.sleep(1.5)
        else:
            #si devuelve error, mostrara un mensaje de error
            print(f"Error: {response_object.message}")

        #tiempo de espera para su automatizacion
        #time.sleep(0.5)
        

    def login(self):
        # Construye un mensaje con las credenciales del cliente y lo envía al servidor
        payload = dict()
        payload['username'] = config.client_user
        payload['password'] = config.client_pswd
        message = parser.build_message(Message.LOGIN, payload)
        response = self.producer.call(message)
        # Procesa la respuesta obtenida y guarda el usuario en una variable si el login fue exitoso
        response = parser.process_response(response)

        if response.status == Status.OK.value:
            status = True
            self.user=User(from_dict=response.body)
            print(f"Exito: {response.message}")
        # Si el login falló, se guarda un estado de error y se muestra el mensaje de error
        else:
            status = False
            print(f"Error: {response.message}")
        #tiempo de espera para su automatizacion
        time.sleep(0.5)

        return status


    def reg_client(self):
        # Crea un nuevo objeto usuario con los datos de configuración y lo envía al servidor para registrarlo
        usuario = User()
        usuario.name = config.client_name    
        usuario.username = config.client_user
        usuario.password = config.client_pswd

        message = parser.build_message(Message.REGISTRO, usuario.get_body())
        self.async_wait(message)
        print("registrao")

    def async_wait(self, message):
        # Crea un hilo para enviar una solicitud asíncrona al servidor y esperar su respuesta
        wait = threading.Thread(target=self.async_call, args=(message,))
        wait.daemon = True
        wait.start()
        time.sleep(0.5)

    def async_call(self, message):
        # Envía una solicitud asíncrona al servidor y muestra un mensaje de éxito o error dependiendo de la respuesta
        producer = QueueProducer(queue=config.queue_clientes)        
        response = producer.call(message)
        response = parser.process_response(response)

        if response.status == Status.OK.value:
            print("OK")
        else:
            print("ERROR")