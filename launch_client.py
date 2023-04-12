# Un script de python que lance un cliente y simule una serie de acciones (launch_client.py)
from controllers.auto_client import AutoClient

def main(allow_clear=True):
    client = AutoClient(allow_clear)
    print("Comenzamos con el auto cliente")
    client.inicio()    

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Clients stopped")