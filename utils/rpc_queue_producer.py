import pika
import config
import uuid

class QueueProducer:
    def __init__(self, queue: str, host: str=config.host_queues, time_limit=None) -> None:
        """
        Inicializa el productor de cola. Se conecta al servidor de colas y crea una cola para las respuestas.
        Asigna un callback para procesar las respuestas obtenidas.
        :param queue: El nombre de la cola a la que se enviarán los mensajes.
        :param host: La dirección IP del servidor de colas.
        :param time_limit: El tiempo máximo que se permitirá esperar una respuesta antes de cancelar la petición.
        """
        # Nos conectamos al servidor de colas en cuestion
        self.time_limit = time_limit
        try:
            self.host = host
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host = self.host)
            )

            self.queue = queue
            self.channel = self.connection.channel()
            # Creamos nuestra cola para respuestas
            result = self.channel.queue_declare(queue='', exclusive=True, durable=False, auto_delete=True)

            # Le asignamos un callback para consumir las respuestas obtenidas
            self.callback_queue = result.method.queue
            self.channel.basic_consume(
                queue=self.callback_queue,
                on_message_callback=self.on_response,
                auto_ack=True
            )

            # Limpiamos la respuesta y el ID (ya que aun no enviamos peticiones)
            self.response = None
            self.correlation_id = None
        except Exception as e:
            print(e)
            raise Exception(e)

    # Función callback
    def on_response(self, channel, method, props, body):
        """
        Función callback que se llama cuando se recibe una respuesta.
        Verifica que el correlation_id de la respuesta coincida con el de la petición.
        :param channel: El canal de la conexión.
        :param method: El método de la conexión.
        :param props: Las propiedades de la conexión.
        :param body: El cuerpo de la respuesta.
        """
        # Solamente verifica que los correlations_id coincidan
        if self.correlation_id == props.correlation_id:
            self.response = body

    def call(self, body:str, time_limit=None):
        """
        Realiza una petición a la cola y espera por una respuesta.
        :param body: El cuerpo del mensaje que se enviará a la cola.
        :param time_limit: El tiempo máximo que se permitirá esperar una respuesta antes de cancelar la petición.
        :return: La respuesta recibida.
        """
        limit = time_limit if time_limit is not None else self.time_limit

        self.response = None

        # Creamos un correlation ID para identificar la respuesta
        self.correlation_id = str(uuid.uuid4())
        
        # Hacemos la peticion
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue,

            # Adjuntamos la cola de respuesta y su ID
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.correlation_id
            ),
            body=body
        )

        # Tiempo que esperaremos (en segundos)
        self.connection.process_data_events(time_limit=limit)
        
        if self.response is None:
            print("[x] Timed out or empty response")
        
        return self.response
