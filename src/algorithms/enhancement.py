"""
Algorithm 3: 可诊断性增强
基于论文中的伪代码实现，通过调整时间约束来消除时间模糊性
"""
from dataclasses import dataclass
from typing import Set, List, Tuple, Dict, Optional
from ..tpn.model import TPN, Transition, TimeConstraint, ConstraintType
from .peterg import PETERG, ETERGNode
import copy


@dataclass
class AdjustmentResult:
    """时间约束调整结果"""
    success: bool
    adjusted_transitions: Set[str]
    delta_req: float
    adjustment_type: str  # 'normal_only', 'fault_only', 'shared', 'failed'


class DiagnosabilityEnhancer:
    """可诊断性增强器 - 实现 Algorithm 3"""
    
    def __init__(self, tpn: TPN, epsilon: float = 0.1):
        """
        Args:
            tpn: 时间 Petri 网
            epsilon: 最小时间间隔增量
        """
        self.tpn = tpn
        self.epsilon = epsilon
        self.adjustments_made = 0
        self.unresolvable_pairs = []
    
    def enhance(self, ambiguous_pairs: List[Tuple[ETERGNode, ETERGNode]]) -> Tuple[TPN, List[AdjustmentResult]]:
        """对所有时间模糊对进行可诊断性增强
        
        Args:
            ambiguous_pairs: 时间模糊的节点对列表 [(正常节点, 故障节点), ...]
        
        Returns:
            (增强后的 TPN, 调整结果列表)
        """
        enhanced_tpn = copy.deepcopy(self.tpn)
        results = []
        
        for normal_node, fault_node in ambiguous_pairs:
            result = self._resolve_ambiguity(enhanced_tpn, normal_node, fault_node)
            results.append(result)
            
            if not result.success:
                self.unresolvable_pairs.append((normal_node, fault_node))
        
        return enhanced_tpn, results
    
    def _resolve_ambiguity(
        self,
        tpn: TPN,
        normal_node: ETERGNode,
        fault_node: ETERGNode
    ) -> AdjustmentResult:
        """解决单个时间模糊对
        
        基于 Algorithm 3 的三阶段策略：
        1. 仅调整正常路径的变迁
        2. 仅调整故障路径的变迁
        3. 调整共享变迁
        """
        # 计算所需的时间间隔
        delta_ovlp = self._calculate_overlap(normal_node, fault_node)
        delta_req = delta_ovlp + self.epsilon
        
        # 提取路径上的变迁（这里简化处理，实际需要路径回溯）
        # 假设我们有方法获取到达每个节点的路径
        normal_path_transitions = self._extract_path_transitions(normal_node)
        fault_path_transitions = self._extract_path_transitions(fault_node)
        
        # 识别独占和共享变迁
        normal_exclusive = normal_path_transitions - fault_path_transitions
        fault_exclusive = fault_path_transitions - normal_path_transitions
        shared = normal_path_transitions & fault_path_transitions
        
        # 阶段 1: 仅调整正常路径独占变迁
        if self._adjust_time_intervals(tpn, normal_exclusive, delta_req):
            self.adjustments_made += 1
            return AdjustmentResult(
                success=True,
                adjusted_transitions=normal_exclusive,
                delta_req=delta_req,
                adjustment_type='normal_only'
            )
        
        # 阶段 2: 仅调整故障路径独占变迁
        if self._adjust_time_intervals(tpn, fault_exclusive, delta_req):
            self.adjustments_made += 1
            return AdjustmentResult(
                success=True,
                adjusted_transitions=fault_exclusive,
                delta_req=delta_req,
                adjustment_type='fault_only'
            )
        
        # 阶段 3: 调整共享变迁
        if self._adjust_time_intervals(tpn, shared, delta_req):
            self.adjustments_made += 1
            return AdjustmentResult(
                success=True,
                adjusted_transitions=shared,
                delta_req=delta_req,
                adjustment_type='shared'
            )
        
        # 无法解决
        return AdjustmentResult(
            success=False,
            adjusted_transitions=set(),
            delta_req=delta_req,
            adjustment_type='failed'
        )
    
    def _calculate_overlap(self, node1: ETERGNode, node2: ETERGNode) -> float:
        """计算两个节点时间区间的重叠量"""
        overlap_start = max(node1.tmin, node2.tmin)
        overlap_end = min(node1.tmax, node2.tmax)
        return max(0, overlap_end - overlap_start)
    
    def _extract_path_transitions(self, node: ETERGNode) -> Set[str]:
        """提取到达节点的路径上的变迁集合
        
        注意：这是简化实现，实际需要在 P-ETERG 构造时记录路径信息
        """
        # TODO: 实际实现需要在 PETERG 中维护路径信息
        # 这里返回空集作为占位
        return set()
    
    def _adjust_time_intervals(
        self,
        tpn: TPN,
        transition_names: Set[str],
        delta_req: float
    ) -> bool:
        """尝试调整指定变迁的时间约束
        
        Args:
            tpn: TPN 网络
            transition_names: 要调整的变迁名称集合
            delta_req: 所需的时间间隔增量
        
        Returns:
            是否成功调整
        """
        if not transition_names:
            return False
        
        # 检查所有变迁是否都有软时间约束
        adjustable_transitions = []
        for t_name in transition_names:
            t = tpn.get_transition(t_name)
            if t and t.time_constraint.constraint_type == ConstraintType.SOFT:
                adjustable_transitions.append(t)
        
        if not adjustable_transitions:
            return False
        
        # 平均分配时间增量到每个可调整的变迁
        delta_per_transition = delta_req / len(adjustable_transitions)
        
        for t in adjustable_transitions:
            # 扩展时间区间的上界
            new_latest = t.time_constraint.latest + delta_per_transition
            t.time_constraint.latest = new_latest
        
        return True
    
    def get_statistics(self) -> Dict[str, any]:
        """获取增强统计信息"""
        return {
            'adjustments_made': self.adjustments_made,
            'unresolvable_pairs': len(self.unresolvable_pairs)
        }


def enhance_diagnosability(
    tpn: TPN,
    ambiguous_pairs: List[Tuple[ETERGNode, ETERGNode]],
    epsilon: float = 0.1
) -> Tuple[TPN, List[AdjustmentResult], Dict[str, any]]:
    """可诊断性增强的便捷函数
    
    Args:
        tpn: 时间 Petri 网
        ambiguous_pairs: 时间模糊的节点对
        epsilon: 最小时间间隔增量
    
    Returns:
        (增强后的 TPN, 调整结果列表, 统计信息)
    """
    enhancer = DiagnosabilityEnhancer(tpn, epsilon)
    enhanced_tpn, results = enhancer.enhance(ambiguous_pairs)
    stats = enhancer.get_statistics()
    return enhanced_tpn, results, stats
