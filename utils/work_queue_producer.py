import pika
import config
import uuid

class WorkQueueProducer:
    def __init__(self, queue: str, host: str=config.host_queues, fanout=False) -> None:
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