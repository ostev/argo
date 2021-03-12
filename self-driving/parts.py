from typing import Optional
from time import sleep

from donkeycar.utils import map_range

from brickpi3 import BrickPi3


class BrickPiLargeMotor(object):
    def __init__(self, port: int):
        self.bp: BrickPi3 = BrickPi3()

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

    def run_threaded(self):
        pass

    def shutdown(self):
        self.bp.set_motor_power(self.port, 0)


class BrickPiSteering(object):
    def __init__(self, port: int):
        self.bp = BrickPi3()

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

    def run(self, angle):
        if angle > 1 or angle < -1:
            return

        self.angle = map_range(angle, -1, 1, 0, self.max_angle)

        self.bp.set_motor_position(self.port, self.angle)

    def run_threaded(self):
        pass

    def shutdown(self):
        self.bp.set_motor_power(self.port, 0)


def runPair(pair, speed):
    pair[0].run(speed)
    pair[1].run(speed)


class BrickPiThrottle:
    def __init__(self, bp: BrickPi3):
        self.bp = bp

        self.throttle: float = 0
        self.motors = (
            BrickPiLargeMotor(self.bp.PORT_B),
            BrickPiLargeMotor(self.bp.PORT_C),
        )

    def run(self, throttle: float):
        runPair(self.motors, throttle)

    def stop(self):
        runPair(self.motors, 0)

    def close(self):
        self.motors[0].shutdown()
        self.motors[1].shutdown()


class BrickPiDriver:
    def __init__(self):
        self.bp = BrickPi3()

        self.steering = BrickPiSteering(self.bp.PORT_D)
        self.throttle = BrickPiThrottle(self.bp)

    def run(self, steering: float, throttle: float):
        self.steering.run(steering)
        self.throttle.run(throttle)

    def run_threaded(self):
        pass

    def update(self):
        pass

    def shutdown(self):
        self.throttle.shutdown()
        self.steering.shutdown()

        self.bp.reset_all()
