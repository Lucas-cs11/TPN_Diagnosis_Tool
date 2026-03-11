"""
算法测试
"""
import unittest
from src.tpn.model import (
    TPN, Transition, Arc, Marking, TimeConstraint,
    TransitionType, ConstraintType
)
from src.algorithms.observation_sync import build_observation_synchronizer
from src.algorithms.peterg import build_peterg


class TestObservationSynchronizer(unittest.TestCase):
    
    def setUp(self):
        """设置测试用例"""
        places = ["p1", "p2", "p3"]
        
        transitions = [
            Transition(
                name="t1",
                transition_type=TransitionType.NORMAL,
                observable=True,
                label="a",
                time_constraint=TimeConstraint(1, 3, ConstraintType.SOFT)
            ),
            Transition(
                name="t2",
                transition_type=TransitionType.NORMAL,
                observable=True,
                label="b",
                time_constraint=TimeConstraint(2, 4, ConstraintType.SOFT)
            )
        ]
        
        arcs = [
            Arc("p1", "t1"),
            Arc("t1", "p2"),
            Arc("p2", "t2"),
            Arc("t2", "p3")
        ]
        
        initial_marking = Marking({"p1": 1, "p2": 0, "p3": 0})
        
        self.tpn = TPN(
            places=places,
            transitions=transitions,
            arcs=arcs,
            initial_marking=initial_marking
        )
    
    def test_synchronizer_construction(self):
        """测试观测同步器构造"""
        synchronizer, stats = build_observation_synchronizer(self.tpn, max_length=3)
        
        self.assertIsNotNone(synchronizer)
        self.assertGreater(len(synchronizer.states), 0)
        self.assertGreater(stats['states_explored'], 0)
    
    def test_synchronizer_initial_state(self):
        """测试初始状态"""
        synchronizer, _ = build_observation_synchronizer(self.tpn, max_length=3)
        
        self.assertIsNotNone(synchronizer.initial_state)
        self.assertEqual(synchronizer.initial_state.k, 0)
        self.assertEqual(synchronizer.initial_state.marking, self.tpn.initial_marking)


class TestPETERG(unittest.TestCase):
    
    def setUp(self):
        """设置测试用例"""
        places = ["p1", "p2", "p3"]
        
        transitions = [
            Transition(
                name="t1",
                transition_type=TransitionType.NORMAL,
                observable=True,
                label="a",
                time_constraint=TimeConstraint(1, 3, ConstraintType.SOFT)
            ),
            Transition(
                name="t2",
                transition_type=TransitionType.FAULT,
                observable=False,
                label="epsilon",
                time_constraint=TimeConstraint(0, 2, ConstraintType.HARD)
            )
        ]
        
        arcs = [
            Arc("p1", "t1"),
            Arc("t1", "p2"),
            Arc("p2", "t2"),
            Arc("t2", "p3")
        ]
        
        initial_marking = Marking({"p1": 1, "p2": 0, "p3": 0})
        
        self.tpn = TPN(
            places=places,
            transitions=transitions,
            arcs=arcs,
            initial_marking=initial_marking
        )
    
    def test_peterg_construction(self):
        """测试 P-ETERG 构造"""
        observation_prefix = ("a",)
        peterg, stats = build_peterg(self.tpn, observation_prefix)
        
        self.assertIsNotNone(peterg)
        self.assertGreater(len(peterg.nodes), 0)
        self.assertEqual(peterg.observation_prefix, observation_prefix)
    
    def test_peterg_initial_nodes(self):
        """测试初始节点"""
        observation_prefix = ("a",)
        peterg, _ = build_peterg(self.tpn, observation_prefix)
        
        self.assertEqual(len(peterg.initial_nodes), 2)  # 正常和故障两个初始节点


if __name__ == '__main__':
    unittest.main()
