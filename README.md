# TPN Diagnosability Verification and Enhancement Tool

This repository implements an executable workflow for diagnosability analysis of Time Petri Nets (TPNs), following the paper *Observation-Driven Diagnosability Verification and Enhancement for Time Petri Nets via Partial Extremum Timed Extended Reachability Graphs*.

The current codebase provides:
- TPN modeling and JSON parsing
- Observation synchronizer construction and suspect prefix extraction
- P-ETERG construction and time-ambiguity detection
- Diagnosability enhancement through timing-constraint adjustment
- Metrics export, batch analysis, and visualization

## Repository Layout

```text
TPN_Diagnosability_Tool/
├── README.md
├── main.py
├── requirements.txt
├── test.sh
├── src/
│   ├── algorithms/
│   │   ├── enhancement.py
│   │   ├── observation_sync.py
│   │   ├── peterg.py
│   │   └── archive/
│   ├── analysis/
│   └── tpn/
├── examples/
│   ├── example1.json
│   ├── example2.json
│   └── example*.json
├── tests/
│   ├── test_algorithms.py
│   └── test_tpn.py
├── docs/
│   ├── guides/
│   ├── notes/
│   └── paper/
└── scripts/
```

Directory conventions:
- `src/`: implementation
- `examples/`: runnable TPN inputs for `main.py`
- `tests/`: unit and regression tests
- `docs/guides/`: user-facing documentation
- `docs/notes/`: semantics notes, debugging records, and historical material
- `docs/paper/`: paper copy used for reference
- `scripts/`: debugging and research helpers
- `results/`: generated output directory, intentionally excluded from source structure

## Quick Start

```bash
pip install -r requirements.txt
python main.py --input examples/example1.json --max-length 5
python -m unittest tests.test_algorithms tests.test_tpn
```

If the default matplotlib cache directory is not writable on your machine, run:

```bash
MPLCONFIGDIR=/tmp/matplotlib python main.py --input examples/example2.json --max-length 5
```

## Input Format

```json
{
  "places": ["p1", "p2", "p3"],
  "transitions": [
    {
      "name": "t1",
      "type": "normal",
      "observable": true,
      "label": "a",
      "time_constraint": {
        "type": "soft",
        "earliest": 1,
        "latest": 3
      }
    }
  ],
  "arcs": [
    {"from": "p1", "to": "t1"},
    {"from": "t1", "to": "p2"}
  ],
  "initial_marking": {"p1": 1, "p2": 0, "p3": 0}
}
```

Conventions:
- `label = "epsilon"` denotes an unobservable transition
- `type = "fault"` denotes a fault transition
- `time_constraint.type` is either `soft` or `hard`

## Documentation

- Quick start: [docs/guides/QUICKSTART.md](/Users/lucas/Desktop/TPN_Diagnosability_Tool/docs/guides/QUICKSTART.md)
- User guide: [docs/guides/USER_GUIDE.md](/Users/lucas/Desktop/TPN_Diagnosability_Tool/docs/guides/USER_GUIDE.md)
- User manual: [docs/guides/USER_MANUAL.md](/Users/lucas/Desktop/TPN_Diagnosability_Tool/docs/guides/USER_MANUAL.md)
- Semantics notes: [docs/notes/SEMANTICS_NOTES.md](/Users/lucas/Desktop/TPN_Diagnosability_Tool/docs/notes/SEMANTICS_NOTES.md)
- Paper: [docs/paper/Observation-Driven Diagnosability Verification and Enhancement for Time Petri Nets via Partial Extremum Timed Extended Reachability Graphs.pdf](/Users/lucas/Desktop/TPN_Diagnosability_Tool/docs/paper/Observation-Driven%20Diagnosability%20Verification%20and%20Enhancement%20for%20Time%20Petri%20Nets%20via%20Partial%20Extremum%20Timed%20Extended%20Reachability%20Graphs.pdf)

## Current Status

`example1` and `example2/FMS` are the main regression baselines for the current implementation. Additional examples cover:
- suspect prefixes that are already time-separated
- cases that can only be resolved through a shared transition
- cases that remain unresolved because all relevant constraints are hard
- multiple ambiguous pairs that reuse the same timing adjustment

Historical draft inputs and non-runnable reference material have been moved to `docs/notes/archive/examples/` so that `--batch examples` only scans runnable inputs.
