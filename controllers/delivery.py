import config
from utils.work_queue_consumer import WorkQueueConsumer
from utils.work_queue_producer import WorkQueueProducer
from utils.ui import UIConsole
import utils.message_parser as parser
from utils.messages import Message, Status
from random import randint, random
from models.order import Order
import time 
import threading

class Delivery:
    def __init__(self, t_min=config.wait_delivery_min, t_max=config.wait_delivery_max, success_rate=config.p_entrega) -> None:
        self.t_min = t_min
        self.t_max = t_max
        self.success_rate = success_rate
        self.ui = UIConsole()
        self.to_be_canceled = []
        try:
            self.consumer = WorkQueueConsumer(queue=config.queue_repartidores,listener=self.entry_point)  
            self.producer = WorkQueueProducer(queue=config.queue_respuesta_repartidores)
        except:
            print("No se pudo crear la conexion al servidor de colas")
            exit(1)

    def entry_point(self, channel, method, props, body):
        print("[C] Mensaje recibido")

        message = parser.read_message(body)
        if not parser.is_okay(message):
            print("Metodo no conocido")
            return
        
        subject, body = parser.get_request_contents(message)
        print(f"\t{subject=}\n\t{body=}")

        # Agregar cancelados    
        if subject == Message.DELIVER_ORDER.value:
           return self.entregar_pedido(body)
        else:
            print("Metodo no implementado")
        
    def entregar_pedido(self, body):
        order = Order()
        order.from_dict(body)
        wait_time= randint(self.t_min, self.t_max)
        iterations = 100
        step_delay = wait_time/iterations
        message = f"Entregando pedido #{order.id}"
        cancelled = False

        for i in range(iterations):
            if order.id in self.to_be_canceled:
                cancelled = True
                break
            self.ui.progress_bar(i, iterations, prefix=message, length=40)
            time.sleep(step_delay)
        
        self.ui.clear()
        success = random() <= self.success_rate and not cancelled

        if success:
            status = Message.ORDER_DELIVERED
            print(f"Pedido #{order.id} entregado :)")
        else:
            if cancelled:
                status = Message.ORDER_CANCELED
            else:
                status = Message.ORDER_LOST
            print(f"Pedido #{order.id} no entregado :( - Cancelado = {cancelled}")
        
        self.producer.call(
            parser.build_message(
                status,
                order.get_body()
            )
        )
    
    def entry_point_priority(self, channel, method, props, body):
        print("[C] Mensaje recibido - Entry point cancelados")

        message = parser.read_message(body)
        if not parser.is_okay(message):
            print("Mensaje incorrecto")
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
    
    def listen_cancels(self):
        cancel_worker = WorkQueueConsumer(queue=config.queue_repartidores, listener=self.entry_point_priority, fanout=True)
        cancel_worker.start_consuming()

    def start_consuming(self):
        cancel_thread = threading.Thread(target=self.listen_cancels)
        cancel_thread.daemon = True
        cancel_thread.start()
        self.consumer.start_consuming()