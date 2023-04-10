import pika
import config

class WorkQueueProducer:
    def __init__(self, queue: str, host: str=config.host_queues, fanout=False) -> None:
        """
        Inicializa una instancia de WorkQueueProducer para enviar mensajes a una cola especificada.

        Args:
        - queue (str): Nombre de la cola a la que se enviarán los mensajes.
        - host (str, optional): Dirección IP del servidor de colas. Por defecto, se utiliza la dirección especificada en la configuración.
        - fanout (bool, optional): Especifica si se usará un exchange de tipo 'fanout' para enviar los mensajes. Por defecto, se utiliza False.
        """
        self.fanout = fanout
        # Nos conectamos al servidor de colas en cuestion
        try:
            self.host = host
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host = self.host)
            )

            self.queue = queue
            self.channel = self.connection.channel()

            if self.fanout:
                self.channel.exchange_declare(exchange=self.queue, exchange_type='fanout')
            else:
                # Creamos nuestra cola para respuestas
                self.channel.queue_declare(queue=self.queue, durable=True)

        except Exception as e:
            print(e)
            raise Exception(e)

    def call(self, body:str):
        """
        Envía un mensaje a la cola especificada.

        Args:
        - body (str): Contenido del mensaje.

        Returns:
        None.
        """
        # Hacemos la peticion
        if self.fanout:
            self.channel.basic_publish(
                exchange=self.queue,
                routing_key='',
                body=body
            )
        else:
            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue,
                # Adjuntamos la cola de respuesta y su ID
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                ),
                body=body
            )