from time import sleep
from statistics import mean

from gpiozero import Motor

from Controller import Controller
from get_robot import get_robot, get_claw_robot, get_noop_robot
import Gamepad
from helpers import map_range, clamp, RESET, GREEN

# Gamepad settings
gamepadType = Controller

exit_control = "BACK"
recalibrate_control = "START"
change_mode_to_claw_control = "B"
change_mode_to_steer_control = "Y"

left_speed_control = "LS_Y"
steering_control = "RS_X"

left_control = "LB"
right_control = "RB"

claw_control = "LT"

class Main(object):
    def __init__(self):
        self.throttle: float = 0
        self.steering: float = 0

        self.hasSwitchedMode = False
        self.isInSteerMode = False

        self.is_left = False
        self.is_right = False

        self.robot = get_noop_robot()

    def main(self):

        # Wait for a connection
        if not Gamepad.available():
            print("%sPlease connect your gamepad...%s\n" % (GREEN, RESET))
            while not Gamepad.available():
                sleep(1.0)
        gamepad = gamepadType()
        print("%sGamepad connected...%s\n" % (GREEN, RESET))

        # Handle joystick updates one at a time
        while gamepad.isConnected():
            # Wait for the next event
            eventType, control, value = gamepad.getNextEvent()

            # Determine the type
            if eventType == "BUTTON":
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
                    if self.isInSteerMode or (not self.hasSwitchedMode):
                        print("Changing to claw mode...")
                        self.isInSteerMode = False
                        self.robot = get_claw_robot()

                        self.hasSwitchedMode = True
                elif control == change_mode_to_steer_control:
                    if self.isInSteerMode or (not self.hasSwitchedMode):
                        print("Changing to claw mode...")
                        self.isInSteerMode = True
                        self.robot = get_robot()

                        self.hasSwitchedMode = True
                elif control == claw_control:
                    if not self.isInSteerMode:
                        if value:
                            self.robot.claw.close()
                        else:
                            self.robot.claw.open()
                elif control == left_control:
                    self.is_left = value
                elif control == right_control:
                    self.is_right = value

            elif eventType == "AXIS":
                # Joystick changed
                if control == left_speed_control:
                    self.throttle = value * -1
                elif control == steering_control:
                    if self.isInSteerMode:
                        self.steering = map_range(value, -1, 1, -0.7, 0.7)
                    else:
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
    except KeyboardInterrupt:
        print("%sExiting...%s" % (GREEN, RESET))
        main.robot.shutdown()
