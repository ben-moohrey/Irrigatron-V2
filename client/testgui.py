import socket
import tkinter as tk
import json
from XboxController import XboxController
import math
import cv2

class JoystickGUI:
    def __init__(
        self, window, server_ip, server_port, controller: None | XboxController
    ):
        self.window = window
        self.server_ip = server_ip
        self.server_port = server_port
        self.controller = controller

		#additional setup for video feed
        self.video_capture = cv2.VideoCapture(4)
        self.video_frame = tk.Label(window)
        self.video_frame.pack(pady=20)

		#invoke video update method
        self.update_video_frame()

        # Establish server connection
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.server_ip, self.server_port))

        # Define joystick representation dimensions
        self.JOY_GUI_SIZE = 200
        self.JOY_CENTER = self.JOY_GUI_SIZE // 2

        # Create joystick GUI components
        self.joy_canvas = tk.Canvas(
            window, width=self.JOY_GUI_SIZE, height=self.JOY_GUI_SIZE, bg="white"
        )
        self.joy_canvas.pack(pady=20)
        self.joy_canvas.create_line(
            self.JOY_CENTER, 0, self.JOY_CENTER, self.JOY_GUI_SIZE, fill="gray"
        )
        self.joy_canvas.create_line(
            0, self.JOY_CENTER, self.JOY_GUI_SIZE, self.JOY_CENTER, fill="gray"
        )

        # Draw outer circle (add this line)
        self.outer_circle = self.joy_canvas.create_oval(
            0,
            0,
            self.JOY_GUI_SIZE,
            self.JOY_GUI_SIZE,
            outline="black",
            width=5
        )

        # Inner circle (knob)
        self.knob = self.joy_canvas.create_oval(
            self.JOY_CENTER - 10,
            self.JOY_CENTER - 10,
            self.JOY_CENTER + 10,
            self.JOY_CENTER + 10,
            fill="red",
        )

        self.keys_pressed = {key: 0 for key in "wasdeqz"}
        self.bind()

        # Joystick data


        self.control_data = {
            "mode": "manual",
            "controls": {
                "translation": {
                    "x": 0,
                    "y": 0,
                },
                "rotation":{
                    "x": 0,
                },
            },
        }

        # Periodic update setup
        self.update_controls()
        self.update_joy_representation()

    def update_video_frame(self):
        ret, frame = self.video_capture.read()
        if ret:

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img - Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_frame.imgtk = imgtk
            self.video_frame.configure(image=imgtk)
	
        self.window.after(5, self.update_video_frame)


    def bind(self):
        self.window.bind("<KeyPress>", lambda event: self.on_key_event(event, 1))
        self.window.bind("<KeyRelease>", lambda event: self.on_key_event(event, 0))

    def unbind(self):
        self.window.unbind("<KeyPress>")
        self.window.unbind("<KeyRelease>")

    def on_key_event(self, event, press_or_release=1):
        key = event.keysym.lower()
        if key in self.keys_pressed:
            self.keys_pressed[key] = press_or_release

    def normalize_sum_to_one(self, x, y):
        total = abs(x) + abs(y)

        # Avoid division by zero
        if total == 0:
            return 0, 0

        if total <= 1:
            return x, y

        # Calculate the scale factor
        scale_factor = 1 / total

        # Scale x and y
        x_new = x * scale_factor
        y_new = y * scale_factor
        return x_new, y_new

    def update_controls(self, recursion=True):
        # First try keyboard
        x = 0
        y = 0
        rot = 0
        z_kb = 0

        keys_pressed = self.keys_pressed

        if 1 in keys_pressed.values():
            x_in = keys_pressed["d"] - keys_pressed["a"]
            y_in = keys_pressed["w"] - keys_pressed["s"]
            x, y = self.normalize_sum_to_one(x_in, y_in)

            z_kb = keys_pressed['z']



            rot = keys_pressed["e"]-keys_pressed["q"]

        elif self.controller:
            self.controller.read_input()
            x_in = self.controller.x_axis_left
            y_in = self.controller.y_axis_left

            rot = self.controller.x_axis_right
            x, y = self.normalize_sum_to_one(x_in, y_in)

        self.control_data['controls']['translation']["x"] = round(x,2)
        self.control_data['controls']['translation']["y"] = round(y,2)
        self.control_data['controls']['rotation']['x'] = round(rot,2)
            

        self.send_control_data()

        if recursion:
            self.window.after(10, self.update_controls)

    def update_joy_representation(self):
        x = self.JOY_CENTER + (self.control_data['controls']['translation']["x"] * self.JOY_CENTER)
        y = self.JOY_CENTER + (-self.control_data['controls']['translation']["y"] * self.JOY_CENTER)

        self.joy_canvas.coords(self.knob, x - 10, y - 10, x + 10, y + 10)
        self.window.after(50, self.update_joy_representation)

    def send_control_data(self):

        serialized_data = json.dumps(self.control_data)
        print(serialized_data)
        self.sock.sendall(serialized_data.encode())

    def close_connection(self):
        self.sock.close()
        self.window.destroy()


# Main window setup
window = tk.Tk()
window.title("Joystick Control")

# Server configuration
SERVER_IP = "127.0.0.1"
# SERVER_IP = '10.144.113.75'
SERVER_PORT = 8003

try:
    controller = XboxController(0.2)
except IOError:
    # Controller Not Connected
    controller = None

# Instantiate and run the joystick GUI
joystick_gui = JoystickGUI(window, SERVER_IP, SERVER_PORT, controller)

# Close the connection when the window is closed
window.protocol("WM_DELETE_WINDOW", joystick_gui.close_connection)

# Start the Tkinter event loop
window.mainloop()
