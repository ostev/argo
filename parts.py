from typing import Optional
from time import sleep
import threading

from helpers import map_range, angle_to_tank

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

        self.steering = BrickPiSteering(self.bp.PORT_D, self.bp)
        self.throttle = BrickPiThrottle(self.bp)

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
        
        self.closed_position: float = 0
        self.open_position: float = 0

        self.calibrate()
    
    def calibrate(self):
        self.close()
        sleep(0.4)
        self.closed_position = self.bp.get_motor_encoder(self.port)
        self.open_position = self.closed_position - 50
        self.open()

    def close(self):
        self.bp.set_motor_power(self.port, 40)
    
    def open(self):
        self.bp.set_motor_position(self.port, self.open_position)
    
    def shutdown(self):
        self.bp.set_motor_power(self.port, 0)

class BrickPiTwoWheelDriver(object):
    def __init__(self):
        self.bp = BrickPi3()

        self.motors = (
            BrickPiDriveMotor(self.bp.PORT_B, self.bp),
            BrickPiDriveMotor(self.bp.PORT_C, self.bp)
        )
    
    def run(self, steering: float, throttle: float):
        if throttle > 1 or throttle < -1:
            raise ValueError(
                "throttle must be between 1(forward)\
                and -1(reverse)"
            )
        
        left = 0.0
        right = 0.0

        if steering == 1 or steering == -1:
            (left, right) = (throttle, throttle * -1)
        else:
            steer = map_range(steering, -1, 1, -90, 90)

            (left, right) = angle_to_tank(steer, throttle)
        
        self.motors[0].run(left)
        self.motors[1].run(right)
    
    def stop(self):
        self.run(0, 0)
    
    def shutdown(self):
        self.motors[0].shutdown()
        self.motors[1].shutdown()
        
        self.bp.reset_all()

class BrickPiTwoWheelClawDriver(BrickPiTwoWheelDriver):
    def __init__(self):
        super().__init__()
        self.claw = BrickPiClaw(self.bp.PORT_D, self.bp)
    
    def calibrate(self):
        self.claw.calibrate()

    def shutdown(self):
        self.claw.shutdown()
        super().shutdown()

class NoOpClaw(object):
    def calibrate(self):
        pass

    def open(self):
        pass

    def close(self):
        pass

class NoOpDriver(object):
    def __init__(self):
        self.claw = NoOpClaw()

    def calibrate(self):
        pass

    def run(self, x, y):
        pass
    
    def stop(self):
        pass

    def shutdown(self):
        pass