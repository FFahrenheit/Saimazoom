"""
Script para desarrollo
Se corren las 4 entidades (cliente, controlador, robots, repartidos) en paralelo
"""
from time import sleep
from threading import Thread
import launch_client as client, launch_controller as controller, launch_delivery as delivery, launch_robot as robot

def main():
    print("[ Developing server started ]")
    functions = [client.main, controller.main, delivery.main, robot.main]

    threads = [ Thread(target = function) for function in functions ]

    for i, thread in enumerate(threads):
        sleep(i * 0.2)
        thread.daemon = True
        thread.start()

    while not False:
        pass


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Server stopped")