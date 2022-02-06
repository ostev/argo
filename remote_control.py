from time import sleep
from enum import Enum

from Controller import Controller
from get_robot import get_robot
from Gamepad import EventType
from helpers import map_range, clamp, RESET, GREEN

# Gamepad settings
gamepadType = Controller

exit_control = "BACK"
recalibrate_control = "START"
change_mode_to_noop_control = "A"
change_mode_to_claw_control = "B"
change_mode_to_steer_control = "Y"
change_mode_to_claw_laser_control = "X"

left_speed_control = "LS_Y"
steering_control = "RS_X"

claw_control = "LT"
laser_control = "RB"


class Mode(Enum):
    noop = 0
    steer = 1
    claw = 2
    claw_laser = 3


class Main(object):
    def __init__(self):
        self.throttle: float = 0
        self.steering: float = 0

        self.mode = Mode.steer

        self.is_left = False
        self.is_right = False

        self.robot = get_robot()

    def main(self):
        gamepad = Controller()

        while True:
            # Wait for the next event
            event = gamepad.get_next_event()

            if event != None:
                eventType, control, value = event
                # Determine the type
                if eventType == EventType.key:
                    # Button changed
                    if control == exit_control:
                        # Exit button (event on press)
                        if value:
                            print("\n%sExiting...%s\n" % (GREEN, RESET))
                            self.robot.shutdown()
                            break

                    elif control == change_mode_to_steer_control:
                        if not (self.mode == Mode.steer):
                            print("Changing to steer mode...")
                            self.mode = Mode.steer
                            self.robot = get_robot()


                elif eventType == EventType.axis:
                    print(control)
                    # Joystick changed
                    if control == left_speed_control:
                        self.throttle = value
                        print(self.throttle)
                    elif control == steering_control:
                        self.steering = value
                        print(self.steering)
                    # print("Left speed: " + str(left_speed))
                    # print("Right speed: " + str(right_speed))

                    self.robot.steer(self.steering, self.throttle)


if __name__ == "__main__":
    main = Main()

    try:
        main.main()
    finally:
        print("%sExiting...%s" % (GREEN, RESET))
        main.robot.shutdown()
