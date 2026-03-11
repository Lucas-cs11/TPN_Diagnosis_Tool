"""
Algorithm 1: 观测同步器构造
基于论文中的伪代码实现
"""
from dataclasses import dataclass, field
from typing import Set, List, Tuple, Dict, Optional
from collections import deque
from ..tpn.model import TPN, Marking, Transition


@dataclass(frozen=True)
class SyncState:
    """观测同步器状态 (M, k)
    M: 标识
    k: 已匹配的观测前缀长度
    """
    marking: Marking
    k: int
    
    def __hash__(self):
        return hash((self.marking, self.k))
    
    def __eq__(self, other):
        return isinstance(other, SyncState) and \
               self.marking == other.marking and \
               self.k == other.k


@dataclass
class ObservationSynchronizer:
    """观测同步器 M_syn = (S, E, S0)"""
    states: Set[SyncState]
    edges: Set[Tuple[SyncState, Transition, SyncState]]
    initial_state: SyncState
    
    def get_suspect_prefixes(self, max_length: int) -> Set[Tuple[str, ...]]:
        """获取可疑观测前缀集合 Φ_sus
        
        可疑观测前缀：存在正常路径和故障路径产生相同观测序列的前缀
        """
        suspect_prefixes = set()
        
        # 按观测前缀长度分组状态
        states_by_prefix: Dict[int, Set[SyncState]] = {}
        for state in self.states:
            if state.k <= max_length:
                if state.k not in states_by_prefix:
                    states_by_prefix[state.k] = set()
                states_by_prefix[state.k].add(state)
        
        # 对每个长度，检查是否存在不同标识但相同观测前缀的状态
        for k, states_set in states_by_prefix.items():
            if k == 0:
                continue
            
            # 提取到达每个状态的观测序列
            # 这里需要回溯路径，暂时简化：如果存在多个不同标识的状态具有相同 k，
            # 则认为可能存在可疑前缀
            markings_at_k = {state.marking for state in states_set}
            if len(markings_at_k) > 1:
                # 需要进一步检查是否有正常路径和故障路径
                # 这里简化处理，实际需要路径标签信息
                pass
        
        return suspect_prefixes
    
    def get_terminal_states(self, prefix_length: int) -> Set[SyncState]:
        """获取特定观测前缀长度的终止状态"""
        return {s for s in self.states if s.k == prefix_length}


class ObservationSynchronizerBuilder:
    """观测同步器构造器 - 实现 Algorithm 1"""
    
    def __init__(self, tpn: TPN, max_length: int):
        self.tpn = tpn
        self.max_length = max_length
        self.states_explored = 0
        self.edges_created = 0
    
    def build(self) -> ObservationSynchronizer:
        """构造观测同步器
        
        基于��文 Algorithm 1 的 BFS 构造方法
        """
        # 初始化
        S0 = SyncState(marking=self.tpn.initial_marking, k=0)
        S = {S0}
        E = set()
        Q = deque([S0])
        Q_visited = {S0}
        
        # BFS 探索
        while Q:
            current_state = Q.popleft()
            M, k = current_state.marking, current_state.k
            
            # 如果已达到最大观测长度，停止扩展
            if k >= self.max_length:
                continue
            
            # 获取使能的变迁
            enabled = self.tpn.enabled_transitions(M)
            
            for t in enabled:
                # 触发变迁，得到新标识
                M_prime = self.tpn.fire(M, t)
                
                # 更新观测前缀长度
                if t.is_observable():
                    k_prime = k + 1
                else:
                    k_prime = k
                
                # 创建新状态
                S_prime = SyncState(marking=M_prime, k=k_prime)
                
                # 如果是新状态，加入队列
                if S_prime not in Q_visited:
                    S.add(S_prime)
                    Q.append(S_prime)
                    Q_visited.add(S_prime)
                    self.states_explored += 1
                
                # 添加边
                E.add((current_state, t, S_prime))
                self.edges_created += 1
        
        return ObservationSynchronizer(
            states=S,
            edges=E,
            initial_state=S0
        )
    
    def get_statistics(self) -> Dict[str, int]:
        """获取构造统计信息"""
        return {
            'states_explored': self.states_explored,
            'edges_created': self.edges_created
        }


def build_observation_synchronizer(tpn: TPN, max_length: int) -> Tuple[ObservationSynchronizer, Dict[str, int]]:
    """构造观测同步器的便捷函数
    
    Args:
        tpn: 时间 Petri 网
        max_length: 最大观测前缀长度
    
    Returns:
        (观测同步器, 统计信息)
    """
    builder = ObservationSynchronizerBuilder(tpn, max_length)
    synchronizer = builder.build()
    stats = builder.get_statistics()
    return synchronizer, stats
