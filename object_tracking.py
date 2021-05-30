from typing import Optional, Tuple
from PiVideoCapture import PiVideoCapture
from picamera import PiCamera
import cv2
import imutils
from time import sleep
from enum import Enum

from get_robot import get_claw_gyro_robot
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
    pos = (0, 0)
    target = (targetX, 0.430)

    blurred = cv2.GaussianBlur(frame, (11, 1), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask = get_mask(hsv, color)
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

        # if radius > 10:
        #     cv2.circle(frame, (int(x), int(y)),
        #                int(radius), (0, 255, 255), 2)
        #     cv2.circle(frame, center, 5, (0, 0, 255), -1)

        #     cv2.imwrite("./test.jpg", frame)
    else:
        return None

    # update = map_range(
    #     pid.update(target[0] - pos[0]),
    #     -120,
    #     120,
    #     -1,
    #     1
    # ) * -1

    if pos[0] < target[0] - 50:
        return -1
    elif pos[0] > target[0] + 50:
        return 1
    else:
        return 0


class Main(object):
    def main(self):
        is_in_range = (False, False)
        self.pos = (0, 0)
        target = (117, 141)

        self.ticks_since_grabbed = 0

        mode = (Color.green, Intention.pick_up)

        pid = PID(0.7, 0.015, 0)

        pid2 = PID(0.8, 0.02, 0)

        camera = PiCamera(resolution=(320, 208))
        camera.vflip = True
        camera.hflip = True

        self.robot = get_claw_gyro_robot()

        # # Initialise the list of tracked points
        # points = deque(maxlen=10)

        vs = PiVideoCapture(camera)

        # Allow the camera time to warm up
        sleep(1)

        self.robot.run_dps(0, -300)
        sleep(1)
        self.robot.stop()
        self.robot.rotate_to(140, 0.4, 3)
        self.robot.run_dps(0, 750)
        sleep(0.3)
        self.robot.stop()

        while True:
            frame = vs.read()

            blurred = cv2.GaussianBlur(frame, (11, 1), 0)
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

            if mode_is_pick_up(mode):
                # Construct a mask for the relevant color, then dilate
                # and erode the image to remove any remaining small blobs.
                mask = get_mask(hsv, mode[0])

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
                    center = (int(M["m10"] / M["m00"]),
                              int(M["m01"] / M["m00"]))

                    is_in_range = (
                        center[0] > 50 and center[0] < 154, center[1] > 175)

                    self.pos = center
                    print(self.pos)

                    if radius > 10:
                        cv2.circle(frame, (int(x), int(y)),
                                   int(radius), (0, 255, 255), 2)
                        cv2.circle(frame, center, 5, (0, 0, 255), -1)

            print(is_in_range)

            if is_in_range[1] and is_in_range[0]:
                if mode_is_pick_up(mode):

                    self.robot.claw.close()
                    self.robot.stop()

                    self.ticks_since_grabbed += 1

                    if self.ticks_since_grabbed > 1:
                        mode = change_mode(mode)

                        is_in_range = (False, False)
                        self.ticks_since_grabbed = 0

            if mode == (Color.green, Intention.deposit):
                self.robot.stop()

                self.robot.claw.close()

                self.robot.run_dps(0, -600)
                sleep(2.3)
                self.robot.stop()
                sleep(0.07)
                self.robot.rotate_to(90, 0.4, 3)

                while True:
                    frame = vs.read()
                    steering = line_steering(pid2, frame, 0.404)

                    if steering != None:
                        self.robot.run(steering, 0.5)
                    else:
                        self.robot.stop()
                        break

                self.robot.claw.open_partial()

                mode = change_mode(mode)

                self.robot.run_dps(0, -700)

                self.robot.rotate_to(210, 0.4, 3)
                self.robot.claw.open()

                pid.reset()
                pid2.reset()

            elif mode == (Color.red, Intention.deposit):
                self.robot.stop()
                self.robot.claw.close()

                self.robot.rotate_to(180, 0.4, 3)
                self.robot.run_dps(0, -700)
                sleep(2)
                self.robot.stop()

                self.robot.rotate_to(90, 0.4, 3)

                while True:
                    frame = vs.read()
                    steering = line_steering(pid2, frame, 200)

                    if steering != None:
                        self.robot.run(steering, 0.5)
                    else:
                        self.robot.stop()
                        break

                self.robot.claw.open_partial()

                sleep(0.5)

                mode = change_mode(mode)

                self.robot.run_dps(0, -700)
                sleep(1.52)
                self.robot.rotate_to(222, 0.4, 3)
                self.robot.claw.open()

            elif mode == (Color.blue, Intention.deposit):
                self.robot.stop()
                self.robot.claw.close()

                self.robot.rotate_to(180, 0.4, 3)
                self.robot.run_dps(0, -600)
                sleep(1.24)
                self.robot.stop()

                self.robot.rotate_to(90, 0.4, 3)

                while True:
                    frame = vs.read()
                    steering = line_steering(pid2, frame, 0.412, Color.yellow)

                    if steering != None:
                        self.robot.run(steering, 0.5)
                    else:
                        self.robot.stop()
                        break

                self.robot.stop()
                self.robot.claw.open_partial()

                sleep(0.5)

                self.robot.run_dps(0, -700)
                sleep(0.7)
                self.robot.stop()

                break

            else:
                self.robot.claw.open()

                if self.pos[0] < target[0] - 50:
                    update = -1
                elif self.pos[0] > target[0] + 50:
                    update = 1
                else:
                    update = 0

                if self.pos[1] < (target[1] - 30):
                    self.robot.run(update, 0.7)
                elif self.pos[1] < (target[1] - 20):
                    self.robot.run(update, 0.4)
                else:
                    self.robot.run(update, 0.3)

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
