import socket
import serial
import json
import threading
import math
import time

# Set up the serial connection to Arduino


# Function to handle client connections
MOTOR_SPEED_MAX = 255
MOTOR_SPEED_MIN = 100
MOTOR_TURN_SPEED = 255

# key_state = {'w': 0, 'a': 0, 's': 0, 'd': 0, 'q': 0, 'e': 0}
# key state = {x: 0, y: 0}
# "TOP_LEFT;BOTTOM_LEFT;TOP_RIGHT;BOTTOM_RIGHT"
# FORWARD: 255;255;255;255
# REVERSE: -255;-255;-255;-255
# LEFT:  -255;255;-255



class RobotSerial:
    def __init__(self, serial_port, baud_rate=115200, write_timer = 0.05):
        self.write_timer


class Robot:
    def __init__(self, serial_port, baud_rate=115200):
        self.serial_conn = serial.Serial(serial_port, baud_rate)
        self.motor_state = {
            "left_front": 0,
            "right_front": 0,
            "left_back": 0,
            "right_back": 0,
        }



        self.pump_state = 0
        self.robot_state = "demo"

        self.power_on_time = time.now()


        #DEMO
        self.state_demo = {
            "state": "forward" # forward, slow_down, water, reverse,
            "fordward":
                "time": 3
                "start_time": None
                "end_time": None


        }
    
    def lerp(self, lerp, lower, upper):
        if (lerp > 1): 
            lerp = 1
        elif (lerp < -1):
            lerp = -1
        
        sign = -1 if lerp < 0 else 1
        
        lerp = abs(lerp)

        value = (1 - lerp) * lower + lerp * upper

        if (value == lower):
            return 0
        return value * sign
    
    def xy_state_to_motor_state(self, xy_state: dict) -> dict:
        x = xy_state['translation']['x']
        y = xy_state['translation']['y']
        rot = xy_state['rotation']['x']
        motor_state = {
            "left_front": int(self.lerp(x+y-rot, MOTOR_SPEED_MIN, MOTOR_SPEED_MAX)),
            "right_front": int(self.lerp(y-x+rot, MOTOR_SPEED_MIN, MOTOR_SPEED_MAX)),
            "left_back": int(self.lerp(y-x-rot, MOTOR_SPEED_MIN, MOTOR_SPEED_MAX)),
            "right_back": int(self.lerp(y+x+rot, MOTOR_SPEED_MIN, MOTOR_SPEED_MAX)),
        }
        print(motor_state)
        return motor_state


    def pump(val: bool):
        if (val):
            serial_string = f"p\n".encode()
            self.serial_conn.write(serial_string)
        else:
            serial_string = f"x\n".encode()
            self.serial_conn.write(serial_string)


    def update_motor_state(self, motor_state):
        self.motor_state.update(motor_state) # = motor_state

    def write_to_serial(self, motor_state):
        if (motor_state != self.motor_state):
            self.update_motor_state(motor_state)
            msv = list(self.motor_state.values())
            serial_string = f"{msv[0]};{msv[2]};{msv[1]};{msv[3]}\n".encode()
            self.serial_conn.write(serial_string)

    # State machine
    def run(self):
        match self.robot_state:
            case "demo":
                self.state_demo = self.demo(self.state_demo)
                return 1

            case _:
                return 0

    # def demo(self, state):

    #     match state['state']:
    #         case "forward"

    #             if 
    #             state['state'] = "slow_down"

    #             state[] 


        








# Server setup
SERVER_IP = "10.144.113.75"
# SERVER_IP = '127.0.0.1'
SERVER_PORT = 8003
SERIAL_PORT = "/dev/ttyACM0" 




def __main__():
    # Create a Robot instance
    robot = Robot(SERIAL_PORT)

    # Create a TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(1)

    try:
        while True:
            print("Waiting for a connection...")
            client_socket, addr = server_socket.accept()
            print("Connected to:", addr)
            while True:
                # Receive data from the client
                data = client_socket.recv(1024)
                # print(data)
                if data:

                    # Update key state and send command to Arduino
                    try:

                        control_data = json.loads(data.decode())
                    except json.decoder.JSONDecodeError as e:
                        continue

                    mode = control_data['mode']

                    if (mode=="controller"):

                        motor_state = robot.xy_state_to_motor_state(control_data)

                        # print(json.dumps(motor_state, indent=4))
                        try:
                            robot.write_to_serial(motor_state)
                        except BaseException as e:
                            print(e)
                            print("FAILED TO WRITE")
                    else:
                        enabled = True
                        while enabled:
                            enabled = robot.run()

                else:
                    break
    except KeyboardInterrupt:
        print("Exiting")
    finally:
        print("Shutting Down Gracefully")
        client_socket.close()
        server_socket.close()
        robot.serial_conn.close()

def test():
    SERIAL_PORT = "/dev/ttyACM0" 
    # serial_conn = serial.Serial(SERIAL_PORT, 115200)
    while True:
        continue
        # serial_conn.write(b'255;0;0;0')

    


if __name__ == "__main__":
    __main__()