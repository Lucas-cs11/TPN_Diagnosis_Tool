"""
性能指标计算模块
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any
import time
import json
from pathlib import Path


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    
    # TPN 基本信息
    tpn_name: str = ""
    num_places: int = 0
    num_transitions: int = 0
    num_arcs: int = 0
    num_fault_transitions: int = 0
    
    # 观测同步器指标
    sync_states: int = 0
    sync_edges: int = 0
    sync_time: float = 0.0
    suspect_prefixes: int = 0
    
    # P-ETERG 指标
    peterg_count: int = 0
    total_peterg_nodes: int = 0
    total_peterg_edges: int = 0
    peterg_construction_time: float = 0.0
    
    # 可诊断性指标
    ambiguous_pairs: int = 0
    resolved_pairs: int = 0
    unresolved_pairs: int = 0
    adjustments_made: int = 0
    enhancement_time: float = 0.0
    
    # 总体指标
    total_time: float = 0.0
    total_states_explored: int = 0
    
    # 详细结果
    peterg_details: List[Dict[str, Any]] = field(default_factory=list)
    adjustment_details: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'tpn_info': {
                'name': self.tpn_name,
                'places': self.num_places,
                'transitions': self.num_transitions,
                'arcs': self.num_arcs,
                'fault_transitions': self.num_fault_transitions
            },
            'observation_synchronizer': {
                'states': self.sync_states,
                'edges': self.sync_edges,
                'time': self.sync_time,
                'suspect_prefixes': self.suspect_prefixes
            },
            'peterg': {
                'count': self.peterg_count,
                'total_nodes': self.total_peterg_nodes,
                'total_edges': self.total_peterg_edges,
                'construction_time': self.peterg_construction_time,
                'details': self.peterg_details
            },
            'diagnosability': {
                'ambiguous_pairs': self.ambiguous_pairs,
                'resolved_pairs': self.resolved_pairs,
                'unresolved_pairs': self.unresolved_pairs,
                'adjustments_made': self.adjustments_made,
                'enhancement_time': self.enhancement_time,
                'details': self.adjustment_details
            },
            'overall': {
                'total_time': self.total_time,
                'total_states_explored': self.total_states_explored
            }
        }
    
    def save_json(self, file_path: str):
        """保存为 JSON 文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def load_json(file_path: str) -> 'PerformanceMetrics':
        """从 JSON 文件加载"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        metrics = PerformanceMetrics()
        
        # TPN 信息
        tpn_info = data.get('tpn_info', {})
        metrics.tpn_name = tpn_info.get('name', '')
        metrics.num_places = tpn_info.get('places', 0)
        metrics.num_transitions = tpn_info.get('transitions', 0)
        metrics.num_arcs = tpn_info.get('arcs', 0)
        metrics.num_fault_transitions = tpn_info.get('fault_transitions', 0)
        
        # 观测同步器
        sync = data.get('observation_synchronizer', {})
        metrics.sync_states = sync.get('states', 0)
        metrics.sync_edges = sync.get('edges', 0)
        metrics.sync_time = sync.get('time', 0.0)
        metrics.suspect_prefixes = sync.get('suspect_prefixes', 0)
        
        # P-ETERG
        peterg = data.get('peterg', {})
        metrics.peterg_count = peterg.get('count', 0)
        metrics.total_peterg_nodes = peterg.get('total_nodes', 0)
        metrics.total_peterg_edges = peterg.get('total_edges', 0)
        metrics.peterg_construction_time = peterg.get('construction_time', 0.0)
        metrics.peterg_details = peterg.get('details', [])
        
        # 可诊断性
        diag = data.get('diagnosability', {})
        metrics.ambiguous_pairs = diag.get('ambiguous_pairs', 0)
        metrics.resolved_pairs = diag.get('resolved_pairs', 0)
        metrics.unresolved_pairs = diag.get('unresolved_pairs', 0)
        metrics.adjustments_made = diag.get('adjustments_made', 0)
        metrics.enhancement_time = diag.get('enhancement_time', 0.0)
        metrics.adjustment_details = diag.get('details', [])
        
        # 总体
        overall = data.get('overall', {})
        metrics.total_time = overall.get('total_time', 0.0)
        metrics.total_states_explored = overall.get('total_states_explored', 0)
        
        return metrics
    
    def print_summary(self):
        """打印性能摘要"""
        print("=" * 60)
        print(f"TPN Diagnosability Analysis Results: {self.tpn_name}")
        print("=" * 60)
        
        print("\n[TPN Information]")
        print(f"  Places: {self.num_places}")
        print(f"  Transitions: {self.num_transitions} (Fault: {self.num_fault_transitions})")
        print(f"  Arcs: {self.num_arcs}")
        
        print("\n[Observation Synchronizer]")
        print(f"  States: {self.sync_states}")
        print(f"  Edges: {self.sync_edges}")
        print(f"  Suspect Prefixes: {self.suspect_prefixes}")
        print(f"  Construction Time: {self.sync_time:.4f}s")
        
        print("\n[P-ETERG Construction]")
        print(f"  Number of P-ETERGs: {self.peterg_count}")
        print(f"  Total Nodes: {self.total_peterg_nodes}")
        print(f"  Total Edges: {self.total_peterg_edges}")
        print(f"  Construction Time: {self.peterg_construction_time:.4f}s")
        
        print("\n[Diagnosability Enhancement]")
        print(f"  Ambiguous Pairs: {self.ambiguous_pairs}")
        print(f"  Resolved: {self.resolved_pairs}")
        print(f"  Unresolved: {self.unresolved_pairs}")
        print(f"  Adjustments Made: {self.adjustments_made}")
        print(f"  Enhancement Time: {self.enhancement_time:.4f}s")
        
        print("\n[Overall Performance]")
        print(f"  Total States Explored: {self.total_states_explored}")
        print(f"  Total Time: {self.total_time:.4f}s")
        print("=" * 60)


class MetricsCollector:
    """性能指标收集器"""
    
    def __init__(self):
        self.metrics = PerformanceMetrics()
        self._start_time = None
        self._phase_start_time = None
    
    def start_timer(self):
        """开始总计时"""
        self._start_time = time.time()
    
    def end_timer(self):
        """结束总计时"""
        if self._start_time:
            self.metrics.total_time = time.time() - self._start_time
    
    def start_phase(self):
        """开始阶段计时"""
        self._phase_start_time = time.time()
    
    def end_phase(self) -> float:
        """结束阶段计时并返回耗时"""
        if self._phase_start_time:
            elapsed = time.time() - self._phase_start_time
            self._phase_start_time = None
            return elapsed
        return 0.0
    
    def get_metrics(self) -> PerformanceMetrics:
        """获取指标对象"""
        return self.metrics
