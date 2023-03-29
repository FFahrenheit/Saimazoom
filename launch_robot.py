# Un script de python que lance un robot (launch_robot.py)
from controllers.robot import Robot

def main():
    try:
        robot = Robot()
        robot.start_consuming()
    except Exception as e:
        print(e)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        print("Robots stopped")