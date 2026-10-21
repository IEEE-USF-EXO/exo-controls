# exo-controls

Control software for the EXO Phase 1 leg: Teensy 4.1 real-time firmware and Jetson Orin Nano companion software (Technical Baseline §4).

| Field | Value |
| --- | --- |
| Owner | Controls team lead (Oscar: hardware and firmware; Tom: control law) |
| Program | IEEE EXO, Phase 1 (unilateral prototype) |
| Current version | v0.1 (scaffold) |

## Current work

Controls has no sub-teams. Each package lists its deliverable, what shows the work is done, and its owner. Drive folder: [Controls](https://drive.google.com/drive/folders/1Pdx0N6EHctdZKqb7P29tVHuNVr8v8yrN)

**CTRL-001 Single actuator CAN command and readout on the bench**
- Deliverable: Teensy 4.1 toolchain plus a single AK80-9 CAN command and readout on the bench. Needs the bench stop path first (see Safety).
- Shows it is done: bench video plus a log of position, velocity, and current.
- Owner: Oscar (hardware).

**CTRL-002 Jetson to Teensy link definition**
- Deliverable: Jetson Orin Nano to Teensy link definition: message set, rates, and when parameter updates are allowed (I-03).
- Shows it is done: an interface draft.
- Owner: Oscar (hardware).

**CTRL-003 State machine v0.1**
- Deliverable: states, transitions, gait-phase detection from FSR, IMU, and encoder inputs, and the per-phase torque law structure for hip and knee.
- Shows it is done: a diagram plus written transition rules.
- Owner: Tom (control law).

**CTRL-004 Offline optimization plan**
- Deliverable: CMA-ES offline pipeline plan: parameter vector, bounds, fitness function, and biomechanical targets. The data source is published datasets only.
- Shows it is done: a plan document.
- Owner: Tom (control law).

**CTRL-005 Software stop**
- Deliverable: a kill command and a watchdog timeout that command zero torque.
- Shows it is done: a bench demonstration on the first powered test.
- Owner: Oscar (hardware).

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

## Where files live

Native design files, bench logs, test data, photos, and vendor PDFs live in Drive. This repo holds exports, drawings, the BOM, code, and short summaries. Raw bench logs are not committed.

Controls: https://drive.google.com/drive/folders/1Pdx0N6EHctdZKqb7P29tVHuNVr8v8yrN
Bench Logs: https://drive.google.com/drive/folders/1_RSpCkNbs0HOr5qNI4XDlgEHmhbr6T7v

## Safety

1. No powered actuator moves until the bench stop path has been demonstrated and the Project Leads have confirmed it.
2. Nobody wears any part of the device, including the battery belt, until the Project Leads confirm written approval.
3. No on-body sensor data, and no data from anyone wearing part of the device, goes into Drive or GitHub.
4. No lithium-ion pack assembly until a reviewed build procedure exists.
5. Lab work in ENG 208 requires the lab safety courses to be complete.
6. Never commit passwords, tokens, keys, or Wi-Fi credentials. Use an ignored file and a committed example file.
