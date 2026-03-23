"""
Minimal SCG construction for event-driven observation synchronization.

This is a lightweight state-class approximation built on top of the same strong
time-semantics interval propagation currently used by the P-ETERG layer.
"""
from dataclasses import dataclass
from typing import Dict, FrozenSet, Optional, Set, Tuple
from collections import deque

from .model import TPN, Marking


@dataclass(frozen=True)
class StateClass:
    """Approximate SCG state class."""
    id: int
    marking_key: Tuple[Tuple[str, int], ...]
    intervals_key: Tuple[Tuple[str, Tuple[float, float]], ...]

    @property
    def marking(self) -> Dict[str, int]:
        return dict(self.marking_key)

    @property
    def intervals(self) -> Dict[str, Tuple[float, float]]:
        return dict(self.intervals_key)


@dataclass(frozen=True)
class StateClassEdge:
    source_id: int
    transition_name: str
    target_id: int
    observable_label: Optional[str]
    is_fault: bool


class SCG:
    """Minimal state class graph."""

    def __init__(self, classes, edges, initial_class_id):
        self.classes = classes
        self.edges = edges
        self.initial_class_id = initial_class_id
        self._outgoing = {}
        for edge in edges:
            self._outgoing.setdefault(edge.source_id, []).append(edge)

    def outgoing(self, class_id: int):
        return self._outgoing.get(class_id, [])

    def reachable_via_event(self, class_ids: FrozenSet[int], event: str, allow_faults: bool) -> Tuple[FrozenSet[int], bool]:
        """Reach target classes via pre-event and post-event unobservable closure."""
        pre_queue = deque([(class_id, False) for class_id in class_ids])
        pre_visited = set(pre_queue)
        event_targets = []

        while pre_queue:
            current_id, seen_fault = pre_queue.popleft()
            for edge in self.outgoing(current_id):
                if edge.observable_label is None:
                    if edge.is_fault and not allow_faults:
                        continue
                    next_state = (edge.target_id, seen_fault or edge.is_fault)
                    if next_state not in pre_visited:
                        pre_visited.add(next_state)
                        pre_queue.append(next_state)
                    continue

                if edge.observable_label == event:
                    event_targets.append((edge.target_id, seen_fault or edge.is_fault))

        post_queue = deque(event_targets)
        post_visited = set(post_queue)
        targets = set()
        used_fault = False

        while post_queue:
            current_id, seen_fault = post_queue.popleft()
            targets.add(current_id)
            if seen_fault:
                used_fault = True

            for edge in self.outgoing(current_id):
                if edge.observable_label is not None:
                    continue
                if edge.is_fault and not allow_faults:
                    continue
                next_state = (edge.target_id, seen_fault or edge.is_fault)
                if next_state not in post_visited:
                    post_visited.add(next_state)
                    post_queue.append(next_state)

        return frozenset(targets), used_fault


class SCGBuilder:
    """Build a lightweight state-class graph from a TPN."""

    def __init__(self, tpn: TPN):
        self.tpn = tpn
        self._next_id = 0

    @staticmethod
    def _marking_key(marking):
        return tuple(sorted(marking.items()))

    @staticmethod
    def _intervals_key(intervals):
        return tuple(sorted(intervals.items()))

    @staticmethod
    def _compute_feasible_fire_window(transition_name: str, intervals: Dict[str, Tuple[float, float]]) -> Tuple[float, float]:
        alpha_t, beta_t = intervals[transition_name]
        global_latest_bound = min(beta for _, beta in intervals.values())
        return alpha_t, min(beta_t, global_latest_bound)

    def _enabled_transitions(self, marking):
        enabled = []
        for transition in self.tpn.transitions:
            if self.tpn.is_enabled(Marking(marking.copy()), transition):
                enabled.append(transition)
        return enabled

    def _initialize_intervals(self, marking):
        intervals = {}
        for transition in self._enabled_transitions(marking):
            intervals[transition.name] = (
                transition.time_constraint.earliest,
                transition.time_constraint.latest
            )
        return intervals

    def _compute_new_intervals(self, marking, marking_prime, fired_name, intervals, fire_min, fire_max):
        intervals_prime = {}
        enabled_before = {transition.name for transition in self._enabled_transitions(marking)}
        enabled_after = self._enabled_transitions(marking_prime)

        for transition in enabled_after:
            if transition.name in enabled_before and transition.name != fired_name:
                old_min, old_max = intervals[transition.name]
                intervals_prime[transition.name] = (
                    max(0.0, old_min - fire_max),
                    old_max - fire_min
                )
            else:
                intervals_prime[transition.name] = (
                    transition.time_constraint.earliest,
                    transition.time_constraint.latest
                )

        return intervals_prime

    def build(self) -> SCG:
        initial_marking = self.tpn.initial_marking.tokens.copy()
        initial_intervals = self._initialize_intervals(initial_marking)

        initial_class = StateClass(
            id=self._next_id,
            marking_key=self._marking_key(initial_marking),
            intervals_key=self._intervals_key(initial_intervals)
        )
        self._next_id += 1

        classes = {initial_class.id: initial_class}
        class_map = {
            (initial_class.marking_key, initial_class.intervals_key): initial_class.id
        }
        edges = set()
        queue = deque([initial_class.id])

        while queue:
            class_id = queue.popleft()
            current = classes[class_id]
            marking = current.marking
            intervals = current.intervals

            for transition in self._enabled_transitions(marking):
                if transition.name not in intervals:
                    continue
                fire_min, fire_max = self._compute_feasible_fire_window(transition.name, intervals)
                if fire_min > fire_max:
                    continue

                marking_prime = self.tpn.fire(Marking(marking.copy()), transition).tokens
                intervals_prime = self._compute_new_intervals(
                    marking,
                    marking_prime,
                    transition.name,
                    intervals,
                    fire_min,
                    fire_max
                )

                target_key = (self._marking_key(marking_prime), self._intervals_key(intervals_prime))
                if target_key in class_map:
                    target_id = class_map[target_key]
                else:
                    target_id = self._next_id
                    self._next_id += 1
                    new_class = StateClass(
                        id=target_id,
                        marking_key=target_key[0],
                        intervals_key=target_key[1]
                    )
                    classes[target_id] = new_class
                    class_map[target_key] = target_id
                    queue.append(target_id)

                edges.add(StateClassEdge(
                    source_id=class_id,
                    transition_name=transition.name,
                    target_id=target_id,
                    observable_label=transition.label if transition.is_observable() else None,
                    is_fault=transition.is_fault()
                ))

        return SCG(classes=classes, edges=edges, initial_class_id=initial_class.id)


def build_scg(tpn: TPN) -> SCG:
    return SCGBuilder(tpn).build()
