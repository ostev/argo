from parts import BrickPiSteerDriver, BrickPiTwoWheelClawDriver, Driver


def get_robot():
    robot = BrickPiSteerDriver()
    return robot

def get_claw_robot():
    robot = BrickPiTwoWheelClawDriver()
    return robot

def get_noop_robot():
    robot = Driver()
    return robot