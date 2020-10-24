from typing import Tuple

from picamera.array import PiRGBArray
from picamera import PiCamera

class PiVideoCapture(object):
    def __init__(self, camera: PiCamera, buffer_size: Tuple[int, int]):
        self.camera = camera
        self.rawCapture = PiRGBArray(self.camera, size=buffer_size)
    
    def read(self):
        self.camera.capture(self.rawCapture, format="bgr")
        return self.rawCapture.array
    
    def clear_buffer(self):
        self.rawCapture.truncate(0)