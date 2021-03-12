from controller_config import button_names, axis_names

from donkeycar.parts.controller import Joystick, JoystickController


class MyJoystick(Joystick):
    # An interface to a physical joystick available at /dev/input/js0
    def __init__(self, *args, **kwargs):
        super(MyJoystick, self).__init__(*args, **kwargs)

        self.button_names = button_names
        self.axis_names = axis_names


class MyJoystickController(JoystickController):
    # A Controller object that maps inputs to actions
    def __init__(self, *args, **kwargs):
        super(MyJoystickController, self).__init__(*args, **kwargs)

    def init_js(self):
        # attempt to init joystick
        try:
            self.js = MyJoystick(self.dev_fn)
            self.js.init()
        except FileNotFoundError:
            print(self.dev_fn, "not found.")
            self.js = None
        return self.js is not None

    def init_trigger_maps(self):
        # init set of mapping from buttons to function calls

        self.button_down_trigger_map = {
            "LS_BTN": self.emergency_stop,
            "BACK": self.erase_last_N_records,
            "RB": self.increase_max_throttle,
            "LB": self.decrease_max_throttle,
            "LT": self.toggle_manual_recording,
            "X": self.toggle_mode,
            "B": self.toggle_constant_throttle,
        }

        self.axis_trigger_map = {
            "RS_HORIZONTAL": self.set_steering,
            "LS_VERTICAL": self.set_throttle,
        }
