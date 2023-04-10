import pika
import config
from typing import Callable

class WorkQueueConsumer():
    def __init__(self, queue: str, listener: Callable, host=config.host_queues, fanout=False) -> None:
        """
        Inicializa el objeto WorkQueueConsumer.

        :param queue: El nombre de la cola a la que nos conectaremos.
        :param listener: La función que se ejecutará cada vez que se reciba un mensaje en la cola.
        :param host: El host del servidor de colas. Por defecto, se utiliza el host definido en config.py.
        :param fanout: Indica si se trata de una cola fanout. Por defecto, es False.
        """
        try:
            # Realiza la conexion al servidor de colas
            self.fanout = fanout
            self.host = host
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=host) 
            )

            # Obtenemos un canal de la conexion
            self.queue = queue
            self.channel = self.connection.channel()
            
            self.listener = listener

            if self.fanout:
                self.channel.exchange_declare(exchange=self.queue, exchange_type='fanout')
                result = self.channel.queue_declare(
                    queue='',
                    exclusive=True
                )
                self.queue_name = result.method.queue

                self.channel.queue_bind(exchange=self.queue, queue=self.queue_name)
            else:
                # Declaramos la cola de mensajes que consumiremos
                self.channel.queue_declare(
                    queue=self.queue,
                    durable=True
                )

        except Exception as e:
            print(e)
            raise Exception(e)
        
    def on_request(self, ch, method, props, body):
        """
        La función que se ejecuta cada vez que se recibe un mensaje en la cola.

        :param ch: El canal de la conexión.
        :param method: El método que se utilizó para enviar el mensaje.
        :param props: Las propiedades del mensaje.
        :param body: El contenido del mensaje.
        """
        try:
            print(f"Received message ")
            self.listener(ch, method, props, body)

            if not self.fanout:
                ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print("Message won't be processed")
            print("Cause: " + str(e))
            if "closed" in str(e):
                raise Exception("Channel closed")
            if not self.fanout:
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


    def start_consuming(self):
        """
        Comienza a consumir mensajes de la cola.
        """
        if self.fanout:
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.on_request,
                auto_ack=True
            )
        else:
            # Solo enviamos un mensaje a la vez
            self.channel.basic_qos(prefetch_count=1)

            # Definimos qué cola consumirá y en dónde se recibirá la respuesta
            self.channel.basic_consume(queue=self.queue, on_message_callback=self.on_request)

        print(f" [x] Esperando peticiones WorkQueue de <{ self.queue }>")
        self.channel.start_consuming()