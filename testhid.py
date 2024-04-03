from client.XboxController import XboxController
import math
controller = XboxController(0.1)

max_x = -100
max_y = -100
max_add = -100
while True:
    controller.read_input()
    x = abs(controller.x_axis_left)
    y = abs(controller.y_axis_left)
    if (x > max_x):
        max_x = x
        print("New X:",max_x)

    if (y > max_y):
        max_y = y
        print("New Y:",max_y)

    if (math.sqrt(x*x+y*y) > max_add):
        max_add = math.sqrt(x*x+y*y)
        print("New add:",max_add)