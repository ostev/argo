
from donkeycar.parts.controller import Joystick, JoystickController


class MyJoystick(Joystick):
    #An interface to a physical joystick available at /dev/input/js0
    def __init__(self, *args, **kwargs):
        super(MyJoystick, self).__init__(*args, **kwargs)

            
        self.button_names = {
            0x134 : 'BTN_Y',
            0x133 : 'BTN_X',
            0x13b : 'BTN_START',
            0x13a : 'BTN_BACK',
            0x130 : 'BTN_A',
            0x131 : 'BTN_B',
            0x137 : 'BTN_RB',
            0x136 : 'BTN_LB',
            0x139 : 'BTN_RT',
            0x138 : 'BTN_LT',
            0x13d : 'BTN_LS',
            0x13e : 'BTN_RS',
        }


        self.axis_names = {
            0x1 : 'LEFT_VERTICAL',
            0x0 : 'LEFT_HORIZONTAL',
            0x5 : 'RIGHT_VERTICAL',
            0x11 : 'PAD_VERTICAL',
            0x10 : 'PAD_HORIZONTAL',
            0x2 : 'RIGHT_HORIZONTAL',
        }



class MyJoystickController(JoystickController):
    #A Controller object that maps inputs to actions
    def __init__(self, *args, **kwargs):
        super(MyJoystickController, self).__init__(*args, **kwargs)


    def init_js(self):
        #attempt to init joystick
        try:
            self.js = MyJoystick(self.dev_fn)
            self.js.init()
        except FileNotFoundError:
            print(self.dev_fn, "not found.")
            self.js = None
        return self.js is not None


    def init_trigger_maps(self):
        #init set of mapping from buttons to function calls
            
        self.button_down_trigger_map = {
            'BTN_RB' : self.increase_max_throttle,
            'BTN_LB' : self.decrease_max_throttle,
            'BTN_RT' : self.toggle_manual_recording,
            'BTN_LT' : self.erase_last_N_records,
            'BTN_LS' : self.emergency_stop,
            'BTN_Y' : self.toggle_mode,
            'BTN_B' : self.toggle_constant_throttle,
        }


        self.axis_trigger_map = {
            'RIGHT_HORIZONTAL' : self.set_steering,
            'LEFT_VERTICAL' : self.set_throttle,
        }


