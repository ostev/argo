from Gamepad import Gamepad


class Controller(Gamepad):
    def __init__(self):
        self.names = {
            "BTN_TR2": "RT",
            "BTN_TR": "RB",
            "BTN_TL2": "LT",
            "BTN_TL": "LB",
            "BTN_THUMBL": "LS_BTN",
            "BTN_THUMBR": "RS_BTN",
            "BTN_WEST": "Y",
            "BTN_EAST": "B",
            "BTN_SOUTH": "A",
            "BTN_NORTH": "X",
            "BTN_SELECT": "BACK",
            "BTN_START": "START",
            "ABS_X": "LS_X",
            "ABS_Y": "LS_Y",
            "ABS_Z": "RS_X",
            "ABS_RZ": "RS_Y"
        }

        Gamepad.__init__(self)
