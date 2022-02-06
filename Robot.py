from Motors import Motors
from angle_to_tank import angle_to_tank


class Robot(object):
    def __init__(self, left: Motors, right: Motors, max_speed: float = 1):
        self.left, self.right = left, right
        self.left.max_speed = max_speed
        self.right.max_speed = max_speed

    def go(self, power_left: float, power_right: float):
        self.left.go(power_left)
        self.right.go(power_right)

    def steer(self, angle: int, throttle: float):
        (left, right) = angle_to_tank(angle, throttle)
        self.go(left, right)

    def stop(self):
        self.left.stop()
        self.right.stop()

    def shutdown(self):
        self.left.stop()
        self.right.stop()

    def close(self):
        self.left.close()
        self.right.close()

    def reverse(self):
        self.left.reverse()
        self.right.reverse()

    def forward(self, power: float = 1):
        if power >= 0:
            self.go(power, power)
        else:
            raise ValueError(
                "Power levels below zero are not allowed as inputs to Robot.forward."
            )

    def backward(self, power: float = 1):
        if power >= 0:
            negatedPower: float = power * -1
            self.go(negatedPower, negatedPower)
        else:
            raise ValueError(
                "Power levels below zero are not allowed as inputs to Robot.backward."
            )
