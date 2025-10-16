import time
import RPi.GPIO as GPIO
from . import config

class Ultrasonic:
    def __init__(self, trig=None, echo=None):
        self.trig = trig or config.TRIG_PIN
        self.echo = echo or config.ECHO_PIN

    def measure(self, samples=10):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.trig, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)
        distances = []
        try:
            for _ in range(samples):
                GPIO.output(self.trig, False); time.sleep(0.05)
                GPIO.output(self.trig, True); time.sleep(0.00001)
                GPIO.output(self.trig, False)
                pulse_start, pulse_end = time.time(), time.time()
                timeout = time.time() + 0.04
                while GPIO.input(self.echo) == 0 and time.time() < timeout:
                    pulse_start = time.time()
                while GPIO.input(self.echo) == 1 and time.time() < timeout:
                    pulse_end = time.time()
                pulse_duration = pulse_end - pulse_start
                distance_cm = pulse_duration * 17150
                distances.append(distance_cm)
                time.sleep(0.05)
        finally:
            GPIO.cleanup()
        if not distances:
            return None
        return round(sum(distances) / len(distances), 2)
