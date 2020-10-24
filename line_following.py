from LaneDetector import LaneDetector
import cv2
import logging
import numpy as np

def display_lines(frame, lines, line_color=(0, 255, 0), line_width=10):
    line_image = np.zeros_like(frame)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)
    line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
    return line_image

logging.basicConfig(level=logging.DEBUG)
frame = cv2.imread("./test.jpg")
ld = LaneDetector(debug=True)
lines = ld.run(frame)