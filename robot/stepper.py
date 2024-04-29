import RPi.GPIO as GPIO
import time

# GPIO Pin Definitions
dir_pin = 33 #pin 33   # Direction Pin
step_pin = 31 #pin 31  # Step Pin
sleep_pin = 29 #pin 29 # Sleep Pin

# Setup GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(dir_pin, GPIO.OUT)
GPIO.setup(step_pin, GPIO.OUT)
GPIO.setup(sleep_pin, GPIO.OUT)

# Motor settings
position_low = 0       # Reference position
position_medium = -3000 # Absolute step position for 'medium'
position_high = -5000   # Absolute step position for 'high'
current_position = position_low # Assume starting at 'low'

# Move to specified absolute position
def move_to_position(target_position):
    global current_position
    steps = target_position - current_position
    direction = GPIO.HIGH if steps > 0 else GPIO.LOW

    GPIO.output(dir_pin, direction)
    GPIO.output(sleep_pin, GPIO.HIGH)

    for _ in range(abs(steps)):
        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(0.001)  # Adjust timing for motor speed control
        GPIO.output(step_pin, GPIO.LOW)
        time.sleep(0.001)

    current_position = target_position
    GPIO.output(sleep_pin, GPIO.LOW)

# Homing function to return to the low position
def home():
    move_to_position(position_low)

# Clean up GPIO pins when done
def cleanup():
    GPIO.cleanup()

# Example usage within the module (for testing)
if __name__ == "__main__":

    try:
        move_to_position(3000)
        # while True:
        #     print('test')
        #     num = input("enter num:")
        #     num = int(num)
        #     move_to_position(num)

    
        
          # Move to high
        # time.sleep(1)                     # Wait for 1 second
        # move_to_position(position_medium) # Move to medium
        # time.sleep(1)                     # Wait for 1 second

    finally:
        #home()
        cleanup()
