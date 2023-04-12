from utils.work_queue_consumer import WorkQueueConsumer
from utils.work_queue_producer import WorkQueueProducer
import config
import utils.message_parser as parser
from utils.messages import Message
from models.order import Order
from random import randint, random
from utils.ui import UIConsole
import time 
import threading


"""
Preguntar ... 
1. Cuando el controlador recibe pedido solo contesta con pedido OK y el cliente es libre?
1.1 El estado buscando existe? aunque sea instantaneo? 
2. Se queda bloqueando esperando al Robot?
2.1 Como terminar la funcion si esta esperando?
3. O continua? 
"""
class Robot:
    def __init__(self, t_min=config.wait_robot_min, t_max=config.wait_robot_max, success_rate=config.p_almacen, allow_clear=True) -> None:
        """
        Constructor de la clase Robot que inicializa los parámetros básicos para la entrega.

        Parámetros:
        - t_min (int): tiempo mínimo de espera para la busqueda (por defecto, config.wait_robot_min).
        - t_max (int): tiempo máximo de espera para la busqueda (por defecto, config.wait_robot_max).
        - success_rate (float): tasa de éxito para la busqueda (por defecto, config.p_almacen).

        Devuelve:
        - None
        """
        self.t_min = t_min
        self.t_max = t_max
        self.success_rate = success_rate
        self.ui = UIConsole(allow_clear=allow_clear)
        self.to_be_canceled = []
        try:
        # Se crea un consumidor y productor de colas para recibir y enviar mensajes de robots
            self.consumer = WorkQueueConsumer(queue=config.queue_robots, listener=self.entry_point)
            self.producer = WorkQueueProducer(queue=config.queue_respuesta_robots)
        except:
            print("No se pudo crear la conexion al servidor de colas")
            exit(1)

    def entry_point_priority(self, channel, method, props, body):
        """
        Procesa los mensajes recibidos en la cola de robots (fanout).

        Lee el mensaje recibido y verifica si es correcto, luego obtiene el asunto y el cuerpo del mensaje.
        Si el asunto del mensaje es CANCEL_ORDER se agrega el id del pedido a la lista de pedidos a cancelar.
        Si el asunto del mensaje es CLEAR_CANCELATION se remueve el id del pedido de la lista de pedidos a cancelar.
        Si el asunto del mensaje no es válido, se lanza una excepción.

        Args:
            channel: canal de RabbitMQ.
            method: método de RabbitMQ.
            props: propiedades del mensaje.
            body: cuerpo del mensaje.

        Returns:
            None.
        """
        print("[C] Mensaje recibido - Entry point cancelados")


        # Se lee el mensaje recibido y se comprueba si es correcto
        message = parser.read_message(body)
        if not parser.is_okay(message):
            print("Metodo no conocido")
            return
           
        # Se obtiene el asunto y el cuerpo del mensaje
        subject, body = parser.get_request_contents(message)

        print(f"\t{subject=}\n\t{body=}")

        # Si el asunto del mensaje es CANCEL_ORDER se agrega el id del pedido a la lista de pedidos a cancelar
        if subject == Message.CANCEL_ORDER.value:
            order_id = body.get('order_id', None)
            if order_id is not None:
                self.to_be_canceled.append(order_id)
            else:
                print("Mensaje de cancelacion no recibido correctamente")
         # Si el asunto del mensaje es CLEAR_CANCELATION se remueve el id del pedido de la lista de pedidos a cancelar
        elif subject == Message.CLEAR_CANCELATION.value:
            order_id = body.get('order_id', None)
            if order_id is not None and order_id in self.to_be_canceled:
                self.to_be_canceled.remove(order_id)
        else:
            raise Exception("Mensaje enviado a cola para cancelar, no es necesario cancelar, saltando...")
        
        print("IDs a cancelar: " + str(self.to_be_canceled))
        
    def entry_point(self, channel, method, props, body):
        """
        Método que se encarga de recibir y procesar los mensajes de los robots.

        Parámetros:
        - channel: canal por el cual se recibió el mensaje.
        - method: método de envío del mensaje.
        - props: propiedades del mensaje recibido.
        - body: cuerpo del mensaje recibido.

        Devuelve:
        - None
        """
        print("[C] Mensaje recibido - Entry point")


        # Leemos y validamos el mensaje
        message = parser.read_message(body)
        if not parser.is_okay(message):
            print("Metodo no conocido")
            return
           
        subject, body = parser.get_request_contents(message)

        print(f"\t{subject=}\n\t{body=}")

        # Routing para buscar articulos
        if subject == Message.SEARCH_ORDER.value:
           self.buscar_pedido(body)
        else:
            print("Metodo no es para robot")
    
    def buscar_pedido(self, body: dict):
        """Método que se encarga de buscar los articulos de un pedido y colocarlos en la zona
        para recolección

        Args:
            body (dict): Informacion del pedido
        """
        # Hacemos el parsing de la orden
        order = Order()
        order.from_dict(body)

        # Obtenemos los articulos en el pedido
        articles = order.description.split("\r")
        cancelled = False

        # Buscamos los articulos uno a uno
        for index, article in enumerate(articles):
            message = f"Buscando { article } (articulo {index+1}) para el pedido #{order.id}\nBuscando: "
            # Tiempo de espera aleatorio
            wait_time = randint(self.t_min, self.t_max)
            # Funciones para el retraso e iteraciones de progress bar
            iterations = 100
            step_delay = wait_time/iterations

            print(article)
            
            # Se imprime la barra de progreso
            for i in range(iterations+1):
                self.ui.progress_bar(i, iterations, prefix=message, length=40)
                # Si el ID del pedido se encuentra en la lista de cancelaciones, se establece la bandera de cancelación y se sale del ciclo
                if order.id in self.to_be_canceled:
                    cancelled = True
                    break
                time.sleep(step_delay)
            
            success = random() <= self.success_rate 
            if not success or cancelled:
                break

        # self.ui.clear()
        # Se verifica que el pedido fue exitoso y no fue cancelado o no encontrado
        # Se retorna un estado dependiendo de esto
        if success and not cancelled:
            print(f"Pedido #{order.id} encontrado :)")
            status = Message.ORDER_FOUND
        else:
            print(f"Pedido #{order.id} no encontrado :( Cancelado = {cancelled}")
            if cancelled:
                status = Message.ORDER_CANCELED
            else:
                status = Message.ORDER_NOT_FOUND

        # Se avisa al controlador
        self.producer.call(
            parser.build_message(
                status,
                order.get_body()
                )
            )

    def listen_cancels(self):
        """
        Crea un consumidor de la cola de robots y escucha los mensajes en dicha cola.

        Args:
            None.

        Returns:
            None.
        """
        # Se crea un consumidor de la cola de robots y se especifica el método que procesará los mensajes
        cancel_worker = WorkQueueConsumer(queue=config.queue_robots, listener=self.entry_point_priority, fanout=True)
        cancel_worker.start_consuming()

    def start_consuming(self):
        """
        Crea un hilo para escuchar la cola de cancelaciones y escucha los mensajes en la cola principal.

        Args:
            None.

        Returns:
            None.
        """
        # Se crea un hilo para escuchar la cola de cancelaciones
        cancel_thread = threading.Thread(target=self.listen_cancels)
        cancel_thread.daemon = True
        cancel_thread.start()
        # Se inicia la escucha de mensajes en la cola principal
        self.consumer.start_consuming()