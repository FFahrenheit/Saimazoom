from models.order import Order
from controllers.api import API
from utils.rpc_queue_consumer import QueueConsumer
from utils.rpc_queue_producer import QueueProducer
from utils.work_queue_producer import WorkQueueProducer
from utils.work_queue_consumer import WorkQueueConsumer
import config
import utils.message_parser as parser
from utils.messages import Message, Status
import threading
from utils.order_status import OrderStatus

class Controller:
    def __init__(self) -> None:
        self.api = API()
        try:
            self.clientes_consumer = QueueConsumer(queue=config.queue_clientes, listener=self.entry_point_clientes)
            self.fanout_robots = WorkQueueProducer(queue=config.queue_robots, fanout=True)
            self.fanout_delivery = WorkQueueProducer(queue=config.queue_repartidores, fanout=True)

        except:
            print("No se pudo crear la conexion al servidor de colas")
            exit(1)


    def entry_point_clientes(self, channel, method, props, body):
        print("[C] Mensaje recibido")

        message = parser.read_message(body)
        if not parser.is_okay(message):
            return parser.build_response(
                Status.ERROR,
                message="Metodo no conocido"
            )
        
        subject, body = parser.get_request_contents(message)

        print(f"\t{subject=}\n\t{body=}")

        if subject == Message.REGISTRO.value:
           return self.registrar_usuario(body)
        elif subject == Message.LOGIN.value:
            return self.login(body)
        elif subject == Message.CREATE_ORDER.value:
            return self.create_order(body)
        elif subject == Message.VIEW_ORDERS.value:
            return self.retrieve_orders(body)
        elif subject == Message.VIEW_ORDER.value:
            return self.view_order(body)
        elif subject == Message.CANCEL_ORDER.value:
            return self.cancel_order(body)
        else:
            return parser.build_response(
                Status.ERROR,
                message="No implementado"
            )
    
    def send_cancelation(self, order_id):
        # Fanout!
        api = API()
        order_details = api.obtener_orden(order_id)
        status = order_details.get('status', None)
    
        final_status = [OrderStatus.DELIVERED.value, OrderStatus.NOT_FOUND.value, OrderStatus.LOST.value, OrderStatus.CANCELLED.value]
        
        if status == None or status in final_status:
            return
        
        message = parser.build_message(
            Message.CANCEL_ORDER,
            body={"order_id" : order_id}
        )

        self.fanout_robots.call(message)
        self.fanout_delivery.call(message)

    def cancel_order(self, body: dict):
        order_id = body.get('order_id', None)
        if order_id is not None:
            current_thread = threading.Thread(target=self.send_cancelation, args=(order_id,))
            current_thread.daemon = True
            current_thread.start()

        print("Cancelar orden... Tsss")
        
        return parser.build_response(
            Status.OK,
            message="Peticion de cancelacion enviada"
        )
    
    def view_order(self, body: dict):
        order_id = body.get('order_id', None)

        if order_id is None:
            return parser.build_response(
                Status.ERROR,
                message="Error de autenticacion"
            )

        order = self.api.obtener_orden(order_id)
        print(order)
        return parser.build_response(
            Status.OK,
            message=f"Detalles de orden",
            body={
                "order" : order
            }
        )

        
    def retrieve_orders(self, body: dict):
        client = body.get('client', None)

        if client is None:
            return parser.build_response(
                Status.ERROR,
                message="Error de autenticacion"
            ) 
        
        orders = self.api.obtener_ordenes(client)

        return parser.build_response(
            Status.OK,
            message=f"Obtenidas {len(orders)} ordenes",
            body={
                "orders" : orders
            }
        )


    def create_order(self, body: dict) -> dict:
        order_id = self.api.crear_orden(body)
        order = Order()
        order.from_dict(body)
        order.id = order_id

        if order_id:
            current_thread = threading.Thread(target=self.search_order, args=(order,))
            current_thread.daemon = True
            current_thread.start()
            return parser.build_response(
                Status.OK,
                message=f"Orden creada con ID {order_id}"
            )
        else:
            return parser.build_response(
                Status.ERROR,
                message="No se pudo crear la orden"
            )

    def search_order(self, order: Order):
        api = API()
        order_id = order.id
        api.actualizar_orden(order_id, status=OrderStatus.PROCESSING.value)
        message = parser.build_message(Message.SEARCH_ORDER, order.get_body())

        # response = self.robots_producer.call(message)
        WorkQueueProducer(queue=config.queue_robots).call(message)
        # Procesamiento de base de datos y respuesta cliente
        print(f"Peticion a robots para pedido #{order_id} enviada")

    def deliver_order(self, order_id):
        message = parser.build_message(Message.DELIVER_ORDER, {"id": order_id})

        print(f"Enviando peticion para pedido #{order_id}")
        response = QueueProducer(queue=config.queue_repartidores).call(message)

        response = parser.process_response(response)

        if response.status == Status.OK.value:
            print(f"EXITO: { response.message }")
        else:
            print(f"ERROR: { response.message }")


    def login(self, body: dict) -> dict:  
        user = self.api.login(body.get('username', ""), body.get('password', ''))
        if user is not None:
            return parser.build_response(
                Status.OK,
                "Login correcto, bienvenido " + user['name'],
                user
            )
        else:
            return parser.build_response(
                Status.ERROR,
                "No se pudieron autenticar las credenciales"
            )

    def registrar_usuario(self, body: dict) -> dict:
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
        
    def retrieve_orders(self, body: dict):
        client = body.get('client', None)

        if client is None:
            return parser.build_response(
                Status.ERROR,
                message="Error de autenticacion"
            ) 
        
        orders = self.api.obtener_ordenes(client)

        return parser.build_response(
            Status.OK,
            message=f"Obtenidas {len(orders)} ordenes",
            body={
                "orders" : orders
            }
        )
    
    def entry_point_robots(self, channel, method, props, body):
        print("[R] Mensaje recibido")

        message = parser.read_message(body)
        if not parser.is_okay(message):
            print("Mensaje malformado del robot")
            # Se descarta, ya que no está bien
            return
        
        subject, body = parser.get_request_contents(message)

        print(f"\t{subject=}\n\t{body=}")
        
        api = API()
        order = Order()
        order.from_dict(body)

        if subject == Message.ORDER_FOUND.value:
            api.actualizar_orden(order.id, OrderStatus.FOUND.value)
            message = parser.build_message(
                Message.DELIVER_ORDER,
                order.get_body()
            )
            api.actualizar_orden(order.id, OrderStatus.ON_DELIVER.value)
            self.delivery_producer.call(message)
        elif subject == Message.ORDER_NOT_FOUND.value:
            api.actualizar_orden(order.id, OrderStatus.NOT_FOUND.value)
        elif subject == Message.ORDER_CANCELED.value:
            api.actualizar_orden(order.id, OrderStatus.CANCELLED.value)
            message = parser.build_message(
                Message.CLEAR_CANCELATION,
                body={"order_id" : order.id}
            )

            self.fanout_robots.call(message)
            self.fanout_delivery.call(message)
        else:
            print("Mensaje no implementado para robot")

    def entry_point_delivery(self, channel, method, props, body):
        print("[D] Mensaje recibido")

        message = parser.read_message(body)
        if not parser.is_okay(message):
            print("Mensaje malformado de repartidores")
            return
        
        subject, body = parser.get_request_contents(message)

        print(f"\t{subject=}\n\t{body=}")
        
        api = API()
        order = Order()
        order.from_dict(body)

        if subject == Message.ORDER_DELIVERED.value:
            api.actualizar_orden(order.id, OrderStatus.DELIVERED.value)
        elif subject == Message.ORDER_LOST.value:
            api.actualizar_orden(order.id, OrderStatus.LOST.value)
        elif subject == Message.ORDER_CANCELED.value:
            api.actualizar_orden(order.id, OrderStatus.CANCELLED.value)
            message = parser.build_message(
                Message.CLEAR_CANCELATION,
                body={"order_id" : order.id}
            )
            self.fanout_robots.call(message)
            self.fanout_delivery.call(message)
        else:
            print("Mensaje no implementado de delivery")

    def listen_response_robots(self):
        self.delivery_producer = WorkQueueProducer(config.queue_repartidores)
        queue_robots = WorkQueueConsumer(config.queue_respuesta_robots, self.entry_point_robots)
        queue_robots.start_consuming()

    def listen_response_delivery(self):
        queue_delivery = WorkQueueConsumer(config.queue_respuesta_repartidores, self.entry_point_delivery)
        queue_delivery.start_consuming()

    def start_consuming(self):
        thread_robots_response = threading.Thread(target=self.listen_response_robots)
        thread_robots_response.daemon = True
        thread_robots_response.start()
        threads_delivery_response = threading.Thread(target=self.listen_response_delivery)
        threads_delivery_response.daemon = True
        threads_delivery_response.start()
        self.clientes_consumer.start_consuming()
