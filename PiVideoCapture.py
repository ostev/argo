from typing import Tuple

from picamera.array import PiRGBArray
from picamera import PiCamera


class PiVideoCapture(object):
    def __init__(self, camera: PiCamera, size=(192, 108)):
        self.camera = camera
        self.rawCapture = PiRGBArray(self.camera, size=size)

    def read(self, format="bgr"):
        """
        Grab a `numpy` array of frame data from the camera
        """
        self.camera.capture(self.rawCapture, format)
        frame = self.rawCapture.array
        self.rawCapture.truncate(0)
        return frame
