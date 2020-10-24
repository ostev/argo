from time import sleep

from gpiozero import Motor

from Motors import Motors
from Robot import Robot
from Controller import Controller
import Gamepad

# Gamepad settings
gamepadType = Controller

buttonExit = "BACK"

left_speed_control = "LS_Y"
right_speed_control = "RS_Y"

def main():
    left_speed: float = 0
    right_speed: float = 0

    left_motors = Motors([Motor(17, 27), Motor(12, 13)])
    right_motors = Motors([Motor(23,22),Motor(16,26)])
    robot = Robot(left_motors, right_motors)

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
        print(eventType)
        print(control)
        print(value)
        # Determine the type
        if eventType == "BUTTON":
            # Button changed
            if control == buttonExit:
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
            print("Left speed: " + str(left_speed))
            print("Right speed: " + str(right_speed))

            robot.go(left_speed, right_speed)

if __name__ == "__main__":
    main()