# Un script de python para simular un cliente desde línea de comandos (commandline_client.py)
from controllers.manual_client import ManualClient

def main():
    client = ManualClient()
    client.menu()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Commandline closed")