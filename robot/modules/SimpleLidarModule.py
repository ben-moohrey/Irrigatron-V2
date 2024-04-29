from modules.BaseModule import BaseModule
from pyrplidar import PyRPlidar
import logging
import time
# from roboviz import MapVisualizer


# class LidarModule(BaseModule):
#     def __init__(
#         self,
#         topics,
#         thread_id,
#         settings,
#         LIDAR_DEVICE,
#     ):

class SimpleLidarModule(BaseModule):
    def __init__(self,topics,thread_id,settings,LIDAR_DEVICE="/dev/ttyUSB0"):
        super().__init__(topics, thread_id, settings)
        self.lidar = PyRPlidar()
        self.port = LIDAR_DEVICE
        self.baudrate = 115200
        self.obstructed_min_angle = 140
        self.obstructed_max_angle = 220
        self.min_distance = 400

        self.connect()

    def connect(self):
        self.lidar.connect(port=self.port, baudrate=self.baudrate, timeout=3)
        # self.lidar.set_motor_pwm(self.motor_pwm)
        time.sleep(2)  # Wait for the motor to stabilize

        self.scan_generator = self.lidar.force_scan()

    def run_scan(self):
        obstacle_detected = False
        

        for count, (quality, angle, distance) in enumerate(self.scan_generator()):
            if self.obstructed_min_angle <= angle <= self.obstructed_max_angle and distance > 0 and distance < self.min_distance:
                obstacle_detected = True
                print(f"Obstacle detected at angle {angle} and distance {distance}")
            if count >= 20:  # Limit the number of scans for demonstration
                break




    def disconnect(self):
        self.lidar.disconnect()
        self.lidar.stop()
        self.lidar.set_motor_pwm(0)  # Turn off motor when done

    def shutdown(self):
        self.disconnect()

    def run(self, shutdown_flag):
        
        if self.run_scan():
            print("Obstacle found during scan.")
        else:
            print("No obstacles detected.")
        # self.disconnect()

if __name__ == "__main__":
    lidar_module = LidarModule()
    lidar_module.run()
