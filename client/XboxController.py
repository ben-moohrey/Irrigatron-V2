import hid

class XboxController:
    VENDOR_ID = 1118  # Microsoft
    PRODUCT_ID = 2835  # Xbox One S controller
    
    def __init__(self, deadzone = 0):
        self.gamepad = hid.device()
        self.gamepad.open(self.VENDOR_ID, self.PRODUCT_ID)
        self.gamepad.set_nonblocking(True)
        self.deadzone = deadzone
        self.init_input()
        

    def init_input(self):
        self.a_button = 0
        self.b_button = 0
        self.x_button = 0
        self.y_button = 0
        self.rb_button = 0
        self.lb_button = 0
        self.up_dpad    = 0
        self.right_dpad = 0
        self.left_dpad  = 0
        self.down_dpad  = 0
        self.l_trigger_raw = 0
        self.r_trigger_raw = 0
        self.x_axis_left_raw = 0
        self.y_axis_left_raw = 32767.5
        self.x_axis_right_raw = 32767.5
        self.y_axis_right_raw = 32767.5
        self.x_axis_left = 0
        self.y_axis_left = 0
        self.x_axis_right = 0
        self.y_axis_right = 0


    def printer(self, show_hex = False):

        print(f"A button: {'Pressed' if self.a_button else 'Released'}")
        print(f"B button: {'Pressed' if self.b_button else 'Released'}")
        print(f"X button: {'Pressed' if self.x_button else 'Released'}")
        print(f"Y button: {'Pressed' if self.y_button else 'Released'}")
        print(f"RB button: {'Pressed' if self.rb_button else 'Released'}")
        print(f"LB button: {'Pressed' if self.lb_button else 'Released'}")
        print(f"JOY LEFT X Axis: {self.x_axis_left_raw}, Y Axis: {self.y_axis_left_raw}")
        print(f"JOY RIGHT X Axis: {self.x_axis_right_raw}, Y Axis: {self.y_axis_right_raw}")
        print(f"Right Trigger: {self.l_trigger_raw}")
        print(f"Left Trigger: {self.r_trigger_raw}")

    def read_input(self):
        try:
            report = self.gamepad.read(64)
        except OSError as e:
            print(e)
            return
        if report:
            self.parse_report(report)
            self.normalize()


    def parse_report(self, report):


        self.a_button = int(report[14] & 0x1 > 0)
        self.b_button = int(report[14] & 0x2 > 0)
        self.x_button = int(report[14] & 0x8 > 0)
        self.y_button = int(report[14] & 0x10 > 0)
        self.rb_button = int(report[14] & 0x80 > 0)
        self.lb_button = int(report[14] & 0x40 > 0)

        # d-pad
        self.up_dpad    = int(report[13] & 0x1 > 0)
        self.right_dpad = int(report[13] & 0x3 > 0)
        self.left_dpad  = int(report[13] & 0x7 > 0)
        self.down_dpad  = int(report[13] & 0x5 > 0)
    
        # Triger
        self.l_trigger_raw = (report[9] | (report[10] << 8)) # / 0x3ff
        self.r_trigger_raw = (report[11] | (report[12] << 8)) # / 0x3ff

        # Joy Sticks
        self.x_axis_left_raw = report[1] | (report[2] << 8)
        self.y_axis_left_raw = report[3] | (report[4] << 8)
        self.x_axis_right_raw = report[5] | (report[6] << 8)
        self.y_axis_right_raw = report[7] | (report[8] << 8)


    def normalize(self):
        self.l_trigger = self.l_trigger_raw / 0x3ff
        self.r_trigger = self.r_trigger_raw / 0x3ff

        self.x_axis_left = (self.x_axis_left_raw - 32767.5) / (32767.5)
        self.y_axis_left = (self.y_axis_left_raw - 32767.5) / (32767.5)
        self.x_axis_right = (self.x_axis_right_raw - 32767.5) / (32767.5)
        self.y_axis_right = (self.y_axis_right_raw - 32767.5) / (32767.5)

        if abs(self.x_axis_left) < self.deadzone:
            self.x_axis_left = 0
        if abs(self.y_axis_left) < self.deadzone:
            self.y_axis_left = 0
        if abs(self.x_axis_right) < self.deadzone:
            self.x_axis_right = 0
        if abs(self.y_axis_left) < self.deadzone:
            self.y_axis_left = 0

        self.y_axis_right *= -1
        self.y_axis_left *= -1
        


    def close(self):
        self.gamepad.close()
