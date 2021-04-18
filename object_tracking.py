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
green_lower = (50, 0, 0)
green_upper = (100, 255, 255)

red_lower = (320, 0, 0)
red_upper = (360, 0, 0)

blue_lower = (190, 0, 0)
blue_upper = (250, 255, 255)

class Mode(Enum):
    pick_up_green = 0
    deposit_green = 1
    pick_up_red = 2
    deposit_red = 3
    pick_up_blue = 4
    deposit_blue = 5

class Main(object):
    def shutdown(self):
        self.robot.shutdown()
        sys.exit()

    def main(self):
        self.robot = get_claw_gyro_robot()
        is_in_range = (False, False)
        pos = (0, 0)
        target = (220, 335)

        ticks_since_grabbed = 0

        mode = Mode.pick_up_green
        
        pid = PID(0.7, 0, 0)

        camera = PiCamera()
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
        self.robot.rotate_to(90, 1)
        self.robot.run_dps(0, 700)
        sleep(1.5)
        self.robot.stop()

        while True:
            frame = vs.read()
            vs.clear_buffer()

            frame = imutils.resize(frame, width=600)
            blurred = cv2.GaussianBlur(frame, (11, 11), 0)
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

            # Construct a mask for the relevant color, then dilate
            # and erode the image to remove any remaining small blobs.
            if mode == Mode.pick_up_green:
                mask = cv2.inRange(hsv, green_lower, green_upper)
            elif mode == Mode.pick_up_blue:
                mask = cv2.inRange(hsv, blue_lower, blue_upper)
            elif mode == Mode.pick_up_red:
                mask = cv2.inRange(hsv, red_lower, red_upper)

            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)

            # Find the countours (jargon for "outlines") in the
            # mask and use it to compute the centre of the ball.
            contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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

                if mode == Mode.pick_up_green:
                    is_in_range = (center[0] > 110 and center[0] < 320, center[1] > 360)
                elif mode == Mode.deposit_green:
                    is_in_range = (center[0] > 110 and center[0] < 320, center[1] > 20)

                pos = center

                # print(center)

                if radius > 10:
                    cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)

            if is_in_range[1] and is_in_range[0]:
                if mode == Mode.pick_up_green \
                    or mode == Mode.pick_up_blue \
                    or mode == Mode.pick_up_red:

                    self.robot.claw.close()
                    self.robot.stop()

                    ticks_since_grabbed += 1
                    
                    if ticks_since_grabbed > 3:
                        mode = Mode.deposit_green \
                            if mode == Mode.pick_up_green \
                            else (Mode.deposit_red \
                                if mode == Mode.pick_up_red \
                                else Mode.deposit_blue)
                elif mode == Mode.deposit_green:
                    self.robot.stop()

                    self.robot.claw.close()

                    self.robot.rotate_to(90, 0.4)
                    self.robot.run_dps(0, -600)
                    sleep(2)
                    self.robot.stop()
                    sleep(0.07)
                    self.robot.rotate_to(0, 1)
                    self.robot.stop()
                    sleep(0.07)
                    self.robot.run_dps(0, 300)
                    sleep(1)
        
                    self.robot.stop()
                    self.robot.claw.open()

                    sleep(1)

                    mode = Mode.pick_up_red

                    self.robot.run_dps(0, -400)
                    sleep(1)
                    self.robot.rotate_to(125, 1)
                    self.robot.run_dps(0, 600)
                    sleep(1.6)
            else:
                ticks_since_grabbed = 0

                self.robot.claw.open()

                update = map_range(
                        pid.update(target[0] - pos[0]),
                        -130,
                        130,
                        -1,
                        1
                    ) * -1
                self.robot.run(update, 0.3)


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
