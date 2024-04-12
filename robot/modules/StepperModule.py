from modules.BaseModule import BaseModule
import RPi.GPIO as GPIO
import time


class StepperModule(BaseModule):
    def __init__(
        self,
        topics,
        thread_id,
        settings,
        ): 
            super().__init__(topics, thread_id, settings)
            
            self.current_position = 0
            # GPIO Pin Definitions
            self.dir_pin = 33   # Direction Pin
            self.step_pin = 31   # Step Pin
            self.sleep_pin = 29  # Sleep Pin

            # Setup GPIO
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self.dir_pin, GPIO.OUT)
            GPIO.setup(self.step_pin, GPIO.OUT)
            GPIO.setup(self.sleep_pin, GPIO.OUT)

            # Motor settings
            self.position_low = 0       # Reference position
            self.position_medium = -3000 # Absolute step position for 'medium'
            self.position_high = -5000   # Absolute step position for 'high'

            self.stepper_location_topic =  self.topics.get_topic("stepper_location_topic")
            self.stepper_location_topic.write_data(self.position_low)


    def run_stepper(self):
        target_position = self.stepper_location_topic.read_data()  # Assuming read_data() method exists

        if target_position != self.current_position:
            steps = target_position - self.current_position
            direction = GPIO.HIGH if steps > 0 else GPIO.LOW

            GPIO.output(self.dir_pin, self.direction)
            GPIO.output(self.sleep_pin, GPIO.HIGH)

            for _ in range(abs(self.steps)):
                GPIO.output(self.step_pin, GPIO.HIGH)
                time.sleep(0.001)  # Adjust timing for motor speed control
                GPIO.output(self.step_pin, GPIO.LOW)
                time.sleep(0.001)

        self.current_position = target_position
        GPIO.output(self.sleep_pin, GPIO.LOW)

        
    def run(self, shutdown_flag):
        self.run_stepper()

    
    def shutdown(self):
        self.stepper_location_topic.write_data(self.position_low)
        self.run_stepper()
        GPIO.cleanup()

        return 1
        
