from Gamepad import Gamepad

class Controller(Gamepad):
    def __init__(self, joystickNumber = 0):
        Gamepad.__init__(self, joystickNumber)

        self.buttonNames = {
            7 : "RT",
            5 : "RB",
            6 : "LT",
            4 : "LB",
            10 : "LS_BTN",
            11 : "RS_BTN",
            0 : "Y",
            1 : "B",
            3 : "X",
            2 : "A",
            8 : "BACK",
            9 : "START"
        }

        self.axisNames = {
            1 : "LS_Y",
            0 : "LS_X",
            3 : "RS_Y",
            2 : "RS_X"
        }

        self._setupReverseMaps()
