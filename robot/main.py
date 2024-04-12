import threading
import multiprocessing

from utils.TopicsProcess import Topics
from modules.ServerModule import ServerModule
from modules.RobotModule import RobotModule
from modules.CameraModule import CameraModule
from modules.LidarModule import LidarModule
import time
from settings import settings
# from roboviz import MapVisualizer
# Server
SERVER_IP = "10.144.113.61"
# SERVER_IP = '127.0.0.1'
SERVER_PORT = 8003
SERIAL_PORT = '/dev/ttyACM0'

# Robot
MOTOR_SPEED_MAX = 500
MOTOR_SPEED_MIN = 50
MOTOR_TURN_SPEED = 255
SERIAL_BAUD_RATE = 115200

MAP_SIZE_PIXELS = 100
MAP_SIZE_METERS = 10
def main():
    # viz = MapVisualizer(MAP_SIZE_PIXELS, MAP_SIZE_METERS, 'SLAM BRUH')
    topics = Topics(settings.get('default_topics'))
    processes = []
    shutdown_flag = multiprocessing.Event()

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
        # {
        #     'module': LidarModule,
        #     'args': (
        #         '/dev/ttyUSB0',
        #         50,
        #         MAP_SIZE_PIXELS,
        #         MAP_SIZE_METERS,
        #     ),
        #     'id': 'LidarModule',
        # },
        
    ]

    for i in range(0, len(modules)):
        module = modules[i].get('module')
        args = modules[i].get('args')
        process_id = modules[i].get('id')

        process = multiprocessing.Process( # threading.Thread( # multiprocessing.Proces
            target=module.spawn,
            args=(
                shutdown_flag,
                topics,
                process_id,
                settings,
                args,
            ),
        )
        process.start()
        processes.append(process)


    lidar_frame_topic = topics.get_topic('lidar_frame')
    lidar_map_topic = topics.get_topic('lidar_map')
    try:
        while True:
            continue
            # if (lidar_map_topic.read_data()):
            #     lidar_map = lidar_map_topic.read_data()
            #     x,y,theta = lidar_frame_topic.read_data()
            #     # print(x)
            #     # viz.display((x/1000.), (y/1000.), theta, lidar_map)
            # # time.sleep(0.05)

    except KeyboardInterrupt:
        print('\n[MAIN] > Shutting Down all processes Gracefully \n')
        shutdown_flag.set()

    try:
        for process in processes:
            process.join()
        print('Successfully Shutdown All Modules')
    except multiprocessing.ProcessError as e:
        print('Error Shutting Down Processes')
        print('STACK TRACE BELOW\n')
        print('--------------------')
        print(e)
        print('--------------------')


if __name__ == '__main__':
    main()
