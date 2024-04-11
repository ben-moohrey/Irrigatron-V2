# from classes.serial import serial
import serial
from modules.BaseModule import BaseModule
import time

class RobotModule(BaseModule):
    def __init__(
        self,
        topics,
        thread_id,
        settings,
        MOTOR_SPEED_MIN,
        MOTOR_SPEED_MAX,
        serial_port,
        baud_rate = 115200,
    ):
        super().__init__(topics, thread_id, settings)
        self.control_data_topic = topics.get_topic('control_data')
        self.arucode_locations_topic = self.topics.get_topic("arucode_locations_topic")
        self.MOTOR_SPEED_MIN = MOTOR_SPEED_MIN
        self.MOTOR_SPEED_MAX = MOTOR_SPEED_MAX
        self.serial_conn = serial.Serial(serial_port, baud_rate)
        self.motor_state = {
            'left_front': 0,
            'right_front': 0,
            'left_back': 0,
            'right_back': 0,
        }
        self.pump_state = 0

        self.robot_state = 'idle'
        self.state_auto = {
            'path_index': 0,
            'current_path_time': 0.0,
            'path_start_time': 0.0,
            'path_time': 0.0,
            'basic_path': self.settings.get('basic_path'),
        }


    def lerp(self, lerp, lower, upper):
        if lerp > 1:
            lerp = 1
        elif lerp < -1:
            lerp = -1

        sign = -1 if lerp < 0 else 1
        lerp = abs(lerp)
        value = (1 - lerp) * lower + lerp * upper

        if value == lower:
            return 0
        return value * sign

    def xyr_write(self, x: float, y: float, rot: float):
        control_data = {  # Ensure this is a dictionary
            "translation": {'x': x, 'y': y}, 
            "rotation": {'x': rot},
            "water": 0,
        }  # Note the absence of a comma here

        self.serial_control(control_data)

    def xyrh_write(self, x: float, y: float, rot: float, arm_height: str):
        control_data = {  # Ensure this is a dictionary
            "translation": {'x': x, 'y': y}, 
            "rotation": {'x': rot},
            "water": 0,
            "arm_height": arm_height
        }  # Note the absence of a comma here

        self.serial_control(control_data)



    def xy_state_to_motor_state(self, xy_state: dict) -> dict:
        x = xy_state['translation']['x']
        y = xy_state['translation']['y']
        rot = xy_state['rotation']['x']

        motor_state = {
            'left_front': int(
                self.lerp(
                    x + y - rot,
                    self.MOTOR_SPEED_MIN,
                    self.MOTOR_SPEED_MAX,
                )
            ),
            'right_front': int(
                self.lerp(
                    y - x + rot,
                    self.MOTOR_SPEED_MIN,
                    self.MOTOR_SPEED_MAX,
                )
            ),
            'left_back': int(
                self.lerp(
                    y - x - rot,
                    self.MOTOR_SPEED_MIN,
                    self.MOTOR_SPEED_MAX,
                )
            ),
            'right_back': int(
                self.lerp(
                    y + x + rot,
                    self.MOTOR_SPEED_MIN,
                    self.MOTOR_SPEED_MAX,
                )
            ),
        }
        return motor_state

    def pump(self, val: bool):
        if val:
            print('pumpin!')    
            serial_string = f'p\n'.encode()
            try:

                self.serial_conn.write(serial_string)
            except:
                print("SERIAL WRITE FAILED")
        else:
            print('no longer pumpin!')
            serial_string = f'x\n'.encode()
            try:
                self.serial_conn.write(serial_string)
            except:
                print("SERIAL WRITE FAILED")

    def move_arm(self, val: str):

        if (val == 'l'):
            serial_string = f'l\n'.encode()
            try:
                self.serial_conn.write(serial_string)
            except:
                print("SERIAL WRITE FAILED")
        elif (val == 'm'):

            serial_string = f'm\n'.encode()
            try:
                self.serial_conn.write(serial_string)
            except:
                print("SERIAL WRITE FAILED")

        elif (val == 'h'):
            serial_string = f'h\n'.encode()
            try:
                self.serial_conn.write(serial_string)
            except:
                print("SERIAL WRITE FAILED")

    def update_motor_state(self, motor_state):
        try:
            self.motor_state.update(motor_state)  # = motor_state
        except:
                print("SERIAL WRITE FAILED")

    def write_to_serial(self, motor_state):
        if motor_state != self.motor_state:
            self.update_motor_state(motor_state)
            msv = list(self.motor_state.values())
            serial_string = f'{msv[0]};{msv[2]};{msv[1]};{msv[3]}\n'.encode()
            try:
                self.serial_conn.write(serial_string)
            except:
                print("SERIAL WRITE FAILED")

    def manual(self, control_data):
        self.serial_control(control_data)

    def serial_control(self, control_data):
        motor_state = self.xy_state_to_motor_state(control_data)
        self.write_to_serial(motor_state)
        try:
            arm_height = control_data.get('arm_height')
            self.move_arm(arm_height)


        except:
            self.log("test")

        water = control_data.get('water')
        if water != self.pump_state:
            self.pump_state = water
            self.pump(water)

    def auto(self):
        basic_path = self.state_auto.get('basic_path')
        path_index = self.state_auto.get('path_index')
        current_path = basic_path[path_index]
        current_path_time = self.state_auto.get('current_path_time')
        path_start_time = self.state_auto.get('path_start_time')
        path_time = self.state_auto.get('path_time')

        if path_start_time == 0.0:
            self.state_auto['path_start_time'] = time.time()
            self.state_auto['path_time'] = self.settings.get('basic_path')[0].get('duration')
            return

        self.serial_control(current_path)
        if (time.time() - path_start_time >= path_time):
            self.log(time.time() - path_start_time)
            if (path_index >= len(basic_path)-1):
                self.robot_state = 'manual'
                self.state_auto['path_index'] = 0
                self.state_auto['path_start_time'] = 0.0
                self.state_auto['current_path_time'] = 0.0
                return
            else:
                self.state_auto['path_time'] += basic_path[path_index+1].get('duration')
                self.state_auto['path_index'] += 1

    def auto_2(self):

        arucode_locations = self.arucode_locations_topic.read_data()
        if arucode_locations:
            


            loc = arucode_locations[0][1]
            code_id = arucode_locations[0][0]
            # self.log((int)(loc[0]>0))
            area = arucode_locations[0][2]
            # self.log(area)

            if (area > 14000):
                self.xyr_write(0,-0.1,0)
            elif (area < 10000):
                self.xyr_write(0,0.1,0)
            else:
                if (code_id==0):
                    self.xyrh_write(0,0,0, 'l')
                elif (code_id==1):
                    self.xyrh_write(0,0,0, 'm')
                elif (code_id==2):
                    self.xyrh_write(0,0,0, 'h')
                else:
                     self.xyr_write(0,0,0)
           

            # x = loc[0]
            # if (x > 40):
            #     self.xyr_write(0,0,0.01)
            # elif (x < -40):
            #     self.xyr_write(0,0, -0.01)
            # else:
            #     self.xyr_write(0,0,0)
           

            


    def shutdown(self):
        self.xyrh_write(0,0,0, 'l')
        self.serial_conn.close()

    def run(self, shutdown_flag):
        
        control_data = self.control_data_topic.read_data()
        print(control_data)
        if control_data:
            match control_data.get('mode'):
                case 'auto':
                    self.robot_state = 'auto'
                case 'manual':
                    self.robot_state = 'manual'

        match self.robot_state:
            case 'auto':
                self.auto_2()
                return 1
            case 'manual':
                if (control_data):
                    self.manual(control_data.get('controls'))
                else:
                    # Case for when auto mode ends (it goes back into manual... this can sometimes mean
                    # that there will be no control_data as a controller never connected)
                    self.robot_state = 'auto'
                return 1
            case 'idle':
                if (time.time() - self.__STARTUP_TIME_T__.read_data() > 2):
                    self.robot_state = 'auto' # DONT GO INTO AUTO
                    return 1
            case _:
                return 0
