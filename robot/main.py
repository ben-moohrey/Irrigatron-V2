import threading
from utils.Topics import Topics
from modules.ServerModule import ServerModule
from modules.RobotModule import RobotModule
from modules.CameraModule import CameraModule
from modules.LidarModule import LidarModule
import time
from settings import settings

# Server
SERVER_IP = "10.144.113.182"
# SERVER_IP = '127.0.0.1'
SERVER_PORT = 8003
SERIAL_PORT = '/dev/ttyACM0'

# Robot
MOTOR_SPEED_MAX = 600
MOTOR_SPEED_MIN = 50
MOTOR_TURN_SPEED = 255
SERIAL_BAUD_RATE = 115200


def main():
    topics = Topics(settings.get('default_topics'))
    threads = []
    shutdown_flag = threading.Event()

    modules = [
        {
            'module': ServerModule,
            'args': (
                SERVER_IP,
                SERVER_PORT,
            ),
            'id': 'ServerModule',
        },
        {
            'module': RobotModule,
            'args': (
                MOTOR_SPEED_MIN,
                MOTOR_SPEED_MAX,
                SERIAL_PORT,
                SERIAL_BAUD_RATE,
            ),
            'id': 'RobotModule',
        },
        {
            'module': CameraModule,
            'args': (),
            'id': 'CameraModule',
        },
        {
            'module': LidarModule,
            'args': ('/dev/ttyUSB0', 50,),
            'id': 'LidarModule',
        },
        
    ]

    for i in range(0, len(modules)):
        module = modules[i].get('module')
        args = modules[i].get('args')
        thread_id = modules[i].get('id')

        thread = threading.Thread(
            target=module.spawn,
            args=(
                shutdown_flag,
                topics,
                thread_id,
                settings,
                args,
            ),
        )
        thread.start()
        threads.append(thread)

    try:
        while True:
            time.sleep(0.05)

    except KeyboardInterrupt:
        print('\n[MAIN] > Shutting Down all Threads Gracefully \n')
        shutdown_flag.set()

    try:
        for thread in threads:
            thread.join()
        print('Successfully Shutdown All Modules')
    except threading.ThreadError as e:
        print('Error Shutting Down Threads')
        print('STACK TRACE BELOW\n')
        print('--------------------')
        print(e)
        print('--------------------')


if __name__ == '__main__':
    main()
