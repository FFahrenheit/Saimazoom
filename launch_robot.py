# Un script de python que lance un robot (launch_robot.py)
from time import sleep

def main():
    while True:
        print("Robots running!")
        sleep(1)

print(__name__)
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Robots stopped")