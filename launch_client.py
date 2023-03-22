# Un script de python que lance un cliente y simule una serie de acciones (launch_client.py)
from time import sleep

def main():
    while True:
        print("Clients running!")
        sleep(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Clients stopped")