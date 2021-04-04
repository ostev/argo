from typing import Optional, Tuple
from time import sleep

from helpers import map_range, CYAN, RESET

from brickpi3 import BrickPi3


class BrickPiDriveMotor(object):
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

    def shutdown(self):
        self.bp.set_motor_power(self.port, 0)


class BrickPiSteering(object):
    def __init__(self, port: int, bp: BrickPi3):
        self.bp = bp

        self.angle = 0.0
        self.max_angle = 0.0

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

    def shutdown(self):
        self.bp.set_motor_power(self.port, 0)


class BrickPiThrottle(object):
    def __init__(self, bp: BrickPi3):
        self.bp = bp

        self.throttle: float = 0
        self.motors = (
            BrickPiDriveMotor(self.bp.PORT_B, self.bp),
            BrickPiDriveMotor(self.bp.PORT_C, self.bp),
        )

    def run(self, throttle: float):
        for motor in self.motors:
            motor.run(throttle)

    def stop(self):
        for motor in self.motors:
            motor.stop()

    def shutdown(self):
        for motor in self.motors:
            motor.shutdown()


class BrickPiSteerDriver(object):
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

    def shutdown(self):
        self.throttle.shutdown()
        self.steering.shutdown()

        self.bp.reset_all()


class BrickPiClaw(object):
    def __init__(self, port: int, bp: BrickPi3):
        self.bp = bp
        self.port = port

    def close(self):
        self.bp.set_motor_power(self.port, 30)
    
    def open(self):
        self.bp.set_motor_power(self.port, -30)
        sleep(0.1)
        self.shutdown()
    
    def shutdown(self):
        self.bp.set_motor_power(self.port, 0)

class BrickPiTwoWheelClawDriver(object):
    def __init__(self):
        self.bp = BrickPi3()

        print("%sInitialising robot...%s" % (CYAN, RESET))

        self.motors = (
            BrickPiDriveMotor(self.bp.PORT_B, self.bp),
            BrickPiDriveMotor(self.bp.PORT_C, self.bp)
        )
        self.claw = BrickPiClaw(self.bp.PORT_D, self.bp)
        print("%sReady.%s\n" % (CYAN, RESET))
    
    def run(self, speed: Tuple[float, float]):
        for x in speed:
            if x > 1 or x < -1:
                raise ValueError(
                    "throttle must be between 1(forward)\
                    and -1(reverse)"
                )
        
        self.motors[0].run(speed[0])
        self.motors[1].run(speed[1])
    
    def stop(self):
        self.run((0, 0))
    
    def shutdown(self):
        self.motors[0].shutdown()
        self.motors[1].shutdown()
        self.claw.shutdown()
        
        self.bp.reset_all()

