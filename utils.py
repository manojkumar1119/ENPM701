import RPi.GPIO as GPIO
from contextlib import contextmanager

GPIO.setwarnings(False)

@contextmanager
def gpio_mode_board():
    try:
        GPIO.setmode(GPIO.BOARD)
        yield
    finally:
        GPIO.cleanup()

def clamp(val, lo, hi):
    if val < lo: return lo
    if val > hi: return hi
    return val
