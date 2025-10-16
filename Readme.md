# Autonomous Mobile Robot – Grand Challenge

> **Course:** ENPM701 — Autonomous Robotics  
> **Team:** Autonomous Robotics (University Project)  
> **Demo Video:** [Watch here](#)  
> **Environment:** 10×10 ft arena; construction zone (2×2 ft, bottom-right), drop zone (4×4 ft, bottom-left)

The goal is to design and program an autonomous ground robot to explore a Martian-style arena, detect color-coded blocks in a required order (**red → green → blue** × 3), pick them with a gripper, and deliver them to the drop zone—fully autonomously.

---

## Table of Contents
- [Hardware Architecture](#hardware-architecture)
- [Software Architecture](#software-architecture)
- [Vision Modules](#vision-modules)
  - [Stop Sign Detection](#stop-sign-detection)
  - [Arrow Detection](#arrow-detection)
  - [Block Detection & Masking](#block-detection--masking)
- [Control & Navigation](#control--navigation)
  - [Motion Control](#motion-control)
  - [Localization](#localization)
  - [Distance Estimation](#distance-estimation)
- [Calibration](#calibration)
- [Grand Challenge Performance](#grand-challenge-performance)
- [Key Takeaways](#key-takeaways)
- [Quick Start](#quick-start)
- [Repository Structure](#repository-structure)
- [Tuning Parameters](#tuning-parameters)
- [Known Issues & Future Work](#known-issues--future-work)
- [Acknowledgments](#acknowledgments)
- [License](#license)

---

## Hardware Architecture

**Platform**
- **Chassis:** 4-wheel base with DC motors  
- **Encoders:** Optical/magnetic wheel encoders (speed + direction)  
- **Motor Driver:** Dual H-Bridge for bidirectional control  
- **Gripper:** Servo-actuated claw for pickup/placement

**Compute & Sensors**
- **Processor:** Raspberry Pi 3B+ (video processing, autonomy) *(video mentions Pi 4; project uses 3B+ in final build—either is compatible)*  
- **Camera:** Raspberry Pi camera (primary perception)  
- **Ultrasonic Sensor:** Proximity sensing & wall avoidance; used for mid-run re-localization  
- **IMU:** Orientation (roll/pitch/yaw) for heading correction & dead-reckoning

> Optional mechanical hack: a **thin cardboard lip** on the gripper improved capture reliability when grasp alignment was slightly off.

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

### Stop Sign Detection
- HSV segmentation tuned to robustly isolate the sign color range across lighting changes.
- Binary masks → contour filtering → presence/stop decision.

### Arrow Detection
- Contour extraction + polygon approximation to classify arrow shapes.
- Direction inference (left/right) feeds the path planner for turning.

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
- Issues encountered:
  - Occasional **false positive** on second red block under changing light.
  - **Premature stop** triggered before reaching the goal zone (extra condition needed).
  - **Missing error handler** for ultrasonic read failures (rare but impactful).

**Post-mortem**
- A small software guard (debounce + state check around the stop condition) would have enabled a clean, full-score run.

---

## Key Takeaways

- **Perception:** Real-time color segmentation + shape cues are viable on Pi-class hardware with careful thresholding.  
- **Localization:** Lightweight fusion (encoders+IMU+ultrasonic) is enough for small arenas when drift is periodically capped.  
- **Control:** Simple P/PID can produce smooth, accurate motion if sensors are calibrated and noise-bounded.  
- **Integration:** Most failures were **edge-case handling** (sensor glitches, early stop)—robust guards matter as much as core algorithms.

---

## Quick Start

> **Prereqs:** Raspberry Pi OS, Python 3.9+, OpenCV, NumPy, IMU & ultrasonic libs, GPIO access.

```bash
# 1) Install deps (example)
sudo apt-get update
sudo apt-get install -y python3-opencv python3-numpy python3-smbus i2c-tools
pip3 install RPi.GPIO

# 2) Enable camera, I2C, and serial as needed
sudo raspi-config   # Interfaces → enable Camera / I2C / Serial

# 3) Clone repo
git clone <your-repo-url>.git
cd <your-repo>

# 4) Run vision debug (shows masks & centroids)
python3 tools/vision_debug.py --camera 0

# 5) Run full autonomy
python3 run_autonomy.py --order R,G,B --trials 3
