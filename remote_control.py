from time import sleep
from statistics import mean

from gpiozero import Motor

from Controller import Controller
from get_robot import get_robot
import Gamepad
from helpers import translate, clamp

# Gamepad settings
gamepadType = Controller

exit_control = "BACK"

left_speed_control = "LS_Y"
steering_control = "RS_X"


def main():
    throttle: float = 0
    previous_throttle: float = 0
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
                    robot.close()
                    break

        elif eventType == "AXIS":
            # Joystick changed
            if control == left_speed_control:
                previous_throttle = throttle
                throttle = value * -1
            elif control == steering_control:
                steering = translate(value, -1, 1, -0.8, 0.8)
            # print("Left speed: " + str(left_speed))
            # print("Right speed: " + str(right_speed))
            robot.run(steering, throttle)


if __name__ == "__main__":
    main()
