from gpiozero import Motor

from Robot import Robot
from Motors import Motors

def get_robot():
    left_motors = Motors([Motor(17, 27), Motor(12, 13)])
    right_motors = Motors([Motor(23,22),Motor(16,26)])
    robot = Robot(left_motors, right_motors)
    return robot