from typing import Tuple

from picamera.array import PiRGBArray
from picamera import PiCamera


class PiVideoCapture(object):
    def __init__(self, camera: PiCamera):
        self.camera = camera
        self.rawCapture = PiRGBArray(self.camera)

    def read(self, format="bgr"):
        """
        Grab a numpy array of frame data from the camera

        Make sure to call `clear_buffer` when you're done.
        """
        self.camera.capture(self.rawCapture, format)
        return self.rawCapture.array

    def clear_buffer(self):
        """
        This must be called after a read to clear the camera's
        buffer, otherwise a crash will result.
        """
        self.rawCapture.truncate(0)
