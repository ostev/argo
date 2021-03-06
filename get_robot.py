from parts import BrickPiSteerDriver, \
    BrickPiOneWheelDriver, \
    BrickPiOneWheelClawDriver, \
    BrickPiOneWheelClawDriverWithGyro, \
    BrickPiOneWheelClawDriverWithLaser, \
    Driver


def get_robot():
    robot = BrickPiSteerDriver()
    return robot


def get_pivot_robot():
    robot = BrickPiOneWheelDriver()
    return robot


def get_claw_robot():
    robot = BrickPiOneWheelClawDriver()
    return robot


def get_claw_gyro_robot():
    return BrickPiOneWheelClawDriverWithGyro()


def get_claw_laser_robot():
    return BrickPiOneWheelClawDriverWithLaser()


def get_noop_robot():
    robot = Driver()
    return robot
