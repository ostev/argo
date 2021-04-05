from time import sleep
from statistics import mean

from gpiozero import Motor

from Controller import Controller
from get_robot import get_robot, get_claw_robot
import Gamepad
from helpers import map_range, clamp, RESET, GREEN

# Gamepad settings
gamepadType = Controller

exit_control = "BACK"
recalibrate_control = "START"

left_speed_control = "LS_Y"
steering_control = "RS_X"


class Main(object):
    def __init__(self):
        self.throttle: float = 0
        self.steering: float = 0

        self.mode = "steer"

        self.robot = get_robot()

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

            elif eventType == "AXIS":
                # Joystick changed
                if control == left_speed_control:
                    self.throttle = value * -1
                elif control == steering_control:
                    self.steering = map_range(value, -1, 1, -0.8, 0.8)
                # print("Left speed: " + str(left_speed))
                # print("Right speed: " + str(right_speed))
                self.robot.run(self.steering, self.throttle)


if __name__ == "__main__":
    main = Main()

    try:
        main.main()
    except KeyboardInterrupt:
        print("%sExiting...%s" % (GREEN, RESET))
        main.robot.shutdown()
