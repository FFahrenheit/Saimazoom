# Un script de python que lance un cliente y simule una serie de acciones (launch_client.py)
from utils.queue_consumer import QueueConsumer
import config

def main():
    queue = QueueConsumer(config.queue_clientes)
    queue.start_consumig()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Clients stopped")