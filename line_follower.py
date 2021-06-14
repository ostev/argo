from typing import Optional, Tuple
from PiVideoCapture import PiVideoCapture
from picamera import PiCamera
import cv2
from _thread import start_new_thread
from time import sleep
from enum import Enum

from get_robot import get_robot
from PID import PID
from helpers import map_range


# The lower and upper boundaries of various colours
# in HSV colour space
green_lower = (40, 70, 0)
green_upper = (100, 255, 255)

red_lower = (160, 70, 0)
red_upper = (180, 255, 255)

blue_lower = (80, 70, 0)
blue_upper = (125, 255, 255)

yellow_lower = (10, 70, 0)
yellow_upper = (25, 255, 255)


class Color(Enum):
    green = 0
    red = 1
    blue = 2
    yellow = 3


RawColor = Tuple[int, int, int]

ColorBounds = Tuple[RawColor, RawColor]


def color_bounds(color: Color) -> ColorBounds:
    if color == Color.green:
        return (green_lower, green_upper)
    elif color == Color.red:
        return (red_lower, red_upper)
    elif color == Color.blue:
        return (blue_lower, blue_upper)
    else:
        return (yellow_lower, yellow_upper)


class Intention(Enum):
    pick_up = 0
    deposit = 1


Mode = Tuple[Color, Intention]


def mode_is_pick_up(mode: Mode):
    return mode[1] == Intention.pick_up


def change_mode(mode: Mode):
    if mode[1] == Intention.deposit:
        return (Color(mode[0].value + 1), Intention.pick_up)
    else:
        return (mode[0], Intention.deposit)


def get_mask(hsv, color):
    if color == Color.green:
        return cv2.inRange(hsv, green_lower, green_upper)
    elif color == Color.red:
        return cv2.inRange(hsv, red_lower, red_upper)
    elif color == Color.blue:
        return cv2.inRange(hsv, blue_lower, blue_upper)
    elif color == Color.yellow:
        return cv2.inRange(hsv, yellow_lower, yellow_upper)


def line_steering(pid: PID, frame, targetX: int, color: Color = Color.blue) -> Optional[float]:

    blurred = cv2.GaussianBlur(frame, (5, 5), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask = get_mask(hsv, color)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # # Find the countours (jargon for "outlines") in the
    # # mask and use it to compute the centre of the ball.
    # contours = cv2.findContours(
    #     mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # contours = imutils.grab_contours(contours)
    # center = None

    # if len(contours) > 0:
    #     # Find the largest countour in the mask, then
    #     # use it to compute the minimum enclosing circle
    #     # and centroid
    #     c = max(contours, key=cv2.contourArea)
    #     ((x, y), radius) = cv2.minEnclosingCircle(c)
    #     M = cv2.moments(c)
    #     center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

    #     pos = center

    #     # if radius > 10:
    #     #     cv2.circle(frame, (int(x), int(y)),
    #     #                int(radius), (0, 255, 255), 2)
    #     #     cv2.circle(frame, center, 5, (0, 0, 255), -1)

    #     #     cv2.imwrite("./test.jpg", frame)

    _, contours, _ = cv2.findContours(mask.copy(), 1, cv2.CHAIN_APPROX_NONE)

    if len(contours) > 0:
        # Find largest contour area and image moments
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)

        # Find x-axis centroid using image moments
        cx = int(M['m10']/M['m00'])

        print("targetX - cx: " + str(targetX - cx))

        # cv2.circle(frame, (cx, 20), 5, (0, 0, 255))
        # cv2.imwrite("./test.jpg", blurred)

        update = map_range(
            pid.update(targetX - cx),
            -85,
            103,
            -0.9,
            0.9
        ) * -1
        print("update: " + str(update))

        return update
    else:
        return None


pid = PID(0.8, 0, 0)

mode = (Color.green, Intention.pick_up)

camera = PiCamera(resolution=(192, 108))
camera.vflip = True
camera.hflip = True

sleep(1)

robot = get_robot()

vs = PiVideoCapture(camera, size=(192, 108))

try:
    while True:
        frame = vs.read()
        frame = frame[38:108, 0:]
        steering = line_steering(pid, frame, 104)

        if steering != None:
            robot.run(steering, 0.5)

finally:
    robot.shutdown()
