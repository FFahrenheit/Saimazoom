# Un script de python que lance el controlador (launch_controller.py)
from time import sleep

def main():
    while True:
        print("Controllers running!")
        sleep(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Controller stopped")