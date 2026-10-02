# firmware (Teensy 4.1)

Real-time loop, 500 to 1000 Hz class (Baseline §4.2): sensor reads, gait state, torque and position commands to the AK80-9 over CAN, software limits, watchdog, logging.

| Path | Contents | Work package |
| --- | --- | --- |
| `src/can/` | AK80-9 command and readout | CTRL-001 |
| `src/safety/` | Software stop, watchdog timeout to zero torque | CTRL-005 |
| `src/control/` | State machine and per-phase torque law | CTRL-003 |
| `src/sensors/` | Encoders, IMUs, FSRs, load cell readout | (B2/B3 hardware) |
| `include/limits.h` | Torque, ROM, current, and temperature limits | Values from I-07 |
| `test/` | Bench test sketches | |

CAN message definitions live in `exo-interfaces/can/` (I-02, I-03). Do not redefine them here.
