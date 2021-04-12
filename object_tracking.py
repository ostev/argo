from collections import deque
from PiVideoCapture import PiVideoCapture
import numpy as np
from picamera import PiCamera
import cv2
import imutils
import time
import sys

from get_robot import get_claw_robot
from PID import PID
from helpers import map_range

# The lower and upper boundaries of various colours
# in HSV colour space
green_lower = (50, 0, 0)
green_upper = (90, 255, 255)


class Main(object):
    def shutdown(self):
        self.robot.shutdown()
        sys.exit()

    def main(self):
        self.robot = get_claw_robot()
        is_in_range = (False, False)
        pos = (0, 0)
        target = (220, 335)
        
        pid = PID(0.7, 0, 0)

        camera = PiCamera()
        camera.vflip = True
        camera.hflip = True

        # # Initialise the list of tracked points
        # points = deque(maxlen=10)

        vs = PiVideoCapture(camera)

        # Allow the camera time to warm up
        time.sleep(1)

        while True:
            frame = vs.read()
            vs.clear_buffer()

            frame = imutils.resize(frame, width=600)
            blurred = cv2.GaussianBlur(frame, (11, 11), 0)
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

            # Construct a mask for the color green, then dilate
            # and erode the image to remove any small blobs left.
            mask = cv2.inRange(hsv, green_lower, green_upper)
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

                is_in_range = (center[0] > 110 and center[0] < 320, center[1] > 360)

                pos = center

                # print(center)

                if radius > 10:
                    cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)

            #speed = map_range(clamp(error[0] * kp, 0, 600), 0, 600, 0, 1)

            if is_in_range[1] and is_in_range[0]:
                self.robot.claw.close()
                self.robot.stop()
            else:
                self.robot.claw.open()

                # if not is_in_range[0]:
                #     if x < 220:
                #         self.robot.turn_left(0.3)
                #     else:
                #         self.robot.turn_right(0.3)
                update = map_range(pid.update(target[0] - pos[0]), -130, 130, -1, 1) * -1
                # if not is_in_range[1]:
                #     self.robot.run(update, 0.3)
                # else:
                #     self.robot.run(update, 0)
                self.robot.run(update, 0.3)


            # points.appendleft(center)


            # cv2.imwrite("./test.jpg", frame)


if __name__ == "__main__":
    try:
        main = Main()
        main.main()
    finally:
        print("Exiting...")
        main.robot.shutdown()
    # main = Main()
    # main.main()