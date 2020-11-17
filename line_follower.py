from time import sleep

from PiVideoCapture import PiVideoCapture
from Robot import Robot
from Motors import Motors

from gpiozero import Motor

from picamera.array import PiRGBArray
from picamera import PiCamera

import numpy as np
import cv2

camera = PiCamera()
camera.rotation = 180
camera.framerate = 20
camera.resolution = (192, 112)

cap = PiVideoCapture(camera)

sleep(0.5)

while True:
    # left_motors = Motors([Motor(17, 27), Motor(12, 13)])
    # right_motors = Motors([Motor(23,22),Motor(16,26)])
    # robot = Robot(left_motors, right_motors)

    image = cap.read()
    cv2.imwrite("test.jpg", image)

    # Create a key that breaks the loop
    key = cv2.waitKey(1) & 0xFF

    # Convert the image to greyscale
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Blur it
    blurred = cv2.GaussianBlur(grayscale, (5, 5), 0)
    # Get the threshold
    _, threshold = cv2.threshold(
        blurred,
        100,
        255,
        cv2.THRESH_BINARY_INV
    )

    # Erode to elimate unnecessary noise
    eroded = cv2.erode(threshold, None, iterations=2)
    # Dilate to restore some eroded parts of the image
    dilated = cv2.dilate(eroded, None, iterations=2)

    # Find all the contours in the mask
    _, contours, _ = cv2.findContours(
        dilated.copy(),
        1,
        cv2.CHAIN_APPROX_NONE
    )

    # Find the geometic center on the x-axis of the
    # largest contour and adjust power accordingly to
    # recenter the camera on the geometic centre of the
    # line.
    if len(contours) > 0:
        # Find the largest contour
        c = max(contours, key = cv2.contourArea)
        # Find the image moments of `c`
        # Just a quick explainer (for myself, more than
        # anything): an "moment" in this context is the
        # weighted average of the intensities of all the
        # pixels in an image. It seems to be a way to
        # find the most intense areas. I don't know
        # a terribly large amount about them myself,
        # I figured them out enough to write this code.
        # See
        # https://stackoverflow.com/questions/22470902#22472044
        # and
        # https://en.wikipedia.org/wiki/Image_moment
        # for more information.
        M = cv2.moments(c)

        # Find the geometric centre (centroid) on the
        # x-axis using the image moments we previously
        # calculated.
        cx = int(M["m10"] / M["m00"])

        if cx >= 150:
            print("Left!")
            # robot.go(-1, 1)
        elif cx < 150 and cx > 40:
            print("Right!")
            # robot.go(1, -1)
        elif cx <= 40:
            print("Keep on driving... 🐟🚗")
            # robot.go(0.7, 0.7)
        
        # Stop if "q" is pressed
        if key == ord("q"):
            break
        
        # We need to do this to prevent the buffer
        # from overflowing. If we don't do this,
        # the result is a crash.
        cap.clear_buffer()

        # Wait a bit
        sleep(0.1)
