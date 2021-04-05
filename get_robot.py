from parts import BrickPiSteerDriver, BrickPiTwoWheelClawDriver


def get_robot():
    robot = BrickPiSteerDriver()
    return robot

def get_claw_robot():
    robot = BrickPiTwoWheelClawDriver()
    return robot