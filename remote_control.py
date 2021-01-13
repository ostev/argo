from time import sleep

from gpiozero import Motor

from Motors import Motors
from Robot import Robot
from Controller import Controller
from get_robot import get_robot
import Gamepad
from helpers import translate

# Gamepad settings
gamepadType = Controller

exit_control = "BACK"

left_speed_control = "LS_Y"
steering_control = "RS_X"


def main():
    throttle: float = 0
    steering: float = 0

    robot = get_robot()

    # Wait for a connection
    if not Gamepad.available():
        print("Please connect your gamepad...")
        while not Gamepad.available():
            sleep(1.0)
    gamepad = gamepadType()
    print("Gamepad connected")

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
                    print("=== Exiting ===")
                    break

        elif eventType == "AXIS":
            # Joystick changed
            if control == left_speed_control:
                throttle = value * -1
            elif control == steering_control:
                steering = value * -1
            # print("Left speed: " + str(left_speed))
            # print("Right speed: " + str(right_speed))
            robot.steer(translate(steering * -1, -1, 1, -90, 90), throttle)


if __name__ == "__main__":
    main()
