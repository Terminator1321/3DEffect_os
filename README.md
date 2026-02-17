---

# 3DEffect_os

Real-time head-tracked 3D display that creates a depth illusion on a flat monitor using webcam tracking and dynamic OpenGL perspective rendering.

---

## Real-Time Head-Tracked 3D Display

An experimental computer vision project that creates the illusion of depth on a normal flat monitor using real-time head tracking and perspective-correct OpenGL rendering.

This system tracks the user’s head position with a webcam and dynamically adjusts the camera perspective, producing a pseudo-3D parallax effect without special hardware.

---

## Important Requirement

⚠️ **This project requires a second monitor.**
The main screen is captured and rendered inside the virtual 3D environment, while the second monitor is used to display the head-tracked 3D output.

If you do not have a physical second monitor, you can use a virtual display solution such as **GlideX**.

---

## How It Works

1. A webcam captures the user’s face in real time.
2. **MediaPipe** detects facial landmarks and extracts the nose position.
3. The nose coordinates are converted into **x, y, z head movement values**.
4. These values control a **virtual OpenGL camera**.
5. The camera updates perspective dynamically, creating a depth illusion.

---

## Rendering Pipeline

* Screen content is captured using **MSS**.
* The captured frame is mapped as a **texture on a front plane**.
* A virtual 3D room is rendered around the plane.
* Side walls use reflections to enhance the depth effect.

---

## Tech Stack

* **Python 3.10.11 (recommended)**
* **OpenGL (PyOpenGL)**
* **OpenCV**
* **MediaPipe**
* **MSS (screen capture)**

---

## Features

* Real-time head tracking
* Perspective-correct parallax rendering
* Pseudo-3D effect on standard monitors
* No special display hardware required

---

## Requirements

* **Python 3.10.11**
* Webcam
* OpenGL-compatible GPU
* **Second monitor** (physical or virtual via GlideX)

---

## Installation

```bash
git clone https://github.com/yourusername/3DEffect_os.git
cd 3DEffect_os
pip install -r requirements.txt
```

---

## Run the Project

```bash
python main.py
```

Make sure:

* Your webcam is connected
* OpenGL drivers are installed
* The second monitor is configured and active

---

## Possible Applications

* AR/VR experiments
* Simulation displays
* Interactive installations
* Research in perspective-based rendering

---

## Status

This is an experimental prototype and may require manual configuration depending on hardware and monitor setup.

---
