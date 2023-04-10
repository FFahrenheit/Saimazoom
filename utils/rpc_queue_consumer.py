import pika
import config
from typing import Callable

class QueueConsumer:

    def __init__(self, queue: str, listener: Callable, host=config.host_queues) -> None:
        """
        Crea una instancia de QueueConsumer que conecta a un servidor de colas y declara la cola que se consumirá.

        :param queue: El nombre de la cola a la que se suscribirá el consumidor.
        :type queue: str
        :param listener: El manejador de eventos que procesará los mensajes de la cola.
        :type listener: Callable
        :param host: El servidor de colas a conectarse, por defecto es el valor de `config.host_queues`.
        :type host: str
        """
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
        """
        Función de callback para procesar los mensajes de la cola.

        :param ch: El canal de la conexión a la cola.
        :type ch: pika.channel.Channel
        :param method: La información del método de la conexión.
        :type method: pika.Spec.Basic.Deliver
        :param props: Las propiedades del mensaje recibido.
        :type props: pika.Spec.BasicProperties
        :param body: El cuerpo del mensaje recibido.
        :type body: bytes
        """
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
        """
        Inicia el proceso de escuchar por mensajes en la cola.
        """
        # Solo enviamos un mensaje a la vez. Fair dispatch
        self.channel.basic_qos(prefetch_count=1)

        # Definimos qué cola consumirá y en dónde se recibirá la respuesta
        self.channel.basic_consume(queue=self.queue, on_message_callback=self.on_request)

        print(f" [x] Esperando peticiones RPC de <{ self.queue }>")
        self.channel.start_consuming()