# Un script de python que lance el controlador (launch_controller.py)
from controllers.controller import Controller

def main(allow_clear=True):
    controller = Controller()
    controller.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Controller stopped")