"""
TPN 模型测试
"""
import unittest
from src.tpn.model import (
    TPN, Transition, Arc, Marking, TimeConstraint,
    TransitionType, ConstraintType
)


class TestTPN(unittest.TestCase):
    
    def setUp(self):
        """设置测试用例"""
        # 创建简单的 TPN
        self.places = ["p1", "p2", "p3"]
        
        self.transitions = [
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
        
        self.arcs = [
            Arc("p1", "t1"),
            Arc("t1", "p2"),
            Arc("p2", "t2"),
            Arc("t2", "p3")
        ]
        
        self.initial_marking = Marking({"p1": 1, "p2": 0, "p3": 0})
        
        self.tpn = TPN(
            places=self.places,
            transitions=self.transitions,
            arcs=self.arcs,
            initial_marking=self.initial_marking
        )
    
    def test_tpn_creation(self):
        """测试 TPN 创建"""
        self.assertEqual(len(self.tpn.places), 3)
        self.assertEqual(len(self.tpn.transitions), 2)
        self.assertEqual(len(self.tpn.arcs), 4)
    
    def test_enabled_transitions(self):
        """测试使能变迁检测"""
        enabled = self.tpn.enabled_transitions(self.initial_marking)
        self.assertEqual(len(enabled), 1)
        self.assertEqual(list(enabled)[0].name, "t1")
    
    def test_fire_transition(self):
        """测试变迁触发"""
        t1 = self.tpn.get_transition("t1")
        new_marking = self.tpn.fire(self.initial_marking, t1)
        
        self.assertEqual(new_marking["p1"], 0)
        self.assertEqual(new_marking["p2"], 1)
        self.assertEqual(new_marking["p3"], 0)
    
    def test_fault_transitions(self):
        """测试故障变迁���别"""
        fault_transitions = self.tpn.get_fault_transitions()
        self.assertEqual(len(fault_transitions), 1)
        self.assertEqual(list(fault_transitions)[0].name, "t2")
    
    def test_observable_transitions(self):
        """测试可观测变迁识别"""
        observable = self.tpn.get_observable_transitions()
        self.assertEqual(len(observable), 1)
        self.assertEqual(list(observable)[0].name, "t1")


class TestMarking(unittest.TestCase):
    
    def test_marking_equality(self):
        """测试标识相等性"""
        m1 = Marking({"p1": 1, "p2": 0})
        m2 = Marking({"p1": 1, "p2": 0})
        m3 = Marking({"p1": 0, "p2": 1})
        
        self.assertEqual(m1, m2)
        self.assertNotEqual(m1, m3)
    
    def test_marking_hash(self):
        """测试标识哈希"""
        m1 = Marking({"p1": 1, "p2": 0})
        m2 = Marking({"p1": 1, "p2": 0})
        
        self.assertEqual(hash(m1), hash(m2))
        
        # 测试在集合中使用
        marking_set = {m1}
        self.assertIn(m2, marking_set)


if __name__ == '__main__':
    unittest.main()
