from typing import Optional
from time import sleep

from helpers import map_range, CYAN, RESET

from brickpi3 import BrickPi3


class BrickPiLargeMotor(object):
    def __init__(self, port: int, bp: BrickPi3):
        self.bp: BrickPi3 = bp

        self.speed: float = 0

        self.port = port

    def run(self, speed: float) -> None:

        self.speed = speed

        if speed > 1 or speed < -1:
            raise ValueError(
                "throttle must be between 1(forward)\
                 and -1(reverse)"
            )

        self.bp.set_motor_power(self.port, self.speed * -100)

    def stop(self):
        self.run(0)

    def close(self):
        self.bp.set_motor_power(self.port, 0)


class BrickPiSteering(object):
    def __init__(self, port: int, bp: BrickPi3):
        self.bp = bp

        self.angle: float = 0
        self.max_angle: float = 0

        self.port = port
        self.calibrate()

    def calibrate(self):
        # Calibrate the steering
        self.bp.set_motor_power(self.port, 70)
        sleep(1)
        self.bp.set_motor_power(self.port, 0)
        sleep(1)
        self.bp.reset_motor_encoder(self.port)

        self.bp.set_motor_power(self.port, -70)
        sleep(1)
        self.bp.set_motor_power(self.port, 0)
        sleep(1)
        self.max_angle = self.bp.get_motor_encoder(self.port)

        self.run(0)

    def run(self, angle: float):
        if angle > 1 or angle < -1:
            return

        self.angle = map_range(angle, -1, 1, 0, self.max_angle)

        self.bp.set_motor_position(self.port, self.angle)

    def run_threaded(self):
        pass

    def close(self):
        self.bp.set_motor_power(self.port, 0)


def runPair(pair, speed):
    pair[0].run(speed)
    pair[1].run(speed)


class BrickPiThrottle:
    def __init__(self, bp: BrickPi3):
        self.bp = bp

        self.throttle: float = 0
        self.motors = (
            BrickPiLargeMotor(self.bp.PORT_B, self.bp),
            BrickPiLargeMotor(self.bp.PORT_C, self.bp),
        )

    def run(self, throttle: float):
        runPair(self.motors, throttle)

    def stop(self):
        self.motors[0].stop()
        self.motors[1].stop()

    def close(self):
        self.motors[0].close()
        self.motors[1].close()


class BrickPiDriver:
    def __init__(self):
        self.bp = BrickPi3()

        print("%sInitialising robot...%s" % (CYAN, RESET))

        self.steering = BrickPiSteering(self.bp.PORT_D, self.bp)
        self.throttle = BrickPiThrottle(self.bp)

        print("%sReady.%s\n" % (CYAN, RESET))

    def calibrate(self):
        self.steering.calibrate()

    def run(self, steering: float, throttle: float):
        self.steering.run(steering)
        self.throttle.run(throttle)

    def stop(self):
        self.throttle.stop()

    def close(self):
        self.throttle.close()
        self.steering.close()

        self.bp.reset_all()