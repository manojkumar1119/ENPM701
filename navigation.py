import numpy as np
from . import config

def ticks_to_distance(ticks: int) -> float:
    return ticks / 0.98

def localize(append_ticks, heading_deg, traj):
    if heading_deg < 0:
        heading_deg += 360.0
    d = ticks_to_distance(append_ticks)
    adjusted = (90.0 - heading_deg) % 360.0
    rad = np.deg2rad(adjusted)
    dx = -d * np.cos(rad)
    dy = d * np.sin(rad)
    traj.append(dx, dy)
    return traj.x[-1], traj.y[-1]

def reorient_to_axes(current_heading, motor, imu, ultrasonic, traj):
    desired_heading_y = 0.0
    rotate_angle = (current_heading - desired_heading_y + 360.0) % 360.0
    motor.rotate(rotate_angle, "L", 2, imu)
    dist_x = ultrasonic.measure()
    motor.rotate(90.0, "R", 2, imu)
    dist_y = ultrasonic.measure()
    traj.append_abs(config.FIELD_X_CM - dist_y - 7.15, dist_x - 7.15)
    return imu.get_angle()

def move_to_goal(goal_x, goal_y, motor, imu, traj):
    cur_x, cur_y = traj.x[-1], traj.y[-1]
    dx, dy = goal_x - cur_x, goal_y - cur_y
    target_heading = (np.degrees(np.arctan2(-dx, dy)) + 360.0) % 360.0
    current_heading = imu.get_angle()
    diff = (target_heading - current_heading + 180.0) % 360.0 - 180.0
    direction = "R" if diff >= 0 else "L"
    new_heading, _ = motor.rotate(abs(diff), direction, 2, imu)
    distance_cm = float(np.hypot(dx, dy))
    lt, rt = motor.move_straight(distance_cm - 7.0, "forward", imu, base_dc=60)
    avg_ticks = (lt + rt) / 2.0
    x, y = localize(avg_ticks, new_heading, traj)
    return new_heading, (x, y)
