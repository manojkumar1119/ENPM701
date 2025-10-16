# Autonomous Mobile Robot – Grand Challenge

> **Course:** ENPM701 — Autonomous Robotics  
> **Environment:** 10×10 ft arena; construction zone (2×2 ft, bottom-right), drop zone (4×4 ft, bottom-left)

The goal is to design and program an autonomous ground robot to explore a Martian-style arena, detect color-coded blocks in a required order (**red → green → blue** × 3), pick them with a gripper, and deliver them to the drop zone—fully autonomously.

---

## Table of Contents
- [Hardware Architecture](#hardware-architecture)
- [Software Architecture](#software-architecture)
- [Vision Modules](#vision-modules)
  - [Block Detection & Masking](#block-detection--masking)
- [Control & Navigation](#control--navigation)
  - [Motion Control](#motion-control)
  - [Localization](#localization)
  - [Distance Estimation](#distance-estimation)
- [Calibration](#calibration)
- [Grand Challenge Performance](#grand-challenge-performance)
- [Key Takeaways](#key-takeaways)
---

## Hardware Architecture

**Platform**
- **Chassis:** 4-wheel base with DC motors  
- **Encoders:** Optical/magnetic wheel encoders (speed + direction)  
- **Motor Driver:** Dual H-Bridge for bidirectional control  
- **Gripper:** Servo-actuated claw for pickup/placement

**Compute & Sensors**
- **Processor:** Raspberry Pi 3B+ (video processing, autonomy)   
- **Camera:** Raspberry Pi camera (primary perception)  
- **Ultrasonic Sensor:** Proximity sensing & wall avoidance; used for mid-run re-localization  
- **IMU:** Orientation (roll/pitch/yaw) for heading correction & dead-reckoning

> Mechanical hack: a **thin cardboard lip** on the gripper improved capture reliability when grasp alignment was slightly off.

---

## Software Architecture

Development followed an incremental, test-driven approach. Each week focused on one subsystem (vision → control → localization → integration). Major modules:

- **Perception:** HSV segmentation → contour analysis → class/pose cues  
- **Control:** P/PID-style speed alignment + heading correction; waypoint routines  
- **Localization:** Encoder odometry + IMU fusion; periodic ultrasonic re-alignment  
- **Task Logic:** Block ordering policy (R→G→B), pickup → transport → dropoff sequencing

> The system favors **deterministic behavior** over raw speed. IMU-based reorientation occurs approximately every 20 cm to limit drift before grasping.

---

## Vision Modules
### Block Detection & Masking
- Color-specific HSV masks for **red, green, blue**.
- Largest valid contour → bounding shape (min-enclosing circle or bounding box).
- Centroid and area heuristics reject false positives (e.g., specular highlights).

---

## Control & Navigation

### Motion Control
- Compared **encoder-only** vs **encoder+IMU** fused control.
- Fused approach yielded **straighter lines and smoother turns**, especially during long traversals.
- Simple P-controller maintains straight-line motion by balancing wheel speeds.

### Localization
- **Dead-reckoning:** Incremental pose updates from encoders + IMU heading.
- **Drift mitigation:** Periodic ultrasonic checks near walls & beacons to cap error growth.

### Distance Estimation
- Empirical mapping from **image features → metric distance**:
  - Collect (centroid/size) vs known distances.
  - Fit a curve (interpolation or poly fit).
  - At runtime, convert observed pixel metrics → approach distance for grasping.

---

## Calibration

1. **HSV Tuning:**  
   Place colored blocks under expected lighting; sweep H/S/V ranges until masks are clean and stable. Save final bounds per color.

2. **Camera–Distance Curve:**  
   Place a block at multiple known distances (e.g., 15–100 cm). Record pixel centroid/size; fit a curve to predict distance in operation.

3. **IMU Alignment:**  
   With robot stationary, record yaw bias and compensate in software. Verify repeated 90° and 180° turns within tolerance.

4. **Encoder Scale:**  
   Command fixed wheel rotations or distances; adjust counts-to-meters constant until measured error < target (e.g., <2% over 2 m).

---

## Grand Challenge Performance

**Scoring Rules**
- ✅ Correct placement: **+1**
- ❌ Incorrect placement: **−1**

**Final Trial Highlights**
- Planned trajectory executed reliably with fused control.  
---

## Key Takeaways

- **Perception:** Real-time color segmentation + shape cues are viable on Pi-class hardware with careful thresholding.  
- **Localization:** Lightweight fusion (encoders+IMU+ultrasonic) is enough for small arenas when drift is periodically capped.  
- **Control:** Simple P/PID can produce smooth, accurate motion if sensors are calibrated and noise-bounded.  

---
