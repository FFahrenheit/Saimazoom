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

"""
Clase Controlador, encargada de enviar trabajo a robots y repartidores,
asi como comunicacion con clientes y logica de negocios
"""
class Controller:    

    # Constructor de la clase Controller
    def __init__(self) -> None:
        """
        Constructor, inicializa las colas globales que consumen trabajo del cliente y hacen fanout a robots y delivery
        """
        # Inicialización del objeto API
        self.api = API()
        
        try:
            # Configuración de consumidor de cola de clientes
            self.clientes_consumer = QueueConsumer(queue=config.queue_clientes, listener=self.entry_point_clientes)
            # Configuración de productor de cola de robots con modo fanout
            self.fanout_robots = WorkQueueProducer(queue=config.queue_robots, fanout=True)
            # Configuración de productor de cola de repartidores con modo fanout
            self.fanout_delivery = WorkQueueProducer(queue=config.queue_repartidores, fanout=True)

        except:
            print("No se pudo crear la conexion al servidor de colas")
            exit(1)

    def entry_point_clientes(self, channel, method, props, body):
        """Función de entrada del cliente a la aplicación

        Args:
            channel (_type_): Canal de la cola
            method (_type_): Metodo del mensaje
            props (_type_): Props del mensaje
            body (_type_): Body del mensaje

        Returns:
            _type_: Respuesta en formato de la aplicacion
        """
        print("[C] Mensaje recibido")
        
        # Lectura del mensaje recibido y validación de su contenido
        message = parser.read_message(body)
        if not parser.is_okay(message):
            return parser.build_response(
                Status.ERROR,
                message="Metodo no conocido"
            )
        
        # Obtención del asunto y cuerpo del mensaje
        subject, body = parser.get_request_contents(message)

        print(f"\t{subject=}\n\t{body=}")

        # Redirección del mensaje según su asunto
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
    
    def send_cancelation(self, order_id: int):
        """Función para enviar una petición de cancelación de una orden

        Args:
            order_id (int): ID de la orden a cancelar
        """
        # Obtención del estado actual de la orden
        api = API()
        order_details = api.obtener_orden(order_id)
        status = order_details.get('status', None)
    
        # Lista de estados finales para la orden
        final_status = [OrderStatus.DELIVERED.value, OrderStatus.NOT_FOUND.value, OrderStatus.LOST.value, OrderStatus.CANCELLED.value]
        # Si la orden ya se encuentra en un estado final, no se envía petición de cancelación
        if status == None or status in final_status:
            return
        
        # Construcción del mensaje de cancelación
        message = parser.build_message(
            Message.CANCEL_ORDER,
            body={"order_id" : order_id}
        )

        # Envío de mensaje de cancelación a las colas de robots y repartidores
        self.fanout_robots.call(message)
        self.fanout_delivery.call(message)

    def cancel_order(self, body: dict):
        """Funcion que gestiona los mensajes de cancelacion de ordenes

        Args:
            body (dict): Bodyy del mensaje

        Returns:
            _type_: Respuesta al cliente de confirmación solicitud de cancelacion
        """
        # Se obtiene el ID de la orden a cancelar
        order_id = body.get('order_id', None)
        if order_id is not None:
            # Se inicia un nuevo hilo para enviar la petición de cancelación.
            current_thread = threading.Thread(target=self.send_cancelation, args=(order_id,))
            current_thread.daemon = True
            current_thread.start()
        
        # Se imprime un mensaje de confirmación en la consola.
        print(f"Cancelar orden ID: {order_id}")
        
        # Se construye una respuesta de éxito.
        return parser.build_response(
            Status.OK,
            message="Peticion de cancelacion enviada"
        )
    
    def view_order(self, body: dict):
        """Funcion que gestiona la visualizacion de una orden

        Args:
            body (dict): Body del mensaje

        Returns:
            _type_: Respuesta con detalles de la orden, estado y mensaje
        """
        # Se obtiene el ID de la orden del cuerpo de la petición.
        order_id = body.get('order_id', None)
            # Si no se proporciona el ID de la orden, se construye una respuesta de error.
        if order_id is None:
            return parser.build_response(
                Status.ERROR,
                message="Error de autenticacion"
            )
        # Se obtienen los detalles de la orden del API y se almacenan en una variable.
        order = self.api.obtener_orden(order_id)
        # Se imprime la información de la orden en la consola.
        # print(order)
        # Se construye una respuesta de éxito con la información de la orden.
        return parser.build_response(
            Status.OK,
            message=f"Detalles de orden",
            body={
                "order" : order
            }
        )
        
    def retrieve_orders(self, body: dict):
        """Funcion que gestiona la obtencion de ordenes de un usuario

        Args:
            body (dict): Body del mensaje

        Returns:
            _type_: Respuesta al cliente, diccionario con estado, mensaje y ordenes
        """
        # Obtener el cliente de la solicitud
        client = body.get('client', None)

        if client is None:
            return parser.build_response(
                Status.ERROR,
                message="Error de autenticacion"
            ) 
        
        # Obtener las órdenes del cliente del API
        orders = self.api.obtener_ordenes(client)

        # Retornar una respuesta exitosa con las órdenes obtenidas
        return parser.build_response(
            Status.OK,
            message=f"Obtenidas {len(orders)} ordenes",
            body={
                "orders" : orders
            }
        )


    def create_order(self, body: dict) -> dict:
        """Funcion que gestiona la creacion de ordenes

        Args:
            body (dict): Body del mensaje

        Returns:
            dict: Respuesta al mensaje, diccionario con estado y mensaje
        """
        # Crear una nueva orden en el API y obtener su ID
        order_id = self.api.crear_orden(body)

        # Crear una instancia de la clase Order a partir del cuerpo de la orden recibida
        order = Order()
        order.from_dict(body)
        order.id = order_id

        if order_id:
            # Iniciar un nuevo hilo para buscar la orden creada
            current_thread = threading.Thread(target=self.search_order, args=(order,))
            current_thread.daemon = True
            current_thread.start()

            # Retornar una respuesta exitosa con el ID de la orden creada
            return parser.build_response(
                Status.OK,
                message=f"Orden creada con ID {order_id}"
            )
        else:
            # Retornar una respuesta de error si no se pudo crear la orden
            return parser.build_response(
                Status.ERROR,
                message="No se pudo crear la orden"
            )

    def search_order(self, order: Order):
        """
        Busca una orden en la cola de robots.

        Parameters:
            order (Order): la orden a buscar.

        Returns:
            None.
        """
        # Obtener una instancia del API
        api = API()
        # Obtener el ID de la orden
        order_id = order.id

        # Actualizar el estado de la orden en el API a "PROCESANDO"
        api.actualizar_orden(order_id, status=OrderStatus.PROCESSING.value)

        # Crear un mensaje para buscar la orden en la cola de robots
        message = parser.build_message(Message.SEARCH_ORDER, order.get_body())

        # Enviar el mensaje a la cola de robots
        WorkQueueProducer(queue=config.queue_robots).call(message)

        # Imprimir un mensaje de confirmación
        print(f"Peticion a robots para pedido #{order_id} enviada")


    def deliver_order(self, order_id):
        """
        Envia una solicitud para entregar una orden.

        Parameters:
            order_id (int): el ID de la orden a entregar.

        Returns:
            None.
        """
        # Se construye el mensaje con el id del pedido
        message = parser.build_message(Message.DELIVER_ORDER, {"id": order_id})

        # Se imprime en pantalla el mensaje de envío del pedido
        print(f"Enviando petición para pedido #{order_id}")

        # Se llama al productor de la cola para enviar el mensaje
        response = QueueProducer(queue=config.queue_repartidores).call(message)

        # Se procesa la respuesta obtenida
        response = parser.process_response(response)

        # Si la respuesta es exitosa se imprime el mensaje de éxito
        if response.status == Status.OK.value:
            print(f"EXITO: { response.message }")
        # De lo contrario se imprime el mensaje de error
        else:
            print(f"ERROR: { response.message }")


    def login(self, body: dict) -> dict:  
        """
        Realiza el inicio de sesión de un usuario.

        Parameters:
            body (dict): un diccionario que contiene el nombre de usuario y la contraseña del usuario.

        Returns:
            dict: un diccionario que contiene el estado de la respuesta, el mensaje y los datos del usuario (si es válido).
        """
        # Se realiza el login del usuario utilizando la api
        user = self.api.login(body.get('username', ""), body.get('password', ''))

        # Si el usuario existe se retorna un mensaje de bienvenida junto con los datos del usuario
        if user is not None:
            return parser.build_response(
                Status.OK,
                "Login correcto, bienvenido " + user['name'],
                user
            )
        # De lo contrario se retorna un mensaje de error
        else:
            return parser.build_response(
                Status.ERROR,
                "No se pudieron autenticar las credenciales"
            )


    def registrar_usuario(self, body: dict) -> dict:
        """
        Registra un nuevo usuario.

        Parameters:
            body (dict): un diccionario que contiene los datos del usuario.

        Returns:
            dict: un diccionario que contiene el estado de la respuesta y un mensaje.
        """
        if self.api.registrar_usuario(body):
            return parser.build_response(
                Status.OK,
                "Usuario registrado"
            )
        # Si no se pudo registrar el usuario se retorna un mensaje de error
        else:
            return parser.build_response(
                Status.ERROR,
                "No se pudo registrar el usuario"
            )

    def retrieve_orders(self, body: dict):
        """
        Obtiene las órdenes de un cliente utilizando la API y retorna un mensaje con las órdenes obtenidas.

        Args:
            body (dict): cuerpo de la solicitud, debe contener el campo "client" con el identificador del cliente.

        Returns:
            dict: diccionario con los siguientes campos:
                - status (str): código de estado de la respuesta (OK o ERROR).
                - message (str): mensaje descriptivo del resultado de la operación.
                - body (dict): diccionario con las órdenes obtenidas del cliente.
        """
        # Se obtiene el cliente de la solicitud
        client = body.get('client', None)

        # Si el cliente es nulo se retorna un mensaje de error de autenticación
        if client is None:
            return parser.build_response(
                Status.ERROR,
                message="Error de autenticacion"
            ) 

        # Se obtienen las órdenes del cliente utilizando la api
        orders = self.api.obtener_ordenes(client)

        # Se retorna un mensaje de éxito con las órdenes obtenidas
        return parser.build_response(
            Status.OK,
            message=f"Obtenidas {len(orders)} ordenes",
            body={
                "orders" : orders
            }
        )


    def entry_point_robots(self, channel, method, props, body):
        """
        Procesa los mensajes recibidos de los robots.

        Args:
            channel (pika.channel.Channel): canal de comunicación de RabbitMQ.
            method (pika.spec.Basic.Deliver): especificación de entrega de un mensaje RabbitMQ.
            props (pika.spec.BasicProperties): propiedades del mensaje RabbitMQ.
            body (bytes): cuerpo del mensaje RabbitMQ en formato bytes.
        """
        print("[R] Mensaje recibido")

        # Se lee el mensaje recibido
        message = parser.read_message(body)

        # Si el mensaje no está bien formado, se descarta
        if not parser.is_okay(message):
            print("Mensaje malformado del robot")
            return

        # Se obtienen los campos del mensaje
        subject, body = parser.get_request_contents(message)

        print(f"\t{subject=}\n\t{body=}")

        # Se crea una instancia de la API y una instancia de la Orden a partir del cuerpo del mensaje
        api = API()
        order = Order()
        order.from_dict(body)

        # Se procesa el mensaje en función de su asunto
        if subject == Message.ORDER_FOUND.value:
            # Si la orden ha sido encontrada, se actualiza su estado en la API y se envía un mensaje de entrega
            message = parser.build_message(
                Message.DELIVER_ORDER,
                order.get_body()
            )
            self.delivery_producer.call(message)
            # Actualizar al final para evitar problemas
            api.actualizar_orden(order.id, OrderStatus.FOUND.value)

        elif subject == Message.ORDER_NOT_FOUND.value:
            # Si la orden no ha sido encontrada, se actualiza su estado en la API
            api.actualizar_orden(order.id, OrderStatus.NOT_FOUND.value)
        elif subject == Message.ORDER_CANCELED.value:
            # Si la orden ha sido cancelada, se actualiza su estado en la API, se envía un mensaje de cancelación y se difunde a todos los robots y repartidores
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
        """
        Procesa los mensajes recibidos de los repartidores.

        Args:
            channel (pika.channel.Channel): canal de comunicación de RabbitMQ.
            method (pika.spec.Basic.Deliver): especificación de entrega de un mensaje RabbitMQ.
            props (pika.spec.BasicProperties): propiedades del mensaje RabbitMQ.
            body (bytes): cuerpo del mensaje RabbitMQ en formato bytes.
        """
        print("[D] Mensaje recibido")

        # Se lee el mensaje y se verifica si está bien formado
        message = parser.read_message(body)
        if not parser.is_okay(message):
            print("Mensaje malformado de repartidores")
            return

        # Se obtiene el asunto y cuerpo del mensaje
        subject, body = parser.get_request_contents(message)

        print(f"\t{subject=}\n\t{body=}")

        # Se crea una instancia de la API y de la Orden
        api = API()
        order = Order()
        order.from_dict(body)

        # Se verifica el asunto del mensaje y se toma acción correspondiente
        if subject == Message.ON_DELIVER.value:
            api.actualizar_orden(order.id, OrderStatus.ON_DELIVER.value)
        elif subject == Message.ORDER_DELIVERED.value:
            api.actualizar_orden(order.id, OrderStatus.DELIVERED.value)
        elif subject == Message.ORDER_LOST.value:
            api.actualizar_orden(order.id, OrderStatus.LOST.value)
        elif subject == Message.ORDER_CANCELED.value:
            api.actualizar_orden(order.id, OrderStatus.CANCELLED.value)
            message = parser.build_message(
                Message.CLEAR_CANCELATION,
                body={"order_id" : order.id}
            )
            # Se envía el mensaje a los robots y repartidores
            self.fanout_robots.call(message)
            self.fanout_delivery.call(message)
        else:
            print("Mensaje no implementado de delivery")


    def listen_response_robots(self):
        """
        Escucha las respuestas de los robots desde la cola "queue_respuesta_robots"
        y las maneja mediante el método "entry_point_robots".
        """
        # Crear un productor de colas para la cola "queue_repartidores"
        self.delivery_producer = WorkQueueProducer(config.queue_repartidores)
        # Crear un consumidor de colas para la cola "queue_respuesta_robots"
        queue_robots = WorkQueueConsumer(config.queue_respuesta_robots, self.entry_point_robots)
        # Iniciar el consumo de mensajes en la cola "queue_respuesta_robots"
        queue_robots.start_consuming()

    def listen_response_delivery(self):
        """
        Escucha las respuestas de los repartidores desde la cola "queue_respuesta_repartidores"
        y las maneja mediante el método "entry_point_delivery".
        """
        # Crear un consumidor de colas para la cola "queue_respuesta_repartidores"
        queue_delivery = WorkQueueConsumer(config.queue_respuesta_repartidores, self.entry_point_delivery)
        # Iniciar el consumo de mensajes en la cola "queue_respuesta_repartidores"
        queue_delivery.start_consuming()

    def start_consuming(self):
        """
        Inicia los hilos de ejecución para escuchar las respuestas de los robots y los repartidores,
        respectivamente, y también inicia el consumo de mensajes en la cola "clientes_consumer".
        """
        # Crear un hilo de ejecución para el método "listen_response_robots"
        thread_robots_response = threading.Thread(target=self.listen_response_robots)
        thread_robots_response.daemon = True
        thread_robots_response.start()

        # Crear un hilo de ejecución para el método "listen_response_delivery"
        threads_delivery_response = threading.Thread(target=self.listen_response_delivery)
        threads_delivery_response.daemon = True
        threads_delivery_response.start()

        # Iniciar el consumo de mensajes en la cola "clientes_consumer"
        self.clientes_consumer.start_consuming()