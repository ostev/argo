from gpiozero import Motor

from Robot import Robot
from Motors import Motors

def get_robot():
    left_motors = Motors([Motor(5, 6), Motor(23, 22)])
    right_motors = Motors([Motor(26, 13),Motor(17, 27)])
    robot = Robot(left_motors, right_motors)
    return robot
