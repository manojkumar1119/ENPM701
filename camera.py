from picamera2 import Picamera2
from libcamera import Transform
import time
from . import config

class Camera:
    def __init__(self):
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration(
            main={"format": "RGB888", "size": config.CAM_RESOLUTION},
            transform=Transform(vflip=config.VFLIP, hflip=config.HFLIP)
        ))
        self.started = False

    def start(self):
        if not self.started:
            self.picam2.start()
            time.sleep(0.1)
            self.started = True

    def capture(self):
        return self.picam2.capture_array()

    def stop(self):
        if self.started:
            self.picam2.stop()
            self.started = False
