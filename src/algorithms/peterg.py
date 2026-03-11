"""
Algorithm 2: P-ETERG (Prefix-based Extended Timed Execution Reachability Graph) 构造
基于论文中的伪代码实现
"""
from dataclasses import dataclass, field
from typing import Set, List, Tuple, Dict, Optional
from collections import deque
from ..tpn.model import TPN, Marking, Transition


@dataclass(frozen=True)
class ETERGNode:
    """P-ETERG 节点 S = (M, k, tmin, tmax, ∆)
    
    M: 标识
    k: 观测前缀长度
    tmin: 最早到达时间
    tmax: 最晚到达时间
    delta: 路径标签 (N=normal, F=fault)
    """
    marking: Marking
    k: int
    tmin: float
    tmax: float
    delta: str  # 'N' or 'F'
    
    def __hash__(self):
        return hash((self.marking, self.k, self.tmin, self.tmax, self.delta))
    
    def __eq__(self, other):
        return isinstance(other, ETERGNode) and \
               self.marking == other.marking and \
               self.k == other.k and \
               abs(self.tmin - other.tmin) < 1e-9 and \
               abs(self.tmax - other.tmax) < 1e-9 and \
               self.delta == other.delta
    
    def __repr__(self):
        return f"S({self.marking}, k={self.k}, [{self.tmin:.2f}, {self.tmax:.2f}], {self.delta})"


@dataclass
class PETERG:
    """P-ETERG = (S, E, S0)"""
    nodes: Set[ETERGNode]
    edges: Set[Tuple[ETERGNode, Transition, ETERGNode]]
    initial_nodes: Set[ETERGNode]
    observation_prefix: Tuple[str, ...]  # 对应的观测前缀
    
    def get_terminal_nodes(self) -> Set[ETERGNode]:
        """获取终止节点（k = m 的节点）"""
        if not self.nodes:
            return set()
        max_k = max(node.k for node in self.nodes)
        return {node for node in self.nodes if node.k == max_k}
    
    def get_normal_terminal_nodes(self) -> Set[ETERGNode]:
        """获取正常路径的终止节点"""
        return {node for node in self.get_terminal_nodes() if node.delta == 'N'}
    
    def get_fault_terminal_nodes(self) -> Set[ETERGNode]:
        """获取故障路径的终止节点"""
        return {node for node in self.get_terminal_nodes() if node.delta == 'F'}
    
    def has_time_ambiguity(self) -> bool:
        """检查是否存在时间模糊性
        
        如果存在正常终止节点和故障终止节点的时间区间重叠，则存在时间模糊性
        """
        normal_nodes = self.get_normal_terminal_nodes()
        fault_nodes = self.get_fault_terminal_nodes()
        
        for n_node in normal_nodes:
            for f_node in fault_nodes:
                # 检查时间区间是否重叠
                if self._intervals_overlap(
                    n_node.tmin, n_node.tmax,
                    f_node.tmin, f_node.tmax
                ):
                    return True
        return False
    
    @staticmethod
    def _intervals_overlap(min1: float, max1: float, min2: float, max2: float) -> bool:
        """检查两个时间区间是否重叠"""
        return not (max1 < min2 or max2 < min1)
    
    def get_ambiguous_pairs(self) -> List[Tuple[ETERGNode, ETERGNode]]:
        """获取所有时间模糊的节点对 (正常节点, 故障节点)"""
        pairs = []
        normal_nodes = self.get_normal_terminal_nodes()
        fault_nodes = self.get_fault_terminal_nodes()
        
        for n_node in normal_nodes:
            for f_node in fault_nodes:
                if self._intervals_overlap(
                    n_node.tmin, n_node.tmax,
                    f_node.tmin, f_node.tmax
                ):
                    pairs.append((n_node, f_node))
        
        return pairs


class PETERGBuilder:
    """P-ETERG 构造器 - 实现 Algorithm 2"""
    
    def __init__(self, tpn: TPN, observation_prefix: Tuple[str, ...]):
        self.tpn = tpn
        self.observation_prefix = observation_prefix
        self.nodes_explored = 0
        self.edges_created = 0
    
    def build(self) -> PETERG:
        """构造 P-ETERG
        
        基于论文 Algorithm 2 的构造方法
        """
        m = len(self.observation_prefix)
        
        # 初始化：创建初始节点（正常和故障两个版本）
        S0_normal = ETERGNode(
            marking=self.tpn.initial_marking,
            k=0,
            tmin=0.0,
            tmax=0.0,
            delta='N'
        )
        
        S0_fault = ETERGNode(
            marking=self.tpn.initial_marking,
            k=0,
            tmin=0.0,
            tmax=0.0,
            delta='F'
        )
        
        S = {S0_normal, S0_fault}
        E = set()
        Q = deque([S0_normal, S0_fault])
        Q_visited = {S0_normal, S0_fault}
        
        # BFS 探索
        while Q:
            current_node = Q.popleft()
            M, k, tmin, tmax, delta = (
                current_node.marking,
                current_node.k,
                current_node.tmin,
                current_node.tmax,
                current_node.delta
            )
            
            # 如果已达到观测前缀长度，停止扩展
            if k >= m:
                continue
            
            # 获取使能的变迁
            enabled = self.tpn.enabled_transitions(M)
            
            for t in enabled:
                # 检查路径标签约束
                if delta == 'N' and t.is_fault():
                    # 正常路径不能触发故障变迁
                    continue
                
                # 触发变迁
                M_prime = self.tpn.fire(M, t)
                
                # 更新观测前缀长度
                if t.is_observable():
                    k_prime = k + 1
                    # 检查观测是否匹配
                    if k_prime <= m and t.label != self.observation_prefix[k_prime - 1]:
                        continue
                else:
                    k_prime = k
                
                # 更新时间区间
                tmin_prime = tmin + t.time_constraint.earliest
                tmax_prime = tmax + t.time_constraint.latest
                
                # 更新路径标签
                if t.is_fault():
                    delta_prime = 'F'
                else:
                    delta_prime = delta
                
                # 创建新节点
                S_prime = ETERGNode(
                    marking=M_prime,
                    k=k_prime,
                    tmin=tmin_prime,
                    tmax=tmax_prime,
                    delta=delta_prime
                )
                
                # 如果是新节点，加入队列
                if S_prime not in Q_visited:
                    S.add(S_prime)
                    Q.append(S_prime)
                    Q_visited.add(S_prime)
                    self.nodes_explored += 1
                
                # 添加边
                E.add((current_node, t, S_prime))
                self.edges_created += 1
        
        return PETERG(
            nodes=S,
            edges=E,
            initial_nodes={S0_normal, S0_fault},
            observation_prefix=self.observation_prefix
        )
    
    def get_statistics(self) -> Dict[str, int]:
        """获取构造统计信息"""
        return {
            'nodes_explored': self.nodes_explored,
            'edges_created': self.edges_created
        }


def build_peterg(tpn: TPN, observation_prefix: Tuple[str, ...]) -> Tuple[PETERG, Dict[str, int]]:
    """构造 P-ETERG 的便捷函数
    
    Args:
        tpn: 时间 Petri 网
        observation_prefix: 观测前缀序列
    
    Returns:
        (P-ETERG, 统计信息)
    """
    builder = PETERGBuilder(tpn, observation_prefix)
    peterg = builder.build()
    stats = builder.get_statistics()
    return peterg, stats
