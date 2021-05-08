from time import sleep

from picamera import PiCamera

import cv2
import imutils

from PiVideoCapture import PiVideoCapture

from get_robot import get_claw_robot
from PID import PID
from helpers import map_range

blue_lower = (102, 70, 0)
blue_upper = (125, 255, 255)

camera = PiCamera(resolution=(320, 208))
camera.vflip = True
camera.hflip = True

# # Initialise the list of tracked points
# points = deque(maxlen=10)

vs = PiVideoCapture(camera)

# Allow the camera time to warm up
sleep(1)

target = (140, 104)
pos = (0, 0)

pid = PID(0.8, 0, 0)

robot = get_claw_robot()

try:
    while True:
        frame = vs.read()

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

            # print(pos)

            if radius > 10:
                cv2.circle(frame, (int(x), int(y)),
                           int(radius), (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
        else:
            robot.stop()
            break

        update = map_range(
            pid.update(target[0] - pos[0]),
            -120,
            120,
            -1,
            1
        ) * -1
        print(update)
        print(pid.update(target[0] - pos[0]))

        cv2.imwrite("./test.jpg", frame)
finally:
    robot.shutdown()
