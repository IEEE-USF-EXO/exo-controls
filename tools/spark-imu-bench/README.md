# Spark IMU bench code

Bench code from the Spark team (formerly Marco's Disciples) for the MPU6500
IMU on a Teensy 4.1. Files are committed as they are in the team's Drive
folder, unmodified. Descriptions below are from the team's "Teensy files
context" note.

| File | Purpose | Status per the team |
| --- | --- | --- |
| `Teensy_IMU_main ver 2 (1).cpp` | Teensy firmware. Reads the MPU6500 over SPI1 (MPU6500_WE library) and streams `ax,ay,az,gx,gy,gz` as CSV at 115200 baud, about 50 Hz. Accel in g, gyro in deg/s, gyro range ±250 deg/s. | Working |
| `Teensy_IMU_gui_v2.py` | Live dashboard (customtkinter, pyserial, matplotlib). Selects the serial port, connects, pauses, and toggles each channel. Optional `ieee_logo.png` in the same folder. | Working |
| `IMU_3D.m` | MATLAB 3D orientation view. Fuses accel and gyro with `imufilter` and rotates a cuboid. Needs the Navigation Toolbox and the Sensor Fusion and Tracking Toolbox. Port is hard-coded to `COM7`. | Working; slow constant rotation when stationary |
| `Teensy_Servo_main.cpp` | Sweeps 8 servos 0 to 180 deg through a PCA9685 (Adafruit_PWMServoDriver). | Not working |

Notes for reviewers, not changes to the code:

- `IMU_3D.m` sets `imufilter` to 100 Hz, but the firmware sends at about
  50 Hz. That mismatch may account for the drift the team reports.
- The firmware hard-codes gyro offsets `(30, -121, -111)`, which apply to
  one specific board.

Source: Drive, Spark (Formerly known as Marco's Disciples).
