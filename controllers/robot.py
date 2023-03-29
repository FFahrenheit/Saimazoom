from utils.work_queue_consumer import WorkQueueConsumer
from utils.work_queue_producer import WorkQueueProducer
import config
import utils.message_parser as parser
from utils.messages import Message, Status
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
    def __init__(self, t_min=config.wait_robot_min, t_max=config.wait_robot_max, success_rate=config.p_almacen) -> None:
        self.t_min = t_min
        self.t_max = t_max
        self.success_rate = success_rate
        self.ui = UIConsole()
        self.to_be_canceled = []
        try:
            self.consumer = WorkQueueConsumer(queue=config.queue_robots, listener=self.entry_point)
            self.producer = WorkQueueProducer(queue=config.queue_respuesta_robots)
        except:
            print("No se pudo crear la conexion al servidor de colas")
            exit(1)

    def entry_point_priority(self, channel, method, props, body):
        print("[C] Mensaje recibido - Entry point cancelados")

        message = parser.read_message(body)
        if not parser.is_okay(message):
            print("Metodo no conocido")
            return
           
        subject, body = parser.get_request_contents(message)

        print(f"\t{subject=}\n\t{body=}")

        if subject == Message.CANCEL_ORDER.value:
            order_id = body.get('order_id', None)
            if order_id is not None:
                self.to_be_canceled.append(order_id)
            else:
                print("Mensaje de cancelacion no recibido correctamente")
        elif subject == Message.CLEAR_CANCELATION.value:
            order_id = body.get('order_id', None)
            if order_id is not None and order_id in self.to_be_canceled:
                self.to_be_canceled.remove(order_id)
        else:
            raise Exception("Mensaje enviado a cola para cancelar, no es necesario cancelar, saltando...")
        
        print("IDs a cancelar: " + str(self.to_be_canceled))
        
    def entry_point(self, channel, method, props, body):
        print("[C] Mensaje recibido - Entry point")

        message = parser.read_message(body)
        if not parser.is_okay(message):
            print("Metodo no conocido")
            return
           
        subject, body = parser.get_request_contents(message)

        print(f"\t{subject=}\n\t{body=}")

        if subject == Message.SEARCH_ORDER.value:
           self.buscar_pedido(body)
        else:
            print("Metodo no es para robot")
    
    def buscar_pedido(self, body):
        order = Order()
        order.from_dict(body)

        articles = order.description.split("\r")
        cancelled = False

        for article in articles:
            message = f"Buscando { article } para el pedido #{order.id}\nBuscando: "
            wait_time = randint(self.t_min, self.t_max)
            iterations = 100
            step_delay = wait_time/iterations

            print(article)
            
            for i in range(iterations):
                self.ui.progress_bar(i, iterations, prefix=message, length=40)
                if order.id in self.to_be_canceled:
                    cancelled = True
                    break
                time.sleep(step_delay)
            
            success = random() <= self.success_rate 
            if not success or cancelled:
                break

        # self.ui.clear()

        if success and not cancelled:
            print(f"Pedido #{order.id} encontrado :)")
            status = Message.ORDER_FOUND
        else:
            print(f"Pedido #{order.id} no encontrado :( Cancelado = {cancelled}")
            if cancelled:
                status = Message.ORDER_CANCELED
            else:
                status = Message.ORDER_NOT_FOUND

        self.producer.call(
            parser.build_message(
                status,
                order.get_body()
                )
            )

    def listen_cancels(self):
        cancel_worker = WorkQueueConsumer(queue=config.queue_robots, listener=self.entry_point_priority, fanout=True)
        cancel_worker.start_consuming()

    def start_consuming(self):
        cancel_thread = threading.Thread(target=self.listen_cancels)
        cancel_thread.daemon = True
        cancel_thread.start()
        self.consumer.start_consuming()