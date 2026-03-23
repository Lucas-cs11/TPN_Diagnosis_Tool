# TPN Diagnosability Verification and Enhancement Tool - User Manual

**Version**: 1.0  
**Date**: 2026-03-23  
**Author**: Jie Lu

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Requirements](#2-system-requirements)
3. [Installation and First Run](#3-installation-and-first-run)
4. [Input Specification](#4-input-specification)
5. [Command-Line Interface](#5-command-line-interface)
6. [Outputs](#6-outputs)
7. [Algorithm Overview](#7-algorithm-overview)
8. [Worked Usage Patterns](#8-worked-usage-patterns)
9. [Interpreting the Results](#9-interpreting-the-results)
10. [Troubleshooting](#10-troubleshooting)
11. [Glossary](#11-glossary)

---

## 1. Introduction

### 1.1 Scope

This manual describes how to run and interpret the current repository implementation for diagnosability verification and diagnosability enhancement of Time Petri Nets (TPNs).

It documents the repository as it exists now:
- input format
- execution flow
- output files
- plotting
- known semantic boundaries

For short setup instructions, see [QUICKSTART.md](/Users/lucas/Desktop/TPN_Diagnosability_Tool/docs/guides/QUICKSTART.md). For a compact workflow summary, see [USER_GUIDE.md](/Users/lucas/Desktop/TPN_Diagnosability_Tool/docs/guides/USER_GUIDE.md).

### 1.2 Main Capabilities

The repository supports:
- TPN parsing from JSON
- observation synchronizer construction
- suspect prefix extraction
- P-ETERG construction
- detection of time-ambiguous normal/fault path pairs
- diagnosability enhancement through timing-constraint adjustment
- metrics export and visualization

### 1.3 Intended Use

Typical use cases include:
- reproducing and checking the repository’s example cases
- experimenting with custom TPN models
- comparing the relative cost of observation synchronizer and P-ETERG construction
- studying how timing-constraint adjustments affect diagnosability

## 2. System Requirements

### 2.1 Runtime Environment

- Python 3.10 or newer is recommended
- `pip` for dependency installation
- a writable directory for matplotlib cache if the default user cache is unavailable

### 2.2 Python Dependencies

The repository currently depends on:
- `matplotlib`
- `numpy`

Install them with:

```bash
pip install -r requirements.txt
```

### 2.3 Repository Layout Relevant to Users

- [main.py](/Users/lucas/Desktop/TPN_Diagnosability_Tool/main.py): command-line entry point
- [examples](/Users/lucas/Desktop/TPN_Diagnosability_Tool/examples): runnable TPN inputs
- [tests](/Users/lucas/Desktop/TPN_Diagnosability_Tool/tests): tests and regression cases
- [docs/notes/SEMANTICS_NOTES.md](/Users/lucas/Desktop/TPN_Diagnosability_Tool/docs/notes/SEMANTICS_NOTES.md): semantic alignment notes

## 3. Installation and First Run

### 3.1 Install Dependencies

```bash
cd /Users/lucas/Desktop/TPN_Diagnosability_Tool
pip install -r requirements.txt
```

### 3.2 Optional Matplotlib Cache Setting

If matplotlib reports that the default cache directory is not writable:

```bash
export MPLCONFIGDIR=/tmp/matplotlib
```

### 3.3 First Run

```bash
python main.py --input examples/example1.json --max-length 5
```

### 3.4 Test the Repository

```bash
python -m unittest tests.test_algorithms tests.test_tpn
```

## 4. Input Specification

### 4.1 Top-Level JSON Structure

A runnable input file contains:

```json
{
  "places": [...],
  "transitions": [...],
  "arcs": [...],
  "initial_marking": {...}
}
```

### 4.2 Places

`places` is a list of place names:

```json
"places": ["p1", "p2", "p3", "p4"]
```

Rules:
- each place name should be unique
- simple identifiers such as `p1`, `p2`, ... are recommended

### 4.3 Transitions

Each transition describes behavior, observability, and a timing constraint:

```json
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
```

Transition fields:

| Field | Type | Required | Meaning |
|------|------|------|------|
| `name` | string | yes | unique transition identifier |
| `type` | string | yes | `normal` or `fault` |
| `observable` | boolean | yes | whether the transition is observable |
| `label` | string | yes | observation label; use `epsilon` for unobservable transitions |
| `time_constraint` | object | yes | timing interval |

Timing-constraint fields:

| Field | Type | Required | Meaning |
|------|------|------|------|
| `type` | string | yes | `soft` or `hard` |
| `earliest` | number | yes | earliest firing time |
| `latest` | number | yes | latest firing time |

Interpretation:
- `soft` constraints may be adjusted during diagnosability enhancement
- `hard` constraints are fixed
- `label = "epsilon"` means that firing the transition produces no observable event

### 4.4 Arcs

Arcs connect places and transitions:

```json
"arcs": [
  {"from": "p1", "to": "t1"},
  {"from": "t1", "to": "p2"},
  {"from": "p2", "to": "t2", "weight": 2}
]
```

Arc fields:

| Field | Type | Required | Meaning |
|------|------|------|------|
| `from` | string | yes | source place or transition |
| `to` | string | yes | target place or transition |
| `weight` | number | no | arc weight, default `1` |

### 4.5 Initial Marking

The initial marking is a mapping from place names to token counts:

```json
"initial_marking": {
  "p1": 1,
  "p2": 0,
  "p3": 0
}
```

### 4.6 Minimal Complete Example

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
    },
    {
      "name": "t2",
      "type": "fault",
      "observable": false,
      "label": "epsilon",
      "time_constraint": {
        "type": "hard",
        "earliest": 0,
        "latest": 2
      }
    }
  ],
  "arcs": [
    {"from": "p1", "to": "t1"},
    {"from": "t1", "to": "p2"},
    {"from": "p2", "to": "t2"},
    {"from": "t2", "to": "p3"}
  ],
  "initial_marking": {
    "p1": 1,
    "p2": 0,
    "p3": 0
  }
}
```

## 5. Command-Line Interface

### 5.1 Single-File Analysis

```bash
python main.py --input examples/example1.json --max-length 5
```

### 5.2 Batch Analysis

```bash
python main.py --batch examples --max-length 5 --output results/batch
```

### 5.3 Common Arguments

| Argument | Meaning |
|------|------|
| `--input` | analyze a single TPN JSON file |
| `--batch` | analyze all runnable `.json` files in a directory |
| `--max-length` | maximum observation-prefix length |
| `--epsilon` | minimum increment used by diagnosability enhancement |
| `--output` | output directory |

### 5.4 Recommended Invocation

```bash
MPLCONFIGDIR=/tmp/matplotlib python main.py \
  --input examples/example2.json \
  --max-length 5 \
  --output results/example2
```

## 6. Outputs

### 6.1 Metrics JSON

Each run writes a `*_metrics.json` file. The current schema is defined in [metrics.py](/Users/lucas/Desktop/TPN_Diagnosability_Tool/src/analysis/metrics.py).

Main sections:
- `tpn_info`
- `observation_synchronizer`
- `peterg`
- `diagnosability`
- `overall`

### 6.2 Per-Network Figure

The detailed dashboard currently contains 6 panels:
- runtime profile
- state and edge footprint
- process snapshot
- per-prefix P-ETERG load
- ranked prefix hotspots
- enhancement outcome

### 6.3 Batch Figure

The batch dashboard currently contains 8 panels:
- state-space footprint
- runtime breakdown
- diagnosability outcomes
- prefix load and graph expansion
- adjustment efficiency
- exploration efficiency
- P-ETERG runtime share
- diagnosis process density

### 6.4 Console Output

The program also prints:
- the phase currently being executed
- counts of states, edges, prefixes, and ambiguous pairs
- final summary metrics

## 7. Algorithm Overview

### 7.1 Observation Synchronizer

Implementation: [observation_sync.py](/Users/lucas/Desktop/TPN_Diagnosability_Tool/src/algorithms/observation_sync.py)

The observation synchronizer is currently built on paired SCG states:
- the left side tracks normal behavior
- the right side tracks behavior with fault inclusion

A prefix becomes a suspect prefix when the paired successor states carry different labels.

### 7.2 P-ETERG

Implementation: [peterg.py](/Users/lucas/Desktop/TPN_Diagnosability_Tool/src/algorithms/peterg.py)

The repository constructs a P-ETERG for each suspect prefix and keeps path-level timing propagation in order to detect time-ambiguous pairs more precisely than a pure node-level merge would allow.

### 7.3 Diagnosability Enhancement

Implementation: [enhancement.py](/Users/lucas/Desktop/TPN_Diagnosability_Tool/src/algorithms/enhancement.py)

The current planner tries three candidate classes in order:
1. normal-path-exclusive transitions
2. fault-path-exclusive transitions
3. shared transitions

It then merges compatible adjustments into a single global plan whenever possible.

## 8. Worked Usage Patterns

### 8.1 Analyze a Paper Example

```bash
python main.py --input examples/example1.json --max-length 5 --output results/example1
```

### 8.2 Run the FMS-Style Example

```bash
python main.py --input examples/example2.json --max-length 5 --output results/example2
```

### 8.3 Run All Runnable Examples

```bash
python main.py --batch examples --max-length 5 --output results/batch
```

### 8.4 Use the Regression Cases

The additional examples cover different behaviors:
- `example3_time_separated.json`: suspect prefix without time ambiguity
- `example4_shared_adjustment.json`: only a shared transition can resolve ambiguity
- `example5_hard_unresolvable.json`: ambiguity remains unresolved because relevant constraints are hard
- `example6_global_shared_reuse.json`: multiple ambiguous pairs reuse the same adjustment

## 9. Interpreting the Results

### 9.1 Observation Synchronizer Statistics

Useful fields:
- `states`
- `edges`
- `suspect_prefixes`
- construction time

If `suspect_prefixes = 0`, no P-ETERG construction is required beyond the current analysis scope.

### 9.2 P-ETERG Statistics

Useful fields:
- number of P-ETERGs
- total node count
- total edge count
- per-prefix details

Large growth here usually indicates that suspect-prefix coverage dominates the run.

### 9.3 Diagnosability Statistics

Useful fields:
- `ambiguous_pairs`
- `resolved_pairs`
- `unresolved_pairs`
- `adjustments_made`

Typical interpretations:
- `ambiguous_pairs = 0`: the network is diagnosable under the current analysis scope
- `resolved_pairs > 0`: diagnosability enhancement found adjustable timing constraints
- `unresolved_pairs > 0`: the remaining ambiguity could not be removed by the current enhancement strategy

### 9.4 Formal-Semantics Notes

If your numeric results do not match a paper figure exactly, check [SEMANTICS_NOTES.md](/Users/lucas/Desktop/TPN_Diagnosability_Tool/docs/notes/SEMANTICS_NOTES.md) before assuming that the implementation is incorrect.

## 10. Troubleshooting

### 10.1 `ModuleNotFoundError`

Install dependencies:

```bash
pip install -r requirements.txt
```

### 10.2 Matplotlib Cache Warnings

Use:

```bash
export MPLCONFIGDIR=/tmp/matplotlib
```

### 10.3 JSON Parsing Errors

Check:
- missing commas
- invalid field names
- `latest < earliest`
- malformed arc endpoints

### 10.4 Batch Mode Fails on an Example File

`examples/` should only contain runnable inputs in the repository’s JSON format. Draft or reference-only files should be kept under `docs/notes/archive/examples/`.

## 11. Glossary

- **TPN**: Time Petri Net
- **Observation synchronizer**: structure used to compare normal behavior and fault-inclusive behavior under the same observation sequence
- **Suspect prefix**: observation prefix whose synchronized states indicate diagnostic uncertainty
- **P-ETERG**: Partial Extremum Timed Extended Reachability Graph
- **Time-ambiguous pair**: a normal/fault path pair with overlapping terminal timing intervals
- **Diagnosability enhancement**: the stage that adjusts timing constraints to separate ambiguous behavior
