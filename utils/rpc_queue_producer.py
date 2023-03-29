import pika
import config
import uuid

class QueueProducer:
    def __init__(self, queue: str, host: str=config.host_queues, time_limit=None) -> None:
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
        # Solamente verifica que los correlations_id coincidan
        if self.correlation_id == props.correlation_id:
            self.response = body

    def call(self, body:str, time_limit=None):
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
