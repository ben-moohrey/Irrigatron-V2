from modules.BaseModule import BaseModule
import RPi.GPIO as GPIO
import time


class StepperModule(BaseModule):
    POSITION_LOW = 0 
    POSITION_MEDIUM = -3000
    POSITION_HIGH = -5000

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

            self.stepper_location_topic.write_data({
                "position": self.position_low,
                "status": "idle"
            })
            
            self.current_position = 0

    def mutate_stepper_topic(self, key, val):
        data = self.stepper_location_topic.read_data()
        data[key] = val
        self.stepper_location_topic.write_data(data)

    def run_stepper(self):
        target_position = self.stepper_location_topic.read_data()['position']  # Assuming read_data() method exists

        if target_position != self.current_position:
            self.mutate_stepper_topic('status', 'moving')
            steps = target_position - self.current_position
            direction = GPIO.HIGH if steps > 0 else GPIO.LOW

            GPIO.output(self.dir_pin, direction)
            GPIO.output(self.sleep_pin, GPIO.HIGH)

            for _ in range(abs(steps)):
                GPIO.output(self.step_pin, GPIO.HIGH)
                time.sleep(0.001)  # Adjust timing for motor speed control
                GPIO.output(self.step_pin, GPIO.LOW)
                time.sleep(0.001)
            
            self.mutate_stepper_topic('status','done')

        self.current_position = target_position
        GPIO.output(self.sleep_pin, GPIO.LOW)

        
    def run(self, shutdown_flag):
        self.run_stepper()

    
    def shutdown(self):
        self.mutate_stepper_topic('position',self.position_low)
        # self.stepper_location_topic.write_data(self.position_low)
        self.log('SHUTTING THE FUCK DOWN BRUH')
        self.run_stepper()
        GPIO.cleanup()

        return 1
        
