from typing import Optional, Tuple
from time import sleep
import threading

from helpers import map_range, angle_to_tank, clamp

from brickpi3 import BrickPi3


class Claw(object):
    def calibrate(self):
        pass

    def open(self):
        pass

    def close(self):
        pass

    def set_position(self, pos: int):
        pass


class Driver(object):
    def __init__(self):
        self.claw = Claw()

    def calibrate(self):
        pass

    def run(self, steering, throttle):
        pass

    def run_dps(self, steering, throttle):
        pass

    def turn_left(self, throttle: float):
        pass

    def turn_right(self, throttle: float):
        pass

    def stop(self):
        pass

    def shutdown(self):
        pass


class BrickPiDriveMotor(object):
    def __init__(self, port: int, bp: BrickPi3):
        self.bp: BrickPi3 = bp

        self.port = port

    def run(self, speed: float):
        if speed > 1 or speed < -1:
            raise ValueError(
                "throttle must be between 1(forward)\
                 and -1(reverse)"
            )

        self.bp.set_motor_power(self.port, speed * -100)

    def run_dps(self, dps: int):
        self.bp.set_motor_dps(self.port, dps * -1)

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

    def run_dps(self, dps: int):
        for motor in self.motors:
            motor.run_dps(dps)

    def stop(self):
        for motor in self.motors:
            motor.stop()

    def shutdown(self):
        for motor in self.motors:
            motor.shutdown()


class BrickPiSteerDriver(Driver):
    def __init__(self):
        self.bp = BrickPi3()

        self.steering = BrickPiSteering(self.bp.PORT_D, self.bp)
        self.throttle = BrickPiThrottle(self.bp)

    def calibrate(self):
        self.steering.calibrate()

    def steer(self, steering: float):
        angle = map_range(steering, -1, 1, -0.8, 0.8)
        self.steering.run(angle)

    def run(self, steering: float, throttle: float):
        self.steer(steering)
        self.throttle.run(throttle)

    def run_dps(self, steering: float, dps: int):
        self.steer(steering)
        self.throttle.run_dps(dps)

    def stop(self):
        self.throttle.stop()

    def turn_left(self, throttle):
        if throttle > -0.4 and throttle < 0.4:
            self.steer(-1)
        else:
            self.steer(-0.5)
        self.throttle.run(throttle)

    def turn_right(self, throttle):
        if throttle > -0.4 and throttle < 0.4:
            self.steer(1)
        else:
            self.steer(0.5)

        self.throttle.run(throttle)

    def shutdown(self):
        self.throttle.shutdown()
        self.steering.shutdown()

        self.bp.reset_all()


class BrickPiClaw(Claw):
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

    def set_position(self, pos: int):
        self.bp.set_motor_position(self.port, self.open_position + pos)

    def shutdown(self):
        self.bp.set_motor_power(self.port, 0)


class BrickPiTwoWheelDriver(Driver):
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

        steer = map_range(steering, -1, 1, -90, 90)
        (left, right) = angle_to_tank(steer, throttle)

        self.motors[0].run(left)
        self.motors[1].run(right)

    """Can only go straight. `steering` ignored."""

    def run_dps(self, steering, dps: int):
        self.motors[0].run_dps(dps)
        self.motors[1].run_dps(dps)

    def stop(self):
        self.run(0, 0)

    def turn_left(self, throttle: float):
        self.motors[0].run(throttle * -1)
        self.motors[1].run(throttle)

    def turn_right(self, throttle: float):
        self.motors[0].run(throttle)
        self.motors[1].run(throttle * -1)

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


class BrickPiGyro:
    def __init__(self, port: int, bp: BrickPi3):
        self.bp = bp
        self.port = port

        self.bp.set_sensor_type(
            self.port,
            self.bp.SENSOR_TYPE.EV3_GYRO_ABS_DPS
        )

        # Wait for the sensor to warm up...
        sleep(5)

        self.calibrate()

    def calibrate(self):
        self.starting_angle = 0
        self.starting_angle = self.get()[0]

    def get(self) -> Tuple[int, int]:
        data = self.bp.get_sensor(self.port)

        return (data[0] - self.starting_angle, data[1])


class BrickPiTwoWheelClawDriverWithGyro(BrickPiTwoWheelClawDriver):
    def __init__(self):
        super().__init__()
        self.gyro = BrickPiGyro(self.bp.PORT_3, self.bp)

    def calibrate(self):
        super().calibrate()
        self.gyro.calibrate()

    def rotate_to(self, targetAngle: int, throttle: float, acceptableError=0):
        while True:
            current_angle = self.gyro.get()[0]
            angle_left = current_angle - targetAngle

            if angle_left >= (0 - acceptableError) \
                    and angle_left <= acceptableError:
                break
            else:
                if angle_left < 0:
                    self.turn_right(throttle)
                else:
                    self.turn_left(throttle)

            sleep(0.05)

        self.stop()
