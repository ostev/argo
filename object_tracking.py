from collections import deque
from PiVideoCapture import PiVideoCapture
import numpy as np
from picamera import PiCamera
import cv2
import imutils
import time


# The lower and upper boundaries of various colours
# in HSV colour space
green_lower = (29, 86, 6)
green_upper = (64, 255, 255)

def main():
    camera = PiCamera()
    camera.vflip = True

    # Initialise the list of tracked points
    points = deque(maxlen=10)

    vs = PiVideoCapture(camera)

    # Allow the camera time to warm up
    time.sleep(1)

    while True:
        frame = vs.read()

        frame = imutils.resize(frame, width=600)
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # Construct a mask fr the color green, then dilate
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

            if radius > 10:
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
        
        points.appendleft(center)

        vs.clear_buffer()

        cv2.imwrite("./test.jpg", frame)


if __name__ == "__main__":
    main()