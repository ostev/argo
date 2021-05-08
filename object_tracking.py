from typing import Optional
from collections import deque
from PiVideoCapture import PiVideoCapture
import numpy as np
from picamera import PiCamera
import cv2
import imutils
from time import sleep
import sys
from enum import Enum

from get_robot import get_claw_gyro_robot
from PID import PID
from helpers import map_range


# The lower and upper boundaries of various colours
# in HSV colour space
green_lower = (50, 70, 0)
green_upper = (100, 255, 255)

red_lower = (160, 70, 0)
red_upper = (180, 255, 255)

blue_lower = (80, 70, 0)
blue_upper = (125, 255, 255)


def change_mode(mode):
    if mode == Mode.pick_up_green:
        return Mode.deposit_green
    elif mode == Mode.pick_up_red:
        return Mode.deposit_red
    elif mode == Mode.pick_up_blue:
        return Mode.deposit_blue


def get_mask(hsv, mode):
    if mode == Mode.pick_up_green:
        return cv2.inRange(hsv, green_lower, green_upper)
    elif mode == Mode.pick_up_red:
        return cv2.inRange(hsv, red_lower, red_upper)
    elif mode == Mode.pick_up_blue:
        return cv2.inRange(hsv, blue_lower, blue_upper)
    else:
        raise ValueError("Incorrect mode")


def mode_is_pick_up(mode):
    return mode == Mode.pick_up_green \
        or mode == Mode.pick_up_red \
        or mode == Mode.pick_up_blue


class Mode(Enum):
    pick_up_green = 0
    deposit_green = 1
    pick_up_red = 2
    deposit_red = 3
    pick_up_blue = 4
    deposit_blue = 5


def line_steering(pid: PID, frame) -> Optional[float]:
    pos = (0, 0)

    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, blue_lower, blue_upper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # Find the countours (jargon for "outlines") in the
    # mask and use it to compute the centre of the ball.
    contours = cv2.findContours(
        mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    center = None

    if len(contours) > 0:
        # Find the largest countour in the mask, then
        # use it to compute the minimum enclosing circle
        # and centroid
        c = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        pos = center
    else:
        return None

    update = map_range(
        pid.update(target[0] - pos[0]),
        -120,
        120,
        -1,
        1
    ) * -1

    if radius > 10:
        cv2.circle(frame, (int(x), int(y)),
                   int(radius), (0, 255, 255), 2)
        cv2.circle(frame, center, 5, (0, 0, 255), -1)
    cv2.imwrite("./test.jpg", frame)

    return update


class Main(object):
    def shutdown(self):
        self.robot.shutdown()
        sys.exit()

    def main(self):
        self.robot = get_claw_gyro_robot()
        is_in_range = (False, False)
        self.pos = (0, 0)
        target = (117, 174)

        self.ticks_since_grabbed = 0

        mode = Mode.pick_up_green

        pid = PID(0.7, 0, 0)

        pid2 = PID(0.8, 0, 0)

        camera = PiCamera(resolution=(320, 208))
        camera.vflip = True
        camera.hflip = True

        # # Initialise the list of tracked points
        # points = deque(maxlen=10)

        vs = PiVideoCapture(camera)

        # Allow the camera time to warm up
        sleep(1)

        self.robot.run_dps(0, -300)
        sleep(1)
        self.robot.stop()
        self.robot.rotate_to(90, 0.7)
        self.robot.run_dps(0, 700)
        sleep(2)
        self.robot.stop()

        while True:
            frame = vs.read()

            blurred = cv2.GaussianBlur(frame, (11, 11), 0)
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

            if mode_is_pick_up(mode):
                # Construct a mask for the relevant color, then dilate
                # and erode the image to remove any remaining small blobs.
                mask = get_mask(hsv, mode)

                mask = cv2.erode(mask, None, iterations=2)
                mask = cv2.dilate(mask, None, iterations=2)

                # Find the countours (jargon for "outlines") in the
                # mask and use it to compute the centre of the ball.
                contours = cv2.findContours(
                    mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                contours = imutils.grab_contours(contours)
                center = None
                print(mode)

                if len(contours) > 0:
                    # Find the largest countour in the mask, then
                    # use it to compute the minimum enclosing circle
                    # and centroid
                    c = max(contours, key=cv2.contourArea)
                    ((x, y), radius) = cv2.minEnclosingCircle(c)
                    M = cv2.moments(c)
                    center = (int(M["m10"] / M["m00"]),
                              int(M["m01"] / M["m00"]))

                    is_in_range = (
                        center[0] > 110 and center[0] < 320, center[1] > 360)

                    self.pos = center

                    print(self.pos)

                    # print(center)

                    if radius > 10:
                        cv2.circle(frame, (int(x), int(y)),
                                   int(radius), (0, 255, 255), 2)
                        cv2.circle(frame, center, 5, (0, 0, 255), -1)

            if is_in_range[1] and is_in_range[0]:
                if mode_is_pick_up(mode):

                    print(mode)

                    self.robot.claw.close()
                    self.robot.stop()

                    self.ticks_since_grabbed += 1
                    print(self.ticks_since_grabbed)

                    if self.ticks_since_grabbed > 1:
                        mode = change_mode(mode)
                        print(str(mode) + "b")
                        is_in_range = (False, False)
                        self.ticks_since_grabbed = 0

            if mode == Mode.deposit_green:
                self.robot.stop()

                self.robot.claw.close()

                self.robot.rotate_to(90, 0.4, 0)
                self.robot.run_dps(0, -600)
                sleep(2.1)
                self.robot.stop()
                sleep(0.07)
                self.robot.rotate_to(0, 0.4)
                self.robot.stop()

                while True:
                    frame = vs.read()
                    steering = line_steering(pid2, frame)

                    if steering != None:
                        self.robot.run(steering, 0.3)
                    else:
                        self.robot.stop()
                        break

                self.robot.claw.open()

                sleep(0.5)

                mode = Mode.pick_up_red

                self.robot.run_dps(0, -700)
                sleep(0.75)
                self.robot.rotate_to(125, 0.7, 1)
                self.robot.run_dps(0, 600)
                sleep(1.6)

                pid.reset()
                pid2.reset()

            elif mode == Mode.deposit_red:
                self.robot.stop()
                self.robot.claw.close()

                self.robot.rotate_to(90, 0.4)
                self.robot.run_dps(0, -700)
                sleep(2.38)
                self.robot.stop()
                sleep(0.07)
                self.robot.rotate_to(0, 0.4)
                self.robot.stop()
                sleep(0.07)
                self.robot.run_dps(0, 700)
                sleep(2.45)

                self.robot.stop()
                self.robot.claw.open()

                sleep(0.5)

                mode = Mode.pick_up_blue

                self.robot.run_dps(0, -700)
                sleep(1.52)
                self.robot.rotate_to(132, 0.7, 1)
                self.robot.run_dps(0, 600)
                sleep(2)

            elif mode == Mode.deposit_blue:
                self.robot.stop()
                self.robot.claw.close()

                self.robot.rotate_to(90, 0.4)
                self.robot.run_dps(0, -600)
                sleep(1.24)
                self.robot.stop()
                sleep(0.07)
                self.robot.rotate_to(0, 0.4)
                self.robot.stop()
                sleep(0.07)
                self.robot.run_dps(0, 700)
                sleep(4.32)

                self.robot.stop()
                self.robot.claw.open()

                sleep(0.5)

                break

            else:
                ticks_since_grabbed = 0

                self.robot.claw.open()

                update = map_range(
                    pid.update(target[0] - self.pos[0]),
                    -130,
                    130,
                    -1,
                    1
                ) * -1
                print(update)
                self.robot.run(update, 0.1)

            # points.appendleft(center)

            cv2.imwrite("./test.jpg", frame)


if __name__ == "__main__":
    try:
        main = Main()
        main.main()
    finally:
        print("Exiting...")
        main.robot.shutdown()
    # main = Main()
    # main.main()
