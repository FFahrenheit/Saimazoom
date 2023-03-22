# Un script de python que lance un repartidor (launch_delivery.py)
from time import sleep

def main():
    while True:
        print("Delivery running!")
        sleep(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Delivery stopped")