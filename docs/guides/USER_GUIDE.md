# User Guide

This guide describes the repository as it is currently implemented. It is not a restatement of the idealized workflow in the paper. File paths, input format, and outputs below reflect the current codebase.

## 1. What the Project Does

The repository implements an executable diagnosability-analysis workflow for Time Petri Nets:

1. Read a TPN from JSON.
2. Build the observation synchronizer and extract suspect prefixes.
3. Build a P-ETERG for each suspect prefix.
4. Detect time-ambiguous normal/fault path pairs.
5. Apply the current diagnosability-enhancement strategy to adjustable timing constraints.
6. Export metrics and figures.

The main entry point is [main.py](/Users/lucas/Desktop/TPN_Diagnosability_Tool/main.py).

## 2. Directory Overview

- [src/tpn](/Users/lucas/Desktop/TPN_Diagnosability_Tool/src/tpn): TPN model, parser, and SCG approximation
- [src/algorithms](/Users/lucas/Desktop/TPN_Diagnosability_Tool/src/algorithms): observation synchronizer, P-ETERG, and diagnosability enhancement
- [src/analysis](/Users/lucas/Desktop/TPN_Diagnosability_Tool/src/analysis): metrics and plotting
- [examples](/Users/lucas/Desktop/TPN_Diagnosability_Tool/examples): runnable example networks
- [tests](/Users/lucas/Desktop/TPN_Diagnosability_Tool/tests): unit and regression tests
- [docs/notes](/Users/lucas/Desktop/TPN_Diagnosability_Tool/docs/notes): semantics notes and debugging records
- [scripts/debug](/Users/lucas/Desktop/TPN_Diagnosability_Tool/scripts/debug): debugging helpers
- [scripts/research](/Users/lucas/Desktop/TPN_Diagnosability_Tool/scripts/research): experimental scripts

## 3. Input Requirements

Inputs use the repository-specific TPN JSON format implemented in [parser.py](/Users/lucas/Desktop/TPN_Diagnosability_Tool/src/tpn/parser.py).

Top-level fields:
- `places`: list of place names
- `transitions`: list of transitions
- `arcs`: list of arcs
- `initial_marking`: initial marking

Transition fields:
- `name`: unique identifier
- `type`: `normal` or `fault`
- `observable`: whether the transition is observable
- `label`: observation label; use `epsilon` for unobservable transitions
- `time_constraint`:
  - `type`: `soft` or `hard`
  - `earliest`
  - `latest`

Notes:
- `label = "epsilon"` does not append an event to the observation sequence.
- `soft` constraints may be adjusted by diagnosability enhancement.
- `hard` constraints are not changed by the enhancement phase.

## 4. Workflow

### 4.1 Observation Synchronizer

Implementation: [observation_sync.py](/Users/lucas/Desktop/TPN_Diagnosability_Tool/src/algorithms/observation_sync.py)

The current synchronizer is built over paired SCG states:
- the left side only tracks normal behavior
- the right side allows fault-inclusive behavior

An observable event is added only when both sides can realize that event. If the labels of the successor pair differ, the corresponding observation prefix is recorded as a suspect prefix.

### 4.2 P-ETERG

Implementation: [peterg.py](/Users/lucas/Desktop/TPN_Diagnosability_Tool/src/algorithms/peterg.py)

The current implementation propagates timing information at the path-state level instead of only maintaining coarse timing ranges on merged nodes. The result exposes:
- merged P-ETERG nodes and edges
- terminal normal-path intervals
- terminal fault-path intervals
- path-level time-ambiguous pairs

### 4.3 Diagnosability Enhancement

Implementation: [enhancement.py](/Users/lucas/Desktop/TPN_Diagnosability_Tool/src/algorithms/enhancement.py)

The current enhancement strategy uses a global plan:
- first try normal-path-exclusive transitions
- then fault-path-exclusive transitions
- finally shared transitions

If several ambiguous pairs can be covered by the same adjustable transition, the planner reuses that adjustment instead of adding a separate change for every pair.

## 5. Running the Tool

### Single File

```bash
MPLCONFIGDIR=/tmp/matplotlib python main.py \
  --input examples/example2.json \
  --max-length 5 \
  --output results/example2
```

### Batch Mode

```bash
MPLCONFIGDIR=/tmp/matplotlib python main.py \
  --batch examples \
  --max-length 5 \
  --output results/batch
```

### Tests

```bash
python -m unittest tests.test_algorithms tests.test_tpn
```

## 6. Outputs

### 6.1 Metrics JSON

Structure definition: [metrics.py](/Users/lucas/Desktop/TPN_Diagnosability_Tool/src/analysis/metrics.py)

Main fields:
- `observation_synchronizer.states`
- `observation_synchronizer.suspect_prefixes`
- `peterg.count`
- `peterg.total_nodes`
- `diagnosability.ambiguous_pairs`
- `diagnosability.resolved_pairs`
- `diagnosability.adjustments_made`
- `overall.total_states_explored`
- `overall.total_time`

### 6.2 Figures

Plotting implementation: [visualizer.py](/Users/lucas/Desktop/TPN_Diagnosability_Tool/src/analysis/visualizer.py)

The current batch dashboard contains 8 panels:
- state-space footprint
- runtime breakdown
- diagnosability outcomes
- prefix load and graph expansion
- adjustment efficiency
- exploration efficiency
- P-ETERG runtime share
- diagnosis process density

The current per-network dashboard contains 6 panels:
- runtime profile
- state and edge footprint
- process snapshot
- per-prefix P-ETERG load
- ranked prefix hotspots
- enhancement outcome

## 7. Example Networks

Paper-aligned examples:
- [example1.json](/Users/lucas/Desktop/TPN_Diagnosability_Tool/examples/example1.json)
- [example2.json](/Users/lucas/Desktop/TPN_Diagnosability_Tool/examples/example2.json)

Additional regression cases:
- [example3_time_separated.json](/Users/lucas/Desktop/TPN_Diagnosability_Tool/examples/example3_time_separated.json)
- [example4_shared_adjustment.json](/Users/lucas/Desktop/TPN_Diagnosability_Tool/examples/example4_shared_adjustment.json)
- [example5_hard_unresolvable.json](/Users/lucas/Desktop/TPN_Diagnosability_Tool/examples/example5_hard_unresolvable.json)
- [example6_global_shared_reuse.json](/Users/lucas/Desktop/TPN_Diagnosability_Tool/examples/example6_global_shared_reuse.json)

These cases cover:
- suspect prefixes that are already time-separated
- cases that can only be resolved through a shared transition
- cases blocked by hard constraints
- multiple ambiguous pairs reusing the same adjustment

## 8. Known Boundaries

This is still research-oriented code. Its outputs should not be treated as a paper-perfect numeric reproduction in every intermediate detail. Current boundaries include:
- the SCG is still a lightweight approximation, not the full linear-constraint state-class graph
- diagnosability enhancement is executable but not a strict per-candidate P-ETERG rebuild as in the paper
- when paper figures and formal definitions diverge, the repository currently follows the formal semantics

See [SEMANTICS_NOTES.md](/Users/lucas/Desktop/TPN_Diagnosability_Tool/docs/notes/SEMANTICS_NOTES.md) for details.
