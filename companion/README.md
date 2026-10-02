# companion (Jetson Orin Nano)

Non-safety-critical (Baseline §4.2). Sends bounded parameter sets to the Teensy; receives summary metrics. Link definition: `exo-interfaces/I-03_jetson-teensy-link.md`.

| Path | Contents | Work package |
| --- | --- | --- |
| `processing/` | Data processing and feature extraction | |
| `optimizer/` | Offline CMA-ES pipeline: parameter vector, bounds, fitness function | CTRL-004 |

Optimizer data sources are restricted to published datasets until gate S2 closes.
