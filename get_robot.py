from parts import BrickPiSteerDriver, \
    BrickPiTwoWheelDriver, \
    BrickPiOneWheelClawDriver, \
    BrickPiOneWheelClawDriverWithGyro, \
    Driver


def get_robot():
    robot = BrickPiSteerDriver()
    return robot


def get_two_wheel_robot():
    robot = BrickPiTwoWheelDriver()
    return robot


def get_claw_robot():
    robot = BrickPiOneWheelClawDriver()
    return robot


def get_claw_gyro_robot():
    return BrickPiOneWheelClawDriverWithGyro()


def get_noop_robot():
    robot = Driver()
    return robot
