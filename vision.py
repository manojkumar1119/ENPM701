import cv2
import numpy as np
from . import config

def get_color_mask(frame, c: str):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    ranges = config.HSV_RANGES.get(c, [])
    mask = None
    for r in ranges:
        lower = np.array(r[0], dtype=np.uint8)
        upper = np.array(r[1], dtype=np.uint8)
        part = cv2.inRange(hsv, lower, upper)
        mask = part if mask is None else (mask | part)
    return mask if mask is not None else np.zeros(frame.shape[:2], dtype=np.uint8)

def get_rect_center_offset(mask, frame):
    blurred = cv2.GaussianBlur(mask, (5, 5), 0)
    _, mask_clean = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None, (None, None), None, None
    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)
    cx, cy = x + w // 2, y + h // 2
    img_center_x = (frame.shape[1] // 2)
    angle_px = cx - img_center_x
    return angle_px, (cx, cy), h, w

def pixels_to_degrees(angle_px: float, focal_px: float = None) -> float:
    if focal_px is None:
        focal_px = config.FOCAL_LENGTH_PX
    return float(np.degrees(np.arctan2(angle_px, focal_px)))

def distance_from_cy(cy: float) -> float:
    return config.cy_to_distance_cm(cy)
