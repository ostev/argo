from gpiozero import Motor
from typing import List

class Motors(object):
    """ Allows you to control a list of motors like a single motor. """
    def __init__(self, motors: List[Motor]):
        self.motors = motors

    def go(self, value: float = 1):
        for motor in self.motors:
            motor.value = value

    def forward(self, power: float = 1):
        if power >= 0 and power <= 1:
            self.go(power)
        else:
            raise ValueError("Power levels below zero are not allowed as inputs to Motors.forward. Supplied power level was: " + str(power))

    def backward(self, power: float = 1):
        if power >= 0 and power <= 1:
            self.go(power * -1)
        else:
            raise ValueError("Power levels below zero are not allowed as inputs to Motors.backward. Supplied power level was: " + str(power))

    def reverse(self):
        for motor in self.motors:
            motor.reverse()
    
    def stop(self):
        for motor in self.motors:
            motor.stop()
    
    def close(self):
        for motor in self.motors:
            motor.close()