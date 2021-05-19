from time import sleep
from enum import Enum

from gpiozero import Motor

from Controller import Controller
from get_robot import get_robot, get_claw_robot, get_noop_robot
from Gamepad import EventType
from helpers import map_range, clamp, RESET, GREEN

# Gamepad settings
gamepadType = Controller

exit_control = "BACK"
recalibrate_control = "START"
change_mode_to_noop_control = "A"
change_mode_to_claw_control = "B"
change_mode_to_steer_control = "Y"
change_mode_to_claw_partial_control = "X"

left_speed_control = "LS_Y"
steering_control = "RS_X"

left_control = "LB"
right_control = "RB"

claw_control = "LT"


class Mode(Enum):
    noop = 0
    steer = 1
    claw = 2
    claw_partial = 3


class Main(object):
    def __init__(self):
        self.throttle: float = 0
        self.steering: float = 0

        self.mode = Mode.noop

        self.is_left = False
        self.is_right = False

        self.robot = get_noop_robot()

    def main(self):
        gamepad = Controller()

        while True:
            # Wait for the next event
            eventType, control, value = gamepad.get_next_event()

            # Determine the type
            if eventType == EventType.key:
                # Button changed
                if control == exit_control:
                    # Exit button (event on press)
                    if value:
                        print("\n%sExiting...%s\n" % (GREEN, RESET))
                        self.robot.shutdown()
                        break
                elif control == recalibrate_control:
                    if value:
                        print("%sRecalibrating...%s\n" % (GREEN, RESET))
                        self.robot.calibrate()
                elif control == change_mode_to_claw_control:
                    if not (self.mode == Mode.claw):
                        print("Changing to claw mode...")
                        self.mode = Mode.claw
                        self.robot = get_claw_robot()

                elif control == change_mode_to_steer_control:
                    if not (self.mode == Mode.steer):
                        print("Changing to steer mode...")
                        self.mode = Mode.steer
                        self.robot = get_robot()

                elif control == change_mode_to_noop_control:
                    if not (self.mode == Mode.noop):
                        print("Changing to no-op mode...")
                        self.mode = Mode.noop
                        self.robot = get_noop_robot()

                elif control == change_mode_to_claw_partial_control:
                    if not (self.mode == Mode.claw_partial):
                        print("Changing to partial-close claw mode...")
                        self.mode = Mode.claw_partial
                        self.robot = get_claw_robot()

                elif control == claw_control:
                    if self.mode == Mode.claw_partial:
                        if value:
                            self.robot.claw.set_position(40)
                        else:
                            self.robot.claw.open()
                    else:
                        if value:
                            self.robot.claw.close()
                        else:
                            self.robot.claw.open()
                elif control == left_control:
                    self.is_left = value
                    if self.is_left:
                        self.robot.turn_left(self.throttle)
                elif control == right_control:
                    self.is_right = value
                    if self.is_right:
                        self.robot.turn_right(self.throttle)
                    else:
                        self.robot.run(self.steering, self.throttle)

            elif eventType == EventType.axis:
                # Joystick changed
                if control == left_speed_control:
                    self.throttle = value * -1
                elif control == steering_control:
                    self.steering = value
                # print("Left speed: " + str(left_speed))
                # print("Right speed: " + str(right_speed))

                if self.is_left:
                    self.robot.turn_left(self.throttle)
                elif self.is_right:
                    self.robot.turn_right(self.throttle)
                else:
                    self.robot.run(self.steering, self.throttle)


if __name__ == "__main__":
    main = Main()

    try:
        main.main()
    finally:
        print("%sExiting...%s" % (GREEN, RESET))
        main.robot.shutdown()
