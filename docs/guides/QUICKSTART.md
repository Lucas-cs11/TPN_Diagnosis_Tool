# Quick Start

This document only keeps the minimum information required to run the repository. For repository structure, see [README.md](/Users/lucas/Desktop/TPN_Diagnosability_Tool/README.md). For semantics decisions, see [SEMANTICS_NOTES.md](/Users/lucas/Desktop/TPN_Diagnosability_Tool/docs/notes/SEMANTICS_NOTES.md).

## Environment Setup

```bash
cd /Users/lucas/Desktop/TPN_Diagnosability_Tool
pip install -r requirements.txt
```

If the default matplotlib cache directory is not writable:

```bash
export MPLCONFIGDIR=/tmp/matplotlib
```

## Analyze a Single Case

```bash
python main.py \
  --input examples/example1.json \
  --max-length 5 \
  --output results/example1
```

Common arguments:
- `--input`: single TPN JSON file
- `--batch`: directory for batch analysis
- `--max-length`: maximum observation-prefix length
- `--epsilon`: minimum increment used in diagnosability enhancement, default `0.1`
- `--output`: output directory

## Batch Analysis

```bash
python main.py \
  --batch examples \
  --max-length 5 \
  --output results/batch
```

Only runnable TPN inputs should stay under `examples/`. Historical drafts are stored under `docs/notes/archive/examples/`.

## Run Tests

```bash
python -m unittest tests.test_algorithms tests.test_tpn
```

You can also use the repository script:

```bash
./test.sh
```

## Minimal Input Format

```json
{
  "places": ["p1", "p2"],
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
  "initial_marking": {
    "p1": 1,
    "p2": 0
  }
}
```

Conventions:
- `label = "epsilon"` denotes an unobservable transition
- `type = "fault"` denotes a fault transition
- `time_constraint.type` is either `soft` or `hard`

## Outputs

Each run produces:
- `*_metrics.json`: structure, runtime, ambiguous-pair, and enhancement statistics
- `plots/*_detailed.png`: per-network dashboard
- `plots/TPN_Batch_Analysis_Comparison.png`: batch dashboard, only for batch mode

## Suggested Reading Order

1. Read [README.md](/Users/lucas/Desktop/TPN_Diagnosability_Tool/README.md) for repository structure.
2. Read [USER_GUIDE.md](/Users/lucas/Desktop/TPN_Diagnosability_Tool/docs/guides/USER_GUIDE.md) for workflow and outputs.
3. Read [SEMANTICS_NOTES.md](/Users/lucas/Desktop/TPN_Diagnosability_Tool/docs/notes/SEMANTICS_NOTES.md) for paper-alignment notes.
