"""
TPN 输入解析器 - 从 JSON 文件加载 TPN 网络
"""
import json
from pathlib import Path
from typing import Dict, Any
from .model import TPN, Transition, Arc, Marking, TimeConstraint, TransitionType, ConstraintType


class TPNParser:
    """TPN JSON 解析器"""
    
    @staticmethod
    def parse_file(file_path: str) -> TPN:
        """从 JSON 文件解析 TPN"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return TPNParser.parse_dict(data)
    
    @staticmethod
    def parse_dict(data: Dict[str, Any]) -> TPN:
        """从字典解析 TPN"""
        # 解析库所
        places = data.get('places', [])
        
        # 解析变迁
        transitions = []
        for t_data in data.get('transitions', []):
            transition = TPNParser._parse_transition(t_data)
            transitions.append(transition)
        
        # 解析弧
        arcs = []
        for arc_data in data.get('arcs', []):
            arc = TPNParser._parse_arc(arc_data)
            arcs.append(arc)
        
        # 解析初始标识
        initial_marking = TPNParser._parse_marking(data.get('initial_marking', {}))
        
        return TPN(
            places=places,
            transitions=transitions,
            arcs=arcs,
            initial_marking=initial_marking
        )
    
    @staticmethod
    def _parse_transition(data: Dict[str, Any]) -> Transition:
        """解析变迁"""
        name = data['name']
        
        # 解析变迁类型
        t_type_str = data.get('type', 'normal').lower()
        transition_type = TransitionType.FAULT if t_type_str == 'fault' else TransitionType.NORMAL
        
        # 解析可观测性
        observable = data.get('observable', True)
        label = data.get('label', name)
        
        # 解析时间约束
        tc_data = data.get('time_constraint', {})
        time_constraint = TPNParser._parse_time_constraint(tc_data)
        
        return Transition(
            name=name,
            transition_type=transition_type,
            observable=observable,
            label=label,
            time_constraint=time_constraint
        )
    
    @staticmethod
    def _parse_time_constraint(data: Dict[str, Any]) -> TimeConstraint:
        """解析时间约束"""
        earliest = float(data.get('earliest', 0))
        latest = float(data.get('latest', float('inf')))
        
        # 解析约束类型
        c_type_str = data.get('type', 'soft').lower()
        constraint_type = ConstraintType.SOFT if c_type_str == 'soft' else ConstraintType.HARD
        
        return TimeConstraint(
            earliest=earliest,
            latest=latest,
            constraint_type=constraint_type
        )
    
    @staticmethod
    def _parse_arc(data: Dict[str, Any]) -> Arc:
        """解析弧"""
        source = data['from']
        target = data['to']
        weight = data.get('weight', 1)
        
        return Arc(source=source, target=target, weight=weight)
    
    @staticmethod
    def _parse_marking(data: Dict[str, int]) -> Marking:
        """解析标识"""
        return Marking(tokens=data.copy())
    
    @staticmethod
    def save_tpn(tpn: TPN, file_path: str):
        """将 TPN 保存为 JSON 文件"""
        data = {
            'places': tpn.places,
            'transitions': [
                {
                    'name': t.name,
                    'type': t.transition_type.value,
                    'observable': t.observable,
                    'label': t.label,
                    'time_constraint': {
                        'type': t.time_constraint.constraint_type.value,
                        'earliest': t.time_constraint.earliest,
                        'latest': t.time_constraint.latest
                    }
                }
                for t in tpn.transitions
            ],
            'arcs': [
                {
                    'from': arc.source,
                    'to': arc.target,
                    'weight': arc.weight
                }
                for arc in tpn.arcs
            ],
            'initial_marking': tpn.initial_marking.tokens
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# 便捷函数
def load_tpn(file_path: str) -> TPN:
    """加载 TPN 文件"""
    return TPNParser.parse_file(file_path)


def save_tpn(tpn: TPN, file_path: str):
    """保存 TPN 文件"""
    TPNParser.save_tpn(tpn, file_path)
