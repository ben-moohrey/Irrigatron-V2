# from classes.serial import serial
import serial
from modules.BaseModule import BaseModule
from modules.StepperModule import StepperModule
from utils.PlantDatabase import PlantDatabase
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
        self.arucode_topic = self.topics.get_topic("arucode_topic")
        self.stepper_location_topic =  self.topics.get_topic("stepper_location_topic")
        self.server_response_data_topic = topics.get_topic('server_response_data_topic')


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

        self.state_auto_2 = {
            'state': 'wander',
            'water_timer': time.time(),
            'current_code': -1,
        }

        self.pumpin = False

        self.plantDatabase = PlantDatabase('/home/irrigatron/Irrigatron-V2/robot/data/database.json')

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
        if val and not self.pump_state:
            self.log('pumpin!')    
            serial_string = f'p\n'.encode()
            try:
                self.serial_conn.write(serial_string)
                self.pump_state = 1
            except:
                self.log("SERIAL WRITE FAILED")
        elif not val and self.pump_state:
            self.log('no longer pumpin!')
            self.pumpin = False
            serial_string = f'x\n'.encode()
            try:
                self.serial_conn.write(serial_string)
                self.pump_state = 0
            except:
                self.log("SERIAL WRITE FAILED")

    def move_arm(self, val: str):
        return
        if (val == 'l'):
            serial_string = f'l\n'.encode()
            try:
                self.serial_conn.write(serial_string)
            except:
                self.log("SERIAL WRITE FAILED")
        elif (val == 'm'):

            serial_string = f'm\n'.encode()
            try:
                self.serial_conn.write(serial_string)
            except:
                self.log("SERIAL WRITE FAILED")

        elif (val == 'h'):
            serial_string = f'h\n'.encode()
            try:
                self.serial_conn.write(serial_string)
            except:
                self.log("SERIAL WRITE FAILED")

    def update_motor_state(self, motor_state):
        try:
            self.motor_state.update(motor_state)  # = motor_state
        except:
                self.log("SERIAL WRITE FAILED")

    def write_to_serial(self, motor_state):
        # self.log("WRITING TO SERIAL")
        if motor_state != self.motor_state:
            self.update_motor_state(motor_state)
            msv = list(self.motor_state.values())
            serial_string = f'{msv[0]};{msv[2]};{msv[1]};{msv[3]}\n'.encode()
            try:
                self.serial_conn.write(serial_string)
            except:
                self.log("SERIAL WRITE FAILED")

    def manual(self, control_data):
        self.serial_control(control_data)

    def serial_control(self, control_data):
        #self.log("Bruh")
        motor_state = self.xy_state_to_motor_state(control_data)
        self.write_to_serial(motor_state)
        try:
            arm_height = control_data.get('arm_height')
            self.move_arm(arm_height)


        except:
            self.log("test")

        water = control_data.get('water')
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
    def get_from_id(self, id: int, information):
        for info in information:
            if info[0] == id:
                return info
    def auto_2(self):
        
        change_state = lambda s : self.state_auto_2.update({'state': s})
        match self.state_auto_2['state']:

            case 'water':

                water_timer = self.state_auto_2['water_timer']
                self.pump(1)
                if (time.time()-water_timer > 5):
                    plant_info = self.plantDatabase.get_plant(self.state_auto_2['current_code'])
                    self.plantDatabase.set_is_watered(self.state_auto_2['current_code'], True)
                    self.pump(0)
                    change_state('wander')
                    self.log("YOU HAVE 2 SECS TO MOVE THE SHIT")
                    time.sleep(2)



                # self.log("watering")
                # time.sleep(2)
                # change_state('arm')
                # self.log("GOING BACK TO ARM")
                return 0

            case 'arm':



                stepper_data = self.stepper_location_topic.read_data()
                stepper_status = stepper_data['status']
                stepper_position = stepper_data['position']
                
                # if (stepper_position==StepperModule.POSITION_LOW):
                #     stepper_status = 'done'

                if (stepper_status == 'idle'):
                    aruco_information = self.arucode_topic.read_data()

                    if (aruco_information is None or len(aruco_information) == 0):
                        change_state('wander')
                        return
                    
                    plant_info = self.plantDatabase.get_plant(self.state_auto_2['current_code'])

                    height = plant_info['height']
                    if (height=='low'):
                        # stepper_data['position'] = StepperModule.POSITION_LOW

                        stepper_status='done'
                    elif (height=='medium'):
                        stepper_data['position'] = StepperModule.POSITION_MEDIUM
                    elif (height=='high'):
                        stepper_data['position'] = StepperModule.POSITION_HIGH
                        
                   

                if (stepper_status == 'done'):
                    stepper_data['status'] = 'idle'
                    self.state_auto_2['water_timer'] = time.time()
                    change_state('water')

                self.stepper_location_topic.write_data(stepper_data)
                return 0
            
            case 'code':
                
                aruco_information = self.arucode_topic.read_data()
                if aruco_information is not None:
                    
                    # self.log(arucode_locations)
                    
                    
                    if len(aruco_information) == 0:
                        change_state('wander')
                        self.log("CHANING STATES")
                        return 0
                    if (self.state_auto_2['current_code'] not in [item[0] for item in aruco_information]):
                        self.log('CHANING BACK.. NO MORE ID')
                        change_state('wander')
                        return 0
                    

                    info = self.get_from_id(self.state_auto_2['current_code'], aruco_information)
                    code_id = info[0]
                    distance = info[1]
                    # self.log((int)(loc[0]>0))
                    euler_angle = info[2]
                    normalized_x = info[3]
                    # self.log(area)
            
                    x_write = 0
                    y_write = 0
                    r_write = 0
                    speed=0.75 #5
                    #self.log("distance",distance)
                    if (distance > 0.48):
                        # self.xyr_write(0, 0.1,0)
                        y_write=speed
                    elif (distance < 0.25):
                        # self.xyr_write(0,-0.1,0)
                        y_write=-speed
                    #self.log(euler_angle)
                    if (euler_angle > 10):
                        x_write=-speed*1.5
                    elif (euler_angle < -50):
                        x_write=speed*1.5

                    # THIS WORKS
                    if (normalized_x > 0.3):
                        r_write=speed
                    elif (normalized_x < -0.3):
                        r_write=-speed

                    if (x_write==0 and y_write==0 and r_write==0):
                        change_state('arm')
                    self.xyr_write(x_write,y_write,r_write)


                return 0
            case 'wander':
                self.xyr_write(0,0,0.2)
                arucode_locations = self.arucode_topic.read_data()


                # self.log(arucode_locations)
                # self.log('testing')
                if arucode_locations is not None and len(arucode_locations) > 0:
                    needs_watering = self.plantDatabase.get_needs_watering()
                    # self.log(needs_watering)
                    for id in [sub_list[0] for sub_list in arucode_locations]:
                        # print(list(map(lambda x: x["aruco_code"], needs_watering)))
                        self.log(id)
                        if (id in list(map(lambda x: x["aruco_code"], needs_watering))):
                            self.log("CHANGING STATES")
                            self.state_auto_2['current_code'] = id
                            self.plantDatabase.set('current_code', int(id))

                           
                            change_state('code')
                            return 0
                    return 1


                    
                    # print('test')
                return 0

                    
           

            # x = loc[0]
            # if (x > 40):
            #     self.xyr_write(0,0,0.01)
            # elif (x < -40):
            #     self.xyr_write(0,0, -0.01)
            # else:
            #     self.xyr_write(0,0,0)
           

            


    def shutdown(self):
        self.xyrh_write(0,0,0, 'l')
        self.pump(0)
        self.plantDatabase.reset_is_watered()
        self.plantDatabase.save()
        self.serial_conn.close()

    def run(self, shutdown_flag):
        #self.log("BRUH")
        # self.state_auto_2['current_code']
        control_data = self.control_data_topic.read_data()
        
        self.server_response_data_topic.write_data(self.state_auto_2['current_code'])
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
                if (time.time() - self.__STARTUP_TIME_T__.read_data() > 9999):
                    self.robot_state = 'auto' # DONT GO INTO AUTO
                    return 1
            case _:
                return 0
