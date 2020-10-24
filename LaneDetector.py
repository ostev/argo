import cv2
import numpy as np
import logging
import math


class LaneDetector(object):
    def __init__(self, debug=False):
        self.debug = debug

        if self.debug == True:
            logging.basicConfig(level=logging.DEBUG)

    @staticmethod
    def find_edges_in_image(frame, debug=False):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        sensitivity = 15
        hue = 130
        lower_blue = np.array([hue - sensitivity, 40, 40])
        upper_blue = np.array([hue + sensitivity, 255, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        if debug == True:
            cv2.imwrite("mask.jpg", mask)

        edges = cv2.Canny(mask, 200, 400)
        cropped_edges = LaneDetector.find_regions_of_interest(edges)

        if debug == True:
            cv2.imwrite("edges.jpg", cropped_edges)
        
        return cropped_edges

    @staticmethod
    def find_regions_of_interest(edges):
        height, width = edges.shape
        mask = np.zeros_like(edges)

        # Only focus on the bottom of the screen.
        polygon = np.array([[
            (0, height * 1 / 3),
            (width, height * 1 / 3),
            (width, height),
            (0, height) 
        ]], np.int32)

        cv2.fillPoly(mask, polygon, 255)
        edges = cv2.bitwise_and(edges, mask)
        return edges

    @staticmethod
    def detect_line_segments(cropped_edges):
        rho = 1
        angle = np.pi / 180
        min_threshold = 50
        min_line_length = 10
        max_line_gap = 14

        line_segments = cv2.HoughLinesP(cropped_edges, rho, angle, min_threshold, np.array([]),
                                        min_line_length, max_line_gap)
        
        return line_segments


    @staticmethod
    def average_slope_intercept(frame, line_segments):
        """
        This function combines line segment into one or two lane lines.
        If all line slopes are less than 0, we have only detected the left lane.
        If all line slopes are greater than 0, we have only detected the right lane
        """
        
        lane_lines = []
        if line_segments is None:
            logging.info("No line segments detected.")
            return lane_lines

        _, width, _ = frame.shape
        left_fit = []
        right_fit = []

        boundary = 1/3
        left_region_boundary = width * (1 - boundary)
        right_region_boundary = width * boundary

        for line_segment in line_segments:
            for x1, y1, x2, y2 in line_segment:
                if x1 == x2:
                    logging.info("skipping vertical line segment (slope=infinity): %s" % line_segment)
                    continue
                fit = np.polyfit((x1, x2), (y1, y2), 1)
                slope = fit[0]
                intercept = fit[1]

                if slope < 0:
                    if x1 < left_region_boundary and x2 < left_region_boundary:
                        left_fit.append((slope, intercept))
                else:
                    if x1 > right_region_boundary and x2 > right_region_boundary:
                        right_fit.append((slope, intercept))

        left_fit_average = np.average(left_fit, axis=0)
        if len(left_fit) > 0:
            lane_lines.append(LaneDetector.make_points(frame, left_fit_average))
        
        right_fit_average = np.average(right_fit, axis=0)
        if len(right_fit) > 0:
            lane_lines.append(LaneDetector.make_points(frame, right_fit_average))

        logging.debug("lane lines:\n%s" % lane_lines)
        return lane_lines

    @staticmethod
    def make_points(frame, line):
        height, width, _ = frame.shape
        slope, intercept = line
        y1 = height # The bottom of the frame.
        y2 = int(y1 * 1 / 2) # Make points from middle of the frame down

        # Bound the coordinates within the frame
        x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
        x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))

        return [[x1, y1, x2, y2]]

    def run(self, image):
            

        edges = LaneDetector.find_edges_in_image(image, debug=self.debug)
        segments = LaneDetector.detect_line_segments(edges)

        logging.debug("line segments:\n%s" % segments)

        if self.debug == True:
            if len(segments) > 0:
                for item in segments:
                    for leftx, boty, rightx, topy in item:
                        graphical_segments = cv2.line(image, (leftx, boty), (rightx,topy), (255, 255, 0), 2)
        
                cv2.imwrite("segments.jpg", graphical_segments)

        lane_lines = LaneDetector.average_slope_intercept(image, segments)

        graphical_lane_lines = display_lines(image, lane_lines)

        if self.debug == True:
            cv2.imwrite("lane_lines.jpg", graphical_lane_lines)

        return lane_lines

class SteeringAngleCalculator(object):
    def __init__(self, debug=False):
        self.debug = debug

        if self.debug == True:
            logging.basicConfig(level=logging.DEBUG)

    def run(self, frame, lane_lines):
        height, width, _ = frame.shape

        if len(lane_lines) == 2:
            _, _, left_x2, _ = lane_lines[0][0]
            _, _, right_x2, _ = lane_lines[1][0]
            mid = int(width / 2)
            x_offset = (left_x2 + right_x2) / 2 - mid
            y_offset = int(height / 2)
        elif len(lane_lines) == 1:
            x1, _, x2, _ = lane_lines[0][0]
            x_offset = x2 - x1
            y_offset = int(height / 2)
        else:
            x_offset = 1
            y_offset = 1

        
        angle_to_mid_radian = math.atan(x_offset / y_offset)
        angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)
        steering_angle = angle_to_mid_deg

        logging.info("predicted steering angle: %s" % steering_angle)

        return steering_angle

def display_lines(frame, lines, line_color=(0, 255, 0), line_width=10):
    line_image = np.zeros_like(frame)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)
    line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
    return line_image

