from XboxController import XboxController
import math
controller = XboxController(0.1)

max_x = -100
max_y = -100
max_add = -100
while True:
    controller.read_input()
