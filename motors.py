import time
import RPi.GPIO as GPIO
from . import config
from .utils import clamp

class MotorController:
    def __init__(self, pins=None):
        self.pins = pins or config.MOTOR_PINS
        self._pwm_lf = self._pwm_lb = self._pwm_rf = self._pwm_rb = None
        self._setup()

    def _setup(self):
        GPIO.setmode(GPIO.BOARD)
        for p in [self.pins.LEFT_FORWARD, self.pins.LEFT_BACKWARD, self.pins.RIGHT_FORWARD, self.pins.RIGHT_BACKWARD]:
            GPIO.setup(p, GPIO.OUT)
        self._pwm_lf = GPIO.PWM(self.pins.LEFT_FORWARD, 50)
        self._pwm_lb = GPIO.PWM(self.pins.LEFT_BACKWARD, 50)
        self._pwm_rf = GPIO.PWM(self.pins.RIGHT_FORWARD, 50)
        self._pwm_rb = GPIO.PWM(self.pins.RIGHT_BACKWARD, 50)
        for p in [self._pwm_lf, self._pwm_lb, self._pwm_rf, self._pwm_rb]:
            p.start(0)

    def _stop_all(self):
        for p in [self._pwm_lf, self._pwm_lb, self._pwm_rf, self._pwm_rb]:
            p.ChangeDutyCycle(0)

    def cleanup(self):
        try:
            self._stop_all()
            self._pwm_lf.stop(); self._pwm_lb.stop(); self._pwm_rf.stop(); self._pwm_rb.stop()
        finally:
            GPIO.cleanup()

    @staticmethod
    def angular_error(current, target):
        error = (target - current + 360.0) % 360.0
        if error > 180.0:
            return 360.0 - error, "L"
        else:
            return error, "R"

    def rotate(self, angle_deg, direction, threshold_deg, imu_reader):
        steps = 0
        current = imu_reader.get_angle()
        target = (current + angle_deg) % 360.0 if direction == "R" else (current - angle_deg + 360.0) % 360.0
        Kp = config.ROTATE_KP
        Kd = config.ROTATE_KD
        prev_error = 0.0
        pwm_val = 0.0
        max_pwm = config.ROTATE_MAX_PWM
        min_pwm = config.ROTATE_MIN_PWM

        while True:
            current = imu_reader.get_angle()
            error, dir_needed = MotorController.angular_error(current, target)
            if error < threshold_deg:
                self._stop_all()
                break
            if error < 10.0:
                max_pwm = config.ROTATE_LOW_ERROR_MAX_PWM
                min_pwm = config.ROTATE_LOW_ERROR_MIN_PWM
            derivative = error - prev_error
            derivative = clamp(derivative, -15.0, 15.0)
            pwm_val = Kp * error + Kd * derivative
            pwm_val = clamp(pwm_val, min_pwm, max_pwm)
            prev_error = error
            steps += 1

            if dir_needed == "L":
                self._pwm_lf.ChangeDutyCycle(pwm_val)
                self._pwm_lb.ChangeDutyCycle(pwm_val)
                self._pwm_rf.ChangeDutyCycle(0)
                self._pwm_rb.ChangeDutyCycle(0)
            else:
                self._pwm_lf.ChangeDutyCycle(0)
                self._pwm_lb.ChangeDutyCycle(0)
                self._pwm_rf.ChangeDutyCycle(pwm_val)
                self._pwm_rb.ChangeDutyCycle(pwm_val)
        return current, steps

    def move_straight(self, dist_cm, direction, imu_reader, base_dc=60):
        GPIO.setmode(GPIO.BOARD)
        lf, lb, rf, rb = self.pins.LEFT_FORWARD, self.pins.LEFT_BACKWARD, self.pins.RIGHT_FORWARD, self.pins.RIGHT_BACKWARD
        pwm_l = GPIO.PWM(lf if direction=="forward" else lb, 50)
        pwm_r = GPIO.PWM(rf if direction=="forward" else rb, 50)
        pwm_l.start(0); pwm_r.start(0)

        GPIO.setup(config.ENCODER_LEFT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(config.ENCODER_RIGHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        left_prev = int(GPIO.input(config.ENCODER_LEFT_PIN))
        right_prev = int(GPIO.input(config.ENCODER_RIGHT_PIN))
        left_ticks = 0
        right_ticks = 0

        def ticks_target(d):
            return int(0.98 * d)  # scale from original
        goal_ticks = ticks_target(dist_cm)

        imu_reader.flush_garbage(5)
        goal_heading = imu_reader.get_angle()

        try:
            while True:
                curr_heading = imu_reader.get_angle()
                raw_diff = (goal_heading - curr_heading) % 360.0
                error = (raw_diff + 180.0) % 360.0 - 180.0
                pid = error * 5.0

                duty_l = clamp(base_dc + pid, 0, 90)
                duty_r = clamp(base_dc - pid, 0, 90)
                pwm_l.ChangeDutyCycle(duty_l)
                pwm_r.ChangeDutyCycle(duty_r)

                l_now = int(GPIO.input(config.ENCODER_LEFT_PIN))
                r_now = int(GPIO.input(config.ENCODER_RIGHT_PIN))
                if l_now != left_prev:
                    left_prev = l_now
                    left_ticks += 1
                if r_now != right_prev:
                    right_prev = r_now
                    right_ticks += 1

                if left_ticks >= goal_ticks and right_ticks >= goal_ticks:
                    break
                time.sleep(0.002)
        finally:
            pwm_l.stop(); pwm_r.stop(); GPIO.cleanup()
        return left_ticks, right_ticks
