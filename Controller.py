from Gamepad import Gamepad


class Controller(Gamepad):
    def __init__(self, joystickNumber=0):
        Gamepad.__init__(self, joystickNumber)

        self.buttonNames = {
            9: "RT",
            7: "RB",
            8: "LT",
            6: "LB",
            13: "LS_BTN",
            14: "RS_BTN",
            4: "Y",
            1: "B",
            3: "X",
            0: "A",
            10: "BACK",
            11: "START",
        }

        self.axisNames = {1: "LS_Y", 0: "LS_X", 3: "RS_Y", 2: "RS_X"}

        self._setupReverseMaps()
