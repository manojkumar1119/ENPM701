from dataclasses import dataclass
import os
import numpy as np

# Camera
CAM_RESOLUTION = (640, 480)
VFLIP = True
HFLIP = True
FOCAL_LENGTH_PX = 1244  # focal length in pixels

# GPIO Pins (BOARD mode)
@dataclass(frozen=True)
class MotorPins:
    LEFT_FORWARD: int = 33
    LEFT_BACKWARD: int = 37
    RIGHT_FORWARD: int = 31
    RIGHT_BACKWARD: int = 35

MOTOR_PINS = MotorPins()

# Encoders
ENCODER_LEFT_PIN = 12   # BOARD numbering
ENCODER_RIGHT_PIN = 7

# Ultrasonic
TRIG_PIN = 16
ECHO_PIN = 18

# Gripper (servo)
GRIPPER_PWM_PIN = 36

# Control Params
ROTATE_KP = 1.0
ROTATE_KD = 0.3
ROTATE_MIN_PWM = 60
ROTATE_MAX_PWM = 90
ROTATE_LOW_ERROR_MAX_PWM = 75
ROTATE_LOW_ERROR_MIN_PWM = 60

MOVE_BASE_DC = 70  # base duty for straight motion

# World geometry
FIELD_X_CM = 304.8
CAM_TO_GRIPPER_CM = 9.5
BLOCK_WIDTH_CM = 3.7

# Goals
GOAL_X = 243.84
GOAL_Y = 60.96
START_X = 60.96 - 8.7
START_Y = 60.96 + CAM_TO_GRIPPER_CM - (BLOCK_WIDTH_CM / 2)

# Vision HSV ranges
HSV_RANGES = {
    "r": [([0, 75, 139], [10, 255, 255]), ([170, 75, 139], [180, 255, 255])],
    "g": [([23, 132, 179], [69, 255, 255])],
    "b": [([79, 134, 85], [111, 255, 255])],
}

# Distance model cy->cm
CY_VALS = np.array([208,218,219,235,243,249,259,264,271,269,275,280,294,309,324,333,356,369,378,382,395,401,415,424,440], dtype=float)
DIST_CM  = np.array([100.4,95.2,91.5,80,75,71.5,67.7,65.3,62.3,59.1,56.6,53.5,50,47,43.5,40.5,37,34.2,30.6,27.8,24.5,21.2,18.5,16.8,15.2], dtype=float)
DIST_POLY = np.poly1d(np.polyfit(CY_VALS, DIST_CM, 5))

def cy_to_distance_cm(cy: float) -> float:
    import numpy as np
    return float(min(max(DIST_POLY(cy), 0.0), 100.0))

# Email (use env vars; don't hardcode secrets)
SMTP_USER = os.getenv("SMTP_USER", "your_email@example.com")
SMTP_PASS = os.getenv("SMTP_PASS", "app_password_here")
SMTP_RECIPIENTS = os.getenv("SMTP_RECIPIENTS", "you@example.com").split(",")
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

# Block order
BLOCK_ORDER = ["r", "g", "b"]
