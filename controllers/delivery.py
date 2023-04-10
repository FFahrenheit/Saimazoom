import config
from utils.work_queue_consumer import WorkQueueConsumer
from utils.work_queue_producer import WorkQueueProducer
from utils.ui import UIConsole
import utils.message_parser as parser
from utils.messages import Message
from random import randint, random
from models.order import Order
import time 
import threading

class Delivery:
        # Constructor de la clase Delivery, se inicializan los parámetros básicos para la entrega
    def __init__(self, t_min=config.wait_delivery_min, t_max=config.wait_delivery_max, success_rate=config.p_entrega) -> None:
        """
        Constructor de la clase Delivery que inicializa los parámetros básicos para la entrega.

        Parámetros:
        - t_min (int): tiempo mínimo de espera para la entrega (por defecto, config.wait_delivery_min).
        - t_max (int): tiempo máximo de espera para la entrega (por defecto, config.wait_delivery_max).
        - success_rate (float): tasa de éxito para la entrega (por defecto, config.p_entrega).

        Devuelve:
        - None
        """
        self.t_min = t_min
        self.t_max = t_max
        self.success_rate = success_rate
        self.ui = UIConsole()
        self.to_be_canceled = []
        try:
        # Se crea un consumidor y productor de colas para recibir y enviar mensajes de repartidores
            self.consumer = WorkQueueConsumer(queue=config.queue_repartidores,listener=self.entry_point)  
            self.producer = WorkQueueProducer(queue=config.queue_respuesta_repartidores)
        except:
            print("No se pudo crear la conexion al servidor de colas")
            exit(1)

    def entry_point(self, channel, method, props, body):
        """
        Método que se encarga de recibir y procesar los mensajes de los repartidores.

        Parámetros:
        - channel: canal por el cual se recibió el mensaje.
        - method: método de envío del mensaje.
        - props: propiedades del mensaje recibido.
        - body: cuerpo del mensaje recibido.

        Devuelve:
        - None
        """
        print("[C] Mensaje recibido")

        message = parser.read_message(body)
        if not parser.is_okay(message):
            print("Metodo no conocido")
            return
        
        subject, body = parser.get_request_contents(message)
        print(f"\t{subject=}\n\t{body=}")

        # Routing para entrega de pedido    
        if subject == Message.DELIVER_ORDER.value:
           return self.entregar_pedido(body)
        else:
            print("Metodo no implementado")
        
    def entregar_pedido(self, body):
        """
        Método que se encarga de entregar un pedido específico.

        Parámetros:
        - body (dict): información del pedido a entregar.

        Devuelve:
        - None
        """
        # Se crea una instancia de la clase Order y se carga la información del pedido recibido en el objeto
        order = Order()
        order.from_dict(body)
        # Se genera un tiempo de espera aleatorio dentro del rango establecido en la configuración
        wait_time= randint(self.t_min, self.t_max)
        # Se establece una cantidad fija de iteraciones para la barra de progreso y se calcula el tiempo de espera por iteración
        iterations = 100
        step_delay = wait_time/iterations
        # Se define un mensaje para la barra de progreso y se establece una bandera para cancelar la entrega
        message = f"Entregando pedido #{order.id}"
        cancelled = False
        # Avisar que se está entregando
        self.producer.call(
            parser.build_message(
                Message.ON_DELIVER,
                order.get_body()
            )
        )
        # Se itera el número de veces definido, actualizando la barra de progreso y esperando el tiempo calculado para cada iteración
        for i in range(iterations):
            # Si el ID del pedido se encuentra en la lista de cancelaciones, se establece la bandera de cancelación y se sale del ciclo
            if order.id in self.to_be_canceled:
                cancelled = True
                break
            self.ui.progress_bar(i, iterations, prefix=message, length=40)
            time.sleep(step_delay)

        # Se borra la barra de progreso
        self.ui.clear()
        # Se determina si la entrega fue exitosa o no, tomando en cuenta la tasa de éxito configurada y si se canceló el pedido
        success = random() <= self.success_rate and not cancelled

        # Si la entrega fue exitosa, se envía un mensaje con el estado "pedido entregado"
        if success:
            status = Message.ORDER_DELIVERED
            print(f"Pedido #{order.id} entregado :)")
        # Si no fue exitosa, se envía un mensaje con el estado "pedido perdido" o "pedido cancelado", según corresponda
        else:
            if cancelled:
                status = Message.ORDER_CANCELED
            else:
                status = Message.ORDER_LOST
            print(f"Pedido #{order.id} no entregado :( - Cancelado = {cancelled}")

        # Se llama al método call del objeto producer, que envía un mensaje a la cola correspondiente con el estado del pedido y su información
        self.producer.call(
            parser.build_message(
                status,
                order.get_body()
            )
        )

    
    def entry_point_priority(self, channel, method, props, body):
        """
        Procesa los mensajes recibidos en la cola de repartidores (fanout).

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
            print("Mensaje incorrecto")
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
    
    
    def listen_cancels(self):
        """
        Crea un consumidor de la cola de repartidores y escucha los mensajes en dicha cola.

        Args:
            None.

        Returns:
            None.
        """
        # Se crea un consumidor de la cola de repartidores y se especifica el método que procesará los mensajes
        cancel_worker = WorkQueueConsumer(queue=config.queue_repartidores, listener=self.entry_point_priority, fanout=True)
        # Se inicia la escucha de mensajes en la cola
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
    