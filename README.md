# exo-controls

Control software for the EXO Phase 1 leg: Teensy 4.1 real-time firmware and Jetson Orin Nano companion software (Technical Baseline §4).

| Field | Value |
| --- | --- |
| Owner | Controls team lead (Oscar: hardware and firmware; Tom: control law) |
| Program | IEEE EXO, Phase 1 (unilateral prototype) |
| Current version | v0.1 (scaffold) |

## Layout

```
firmware/      Teensy 4.1 real-time loop: CAN to AK80-9, sensors, state machine, limits, watchdog
companion/     Jetson Orin Nano: data processing, feature extraction, CMA-ES optimizer
tools/         Bench scripts, log parsers, AK80-9 setup notes
data/          Pointer to bench logs (raw logs are not committed)
docs/          State machine, control law, test reports
```

Safety boundary: the Teensy holds final authority over commanded torque. Companion code sends bounded parameter sets only (Baseline §4.2).

## How changes are made

Branch from `main`, open a pull request, get one approval from the code owner, merge. See `CONTRIBUTING.md`.

## Drive folder

Drive folder (Controls): https://drive.google.com/drive/folders/1Pdx0N6EHctdZKqb7P29tVHuNVr8v8yrN
Bench Logs: https://drive.google.com/drive/folders/1_RSpCkNbs0HOr5qNI4XDlgEHmhbr6T7v
