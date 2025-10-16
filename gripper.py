import time
import RPi.GPIO as GPIO
from . import config

class Gripper:
    def __init__(self, pwm_pin=None):
        self.pin = pwm_pin or config.GRIPPER_PWM_PIN

    def actuate(self, action: str):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin, GPIO.OUT)
        pwm = GPIO.PWM(self.pin, 50)
        try:
            pwm.start(9.5)  # neutral
            time.sleep(0.5)
            if action == "c":
                pwm.ChangeDutyCycle(7.5)
            elif action == "o":
                pwm.ChangeDutyCycle(11.5)
            time.sleep(0.5)
        finally:
            pwm.stop()
            GPIO.cleanup()
