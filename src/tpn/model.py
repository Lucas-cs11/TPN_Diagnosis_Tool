"""
TPN (Time Petri Net) 数据结构定义
"""
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional
from enum import Enum


class TransitionType(Enum):
    """变迁类型"""
    NORMAL = "normal"
    FAULT = "fault"


class ConstraintType(Enum):
    """时间约束类型"""
    SOFT = "soft"
    HARD = "hard"


@dataclass
class TimeConstraint:
    """时间约束 [earliest, latest]"""
    earliest: float
    latest: float
    constraint_type: ConstraintType
    
    def __post_init__(self):
        if self.earliest > self.latest:
            raise ValueError(f"Invalid time constraint: [{self.earliest}, {self.latest}]")
    
    def __repr__(self):
        return f"[{self.earliest}, {self.latest}] ({self.constraint_type.value})"


@dataclass
class Transition:
    """变迁"""
    name: str
    transition_type: TransitionType
    observable: bool
    label: str  # 观测标签，不可观测变迁使用 "epsilon"
    time_constraint: TimeConstraint
    
    def is_fault(self) -> bool:
        return self.transition_type == TransitionType.FAULT
    
    def is_observable(self) -> bool:
        return self.observable and self.label != "epsilon"
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return isinstance(other, Transition) and self.name == other.name


@dataclass
class Arc:
    """弧（连接库所和变迁）"""
    source: str  # 库所或变迁名称
    target: str  # 库所或变迁名称
    weight: int = 1  # 弧权重，默认为 1


@dataclass
class Marking:
    """标识（marking）- 库所中的 token 分布"""
    tokens: Dict[str, int] = field(default_factory=dict)
    
    def __getitem__(self, place: str) -> int:
        return self.tokens.get(place, 0)
    
    def __setitem__(self, place: str, value: int):
        self.tokens[place] = value
    
    def copy(self) -> 'Marking':
        return Marking(tokens=self.tokens.copy())
    
    def __hash__(self):
        return hash(tuple(sorted(self.tokens.items())))
    
    def __eq__(self, other):
        return isinstance(other, Marking) and self.tokens == other.tokens
    
    def __repr__(self):
        return f"M{{{', '.join(f'{p}:{t}' for p, t in sorted(self.tokens.items()) if t > 0)}}}"


@dataclass
class TPN:
    """时间 Petri 网"""
    places: List[str]
    transitions: List[Transition]
    arcs: List[Arc]
    initial_marking: Marking
    
    # 派生属性
    _pre_matrix: Optional[Dict[Tuple[str, str], int]] = field(default=None, init=False, repr=False)
    _post_matrix: Optional[Dict[Tuple[str, str], int]] = field(default=None, init=False, repr=False)
    _transition_map: Optional[Dict[str, Transition]] = field(default=None, init=False, repr=False)
    
    def __post_init__(self):
        self._build_matrices()
        self._build_transition_map()
    
    def _build_matrices(self):
        """构建 Pre 和 Post 矩阵"""
        self._pre_matrix = {}
        self._post_matrix = {}
        
        for arc in self.arcs:
            # 判断弧的方向
            if arc.source in self.places and arc.target in [t.name for t in self.transitions]:
                # 库所 -> 变迁 (Pre)
                self._pre_matrix[(arc.source, arc.target)] = arc.weight
            elif arc.source in [t.name for t in self.transitions] and arc.target in self.places:
                # 变迁 -> 库所 (Post)
                self._post_matrix[(arc.source, arc.target)] = arc.weight
    
    def _build_transition_map(self):
        """构建变迁名称到变迁对象的映射"""
        self._transition_map = {t.name: t for t in self.transitions}
    
    def get_transition(self, name: str) -> Optional[Transition]:
        """根据名称获取变迁"""
        return self._transition_map.get(name)
    
    def pre(self, place: str, transition: str) -> int:
        """获取 Pre 矩阵值"""
        return self._pre_matrix.get((place, transition), 0)
    
    def post(self, transition: str, place: str) -> int:
        """获取 Post 矩阵值"""
        return self._post_matrix.get((transition, place), 0)
    
    def enabled_transitions(self, marking: Marking) -> Set[Transition]:
        """获取在给定标识下使能的变迁集合"""
        enabled = set()
        for transition in self.transitions:
            if self.is_enabled(marking, transition):
                enabled.add(transition)
        return enabled
    
    def is_enabled(self, marking: Marking, transition: Transition) -> bool:
        """检查变迁在给定标识下是否使能"""
        for place in self.places:
            if marking[place] < self.pre(place, transition.name):
                return False
        return True
    
    def fire(self, marking: Marking, transition: Transition) -> Marking:
        """触发变迁，返回新的标识"""
        if not self.is_enabled(marking, transition):
            raise ValueError(f"Transition {transition.name} is not enabled")
        
        new_marking = marking.copy()
        
        # 消耗输入库所的 token
        for place in self.places:
            new_marking[place] -= self.pre(place, transition.name)
        
        # 产生输出库所的 token
        for place in self.places:
            new_marking[place] += self.post(transition.name, place)
        
        return new_marking
    
    def get_fault_transitions(self) -> Set[Transition]:
        """获取所有故障变迁"""
        return {t for t in self.transitions if t.is_fault()}
    
    def get_observable_transitions(self) -> Set[Transition]:
        """获取所有可观测变迁"""
        return {t for t in self.transitions if t.is_observable()}
    
    def get_unobservable_transitions(self) -> Set[Transition]:
        """获取所有不可观测变迁"""
        return {t for t in self.transitions if not t.is_observable()}
    
    def get_soft_constraint_transitions(self) -> Set[Transition]:
        """获取所有软时间约束变迁"""
        return {t for t in self.transitions 
                if t.time_constraint.constraint_type == ConstraintType.SOFT}
    
    def get_hard_constraint_transitions(self) -> Set[Transition]:
        """获取所有硬时间约束变迁"""
        return {t for t in self.transitions 
                if t.time_constraint.constraint_type == ConstraintType.HARD}
    
    def __repr__(self):
        return (f"TPN(places={len(self.places)}, "
                f"transitions={len(self.transitions)}, "
                f"arcs={len(self.arcs)})")
