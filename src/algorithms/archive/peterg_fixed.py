"""
P-ETERG (Partial Extremum Timed Extended Reachability Graph) 构造算法
修复版本 - 严格按照论文 Algorithm 2 实现
"""
from collections import deque
from typing import Set, Tuple, Dict, List
import copy


class ETERGNode:
    """ETERG 节点：(M, k, t_min, t_max, δ)"""
    
    def __init__(self, marking, k, tmin, tmax, delta):
        self.marking = marking  # 当前标识
        self.k = k              # 已匹配的观测前缀长度
        self.tmin = tmin        # 最小端到端延迟
        self.tmax = tmax        # 最大端到端延迟
        self.delta = delta      # 路径标签：'N' (normal) 或 'F' (fault)
    
    def __eq__(self, other):
        """
        论文中的状态去重条件：
        两个节点相同当且仅当 (M, k, δ) 相同
        注意：时间区间不参与去重判断
        """
        return (self.marking == other.marking and
                self.k == other.k and
                self.delta == other.delta)
    
    def __hash__(self):
        return hash((tuple(self.marking), self.k, self.delta))
    
    def __repr__(self):
        return f"S(M={self.marking}, k={self.k}, [{self.tmin:.2f},{self.tmax:.2f}], {self.delta})"


class PETERGBuilder:
    """P-ETERG 构造器"""
    
    def __init__(self, tpn, observation_prefix, fault_transitions):
        self.tpn = tpn
        self.observation_prefix = observation_prefix  # φ = (e1, e2, ..., em)
        self.fault_transitions = set(fault_transitions)
        self.nodes_explored = 0
    
    def build(self):
        """
        构造 P-ETERG
        论文 Algorithm 2: P-ETERG Construction
        
        Returns:
            (nodes, edges, initial_node)
        """
        m = len(self.observation_prefix)  # 观测前缀长度
        
        # 初始化：创建单个初始节点（论文 Algorithm 2, Line 3-5）
        M0 = self.tpn.initial_marking
        S0 = ETERGNode(
            marking=M0,
            k=0,
            tmin=0.0,
            tmax=0.0,
            delta='N'  # 初始标签为 N
        )
        
        S = {S0}  # 节点集合
        E = set()  # 边集合
        Q = deque([S0])  # BFS 队列
        
        # 用于时间区间合并的辅助字典
        # key: (M, k, δ), value: 该状态的所有时间区间
        state_intervals = {}
        state_intervals[(tuple(M0), 0, 'N')] = [(0.0, 0.0)]
        
        self.nodes_explored = 1
        
        # BFS 探索（论文 Algorithm 2, Line 6-20）
        while Q:
            current_node = Q.popleft()
            M, k, tmin, tmax, delta = (
                current_node.marking,
                current_node.k,
                current_node.tmin,
                current_node.tmax,
                current_node.delta
            )
            
            # 如果已经匹配完所有观测，停止扩展
            if k >= m:
                continue
            
            # 获取当前标识下的使能变迁
            enabled_transitions = self._get_enabled_transitions(M)
            
            for t in enabled_transitions:
                # 计算触发 t 后的新标识
                M_prime = self._fire_transition(M, t)
                
                # 计算新的路径标签
                delta_prime = 'F' if (delta == 'F' or t in self.fault_transitions) else 'N'
                
                # 计算新的观测匹配长度
                is_observable = (t.label is not None and t.label != '')
                
                if is_observable:
                    # 论文 Algorithm 2, Line 12-13
                    if k < m and t.label == self.observation_prefix[k]:
                        k_prime = k + 1  # 匹配成功
                    else:
                        # 观测不匹配，跳过此变迁
                        continue
                else:
                    # 不可观测变迁，k 不变
                    k_prime = k
                
                # 计算新的端到端延迟区间
                tmin_prime = tmin + t.time_constraint.earliest
                tmax_prime = tmax + t.time_constraint.latest
                
                # 状态去重和时间区间合并
                state_key = (tuple(M_prime), k_prime, delta_prime)
                
                if state_key in state_intervals:
                    # 状态已存在，合并时间区间
                    intervals = state_intervals[state_key]
                    intervals.append((tmin_prime, tmax_prime))
                    
                    # 更新节点的时间区间为所有路径的并集
                    all_tmin = min(iv[0] for iv in intervals)
                    all_tmax = max(iv[1] for iv in intervals)
                    
                    # 查找并更新现有节点
                    for node in S:
                        if (tuple(node.marking) == tuple(M_prime) and 
                            node.k == k_prime and 
                            node.delta == delta_prime):
                            node.tmin = all_tmin
                            node.tmax = all_tmax
                            break
                else:
                    # 新状态，添加到集合
                    state_intervals[state_key] = [(tmin_prime, tmax_prime)]
                    S.add(S_prime)
                    Q.append(S_prime)
                    self.nodes_explored += 1
                
                # 添加边
                E.add((current_node, t, S_prime))
        
        return PETERGResult(
            nodes=S,
            edges=E,
            initial_node=S0,
            observation_prefix=self.observation_prefix
        )
    
    def _get_enabled_transitions(self, marking):
        """获取当前标识下的使能变迁"""
        enabled = []
        for t in self.tpn.transitions:
            # 检查所有前置库所是否有足够的 token
            is_enabled = True
            for place_id, weight in t.pre.items():
                if marking.get(place_id, 0) < weight:
                    is_enabled = False
                    break
            if is_enabled:
                enabled.append(t)
        return enabled
    
    def _fire_transition(self, marking, transition):
        """触发变迁，返回新标识"""
        new_marking = marking.copy()
        
        # 移除前置库所的 token
        for place_id, weight in transition.pre.items():
            new_marking[place_id] = new_marking.get(place_id, 0) - weight
        
        # 添加后置库所的 token
        for place_id, weight in transition.post.items():
            new_marking[place_id] = new_marking.get(place_id, 0) + weight
        
        return new_marking


class PETERGResult:
    """P-ETERG 构造结果"""
    
    def __init__(self, nodes, edges, initial_node, observation_prefix):
        self.nodes = nodes
        self.edges = edges
        self.initial_node = initial_node
        self.observation_prefix = observation_prefix
    
    def get_terminal_nodes(self):
        """获取终端节点（k = m 的节点）"""
        m = len(self.observation_prefix)
        return [node for node in self.nodes if node.k == m]
    
    def get_normal_paths(self):
        """获取所有正常路径的端到端延迟区间"""
        terminal_nodes = self.get_terminal_nodes()
        normal_intervals = []
        for node in terminal_nodes:
            if node.delta == 'N':
                normal_intervals.append((node.tmin, node.tmax))
        return normal_intervals
    
    def get_fault_paths(self):
        """获取所有故障路径的端到端延迟区间"""
        terminal_nodes = self.get_terminal_nodes()
        fault_intervals = []
        for node in terminal_nodes:
            if node.delta == 'F':
                fault_intervals.append((node.tmin, node.tmax))
        return fault_intervals
    
    def has_time_ambiguity(self):
        """
        检测时间模糊性
        论文 Theorem 1: 如果存在正常路径和故障路径的时间区间重叠，则不可诊断
        """
        normal_intervals = self.get_normal_paths()
        fault_intervals = self.get_fault_paths()
        
        if not normal_intervals or not fault_intervals:
            return False
        
        # 检查是否存在重叠
        for n_min, n_max in normal_intervals:
            for f_min, f_max in fault_intervals:
                # 区间重叠条件：max(n_min, f_min) <= min(n_max, f_max)
                if max(n_min, f_min) <= min(n_max, f_max):
                    return True
        
        return False
    
    def __repr__(self):
        return (f"P-ETERG(nodes={len(self.nodes)}, edges={len(self.edges)}, "
                f"prefix={self.observation_prefix})")


def build_peterg(tpn, observation_prefix, fault_transitions):
    """
    构造 P-ETERG 的便捷函数
    
    Args:
        tpn: TPN 模型
        observation_prefix: 观测前缀，例如 ('a', 'b')
        fault_transitions: 故障变迁集合
    
    Returns:
        PETERGResult 对象
    """
    builder = PETERGBuilder(tpn, observation_prefix, fault_transitions)
    return builder.build()
