import pika
import config
from typing import Callable

class QueueConsumer:

    def __init__(self, queue: str, listener: Callable, host=config.host_queues) -> None:
        try:
            # Realiza la conexion al servidor de colas
            self.host = host
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=host) 
            )

            # Obtenemos un canal de la conexion
            self.queue = queue
            self.channel = self.connection.channel()

            # Declaramos la cola de mensajes que consumiremos
            self.channel.queue_declare(
                queue=self.queue
            )
            self.listener = listener

        except Exception as e:
            print(e)
            raise Exception(e)
        

    def on_request(self, ch, method, props, body):
        # message = parser.read_message(body)
        print(f"Received message ")

        # message = parser.read_message(body)

        response = self.listener(ch, method, props, body)
        
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=str(response)
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)
        

    def start_consuming(self):
        # Solo enviamos un mensaje a ka vez
        self.channel.basic_qos(prefetch_count=1)

        # Definimos qué cola consumirá y en dónde se recibirá la respuesta
        self.channel.basic_consume(queue=self.queue, on_message_callback=self.on_request)

        print(f" [x] Esperando peticiones RPC de <{ self.queue }>")
        self.channel.start_consuming()
