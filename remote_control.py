from time import sleep

from gpiozero import Motor

from Motors import Motors
from Robot import Robot
from Controller import Controller
from get_robot import get_robot
import Gamepad

# Gamepad settings
gamepadType = Controller

exit_control = "BACK"

left_speed_control = "LS_Y"
right_speed_control = "RS_Y"

def main():
    left_speed: float = 0
    right_speed: float = 0

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
                left_speed = value * -1
            elif control == right_speed_control:
                right_speed = value * -1
            # print("Left speed: " + str(left_speed))
            # print("Right speed: " + str(right_speed))

            robot.go(left_speed, right_speed)

if __name__ == "__main__":
    main()
