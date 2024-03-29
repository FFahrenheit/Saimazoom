# Un script de python que lance un repartidor (launch_delivery.py)
from controllers.delivery import Delivery

def main(allow_clear=True):
    controller = Delivery(allow_clear=allow_clear)
    controller.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Delivery stopped")