"""
调试 P-ETERG 构造过程
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from tpn.model import TPN, Transition, TimeConstraint
from algorithms.peterg_fixed import ETERGNode
from collections import deque


def load_tpn_from_json(json_path):
    """从 JSON 文件加载 TPN"""
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    places = data['places']
    place_ids = [p['id'] for p in places]
    
    transitions = []
    for t_data in data['transitions']:
        t = Transition(
            id=t_data['id'],
            name=t_data['name'],
            label=t_data.get('label'),
            time_constraint=TimeConstraint(
                t_data['time_constraint']['earliest'],
                t_data['time_constraint']['latest']
            ),
            is_fault=t_data.get('is_fault', False)
        )
        t.pre = {p: w for p, w in t_data['pre'].items()}
        t.post = {p: w for p, w in t_data['post'].items()}
        transitions.append(t)
    
    initial_marking = {p: w for p, w in data['initial_marking'].items()}
    
    tpn = TPN(
        places=place_ids,
        transitions=transitions,
        initial_marking=initial_marking
    )
    
    return tpn


def debug_peterg_construction(tpn, observation_prefix, fault_transitions):
    """调试 P-ETERG 构造过程"""
    print(f"\n{'='*80}")
    print(f"调试 P-ETERG 构造: φ = {observation_prefix}")
    print(f"{'='*80}\n")
    
    m = len(observation_prefix)
    M0 = tpn.initial_marking
    fault_set = set(fault_transitions)
    
    S0 = ETERGNode(M0, 0, 0.0, 0.0, 'N')
    S = {S0}
    Q = deque([S0])
    
    state_intervals = {}
    state_intervals[(tuple(sorted(M0.items())), 0, 'N')] = [(0.0, 0.0)]
    
    step = 0
    
    while Q:
        current = Q.popleft()
        step += 1
        
        print(f"步骤 {step}: 扩展节点")
        print(f"  当前节点: M={dict(current.marking)}, k={current.k}, [{current.tmin:.2f},{current.tmax:.2f}], δ={current.delta}")
        
        if current.k >= m:
            print(f"  → 已匹配完所有观测，停止扩展\n")
            continue
        
        # 获取使能变迁
        enabled = []
        for t in tpn.transitions:
            is_enabled = all(current.marking.get(p, 0) >= w for p, w in t.pre.items())
            if is_enabled:
                enabled.append(t)
        
        print(f"  使能变迁: {[t.id for t in enabled]}")
        
        for t in enabled:
            # 计算新标识
            M_prime = current.marking.copy()
            for p, w in t.pre.items():
                M_prime[p] = M_prime.get(p, 0) - w
            for p, w in t.post.items():
                M_prime[p] = M_prime.get(p, 0) + w
            
            # 计算新标签
            delta_prime = 'F' if (current.delta == 'F' or t in fault_set) else 'N'
            
            # 计算新的 k
            is_observable = (t.label is not None and t.label != '')
            
            if is_observable:
                if current.k < m and t.label == observation_prefix[current.k]:
                    k_prime = current.k + 1
                    print(f"    触发 {t.id} (观测 '{t.label}'): 匹配成功, k: {current.k} → {k_prime}")
                else:
                    print(f"    触发 {t.id} (观测 '{t.label}'): 不匹配 (期望 '{observation_prefix[current.k]}'), 跳过")
                    continue
            else:
                k_prime = current.k
                print(f"    触发 {t.id} (不可观测): k 保持 {k_prime}")
            
            # 计算新的时间区间
            tmin_prime = current.tmin + t.time_constraint.earliest
            tmax_prime = current.tmax + t.time_constraint.latest
            
            print(f"      → M'={dict(M_prime)}, k'={k_prime}, [{tmin_prime:.2f},{tmax_prime:.2f}], δ'={delta_prime}")
            
            # 状态去重
            state_key = (tuple(sorted(M_prime.items())), k_prime, delta_prime)
            
            if state_key in state_intervals:
                print(f"      → 状态已存在，合并时间区间")
                intervals = state_intervals[state_key]
                old_intervals = intervals.copy()
                intervals.append((tmin_prime, tmax_prime))
                
                all_tmin = min(iv[0] for iv in intervals)
                all_tmax = max(iv[1] for iv in intervals)
                
                print(f"         旧区间: {old_intervals}")
                print(f"         新区间: {intervals}")
                print(f"         合并后: [{all_tmin:.2f}, {all_tmax:.2f}]")
                
                # 更新现有节点
                for node in S:
                    if (tuple(sorted(node.marking.items())) == tuple(sorted(M_prime.items())) and
                        node.k == k_prime and
                        node.delta == delta_prime):
                        node.tmin = all_tmin
                        node.tmax = all_tmax
                        print(f"         更新节点: {node}")
                        break
            else:
                print(f"      → 新状态，添加到集合")
                new_node = ETERGNode(M_prime, k_prime, tmin_prime, tmax_prime, delta_prime)
                state_intervals[state_key] = [(tmin_prime, tmax_prime)]
                S.add(new_node)
                Q.append(new_node)
                print(f"         新节点: {new_node}")
        
        print()
    
    print(f"{'='*80}")
    print(f"构造完成")
    print(f"总节点数: {len(S)}")
    print(f"{'='*80}\n")
    
    # 显示所有节点
    print("所有节点:")
    for i, node in enumerate(sorted(S, key=lambda n: (n.k, n.delta, n.tmin)), 1):
        print(f"  {i}. M={dict(node.marking)}, k={node.k}, [{node.tmin:.2f},{node.tmax:.2f}], δ={node.delta}")
    
    return S


def main():
    # 加载 Example 1
    tpn = load_tpn_from_json("examples/example1.json")
    fault_transitions = [t for t in tpn.transitions if t.is_fault]
    
    print("TPN 信息:")
    print(f"  Places: {tpn.places}")
    print(f"  Transitions:")
    for t in tpn.transitions:
        print(f"    {t.id}: label='{t.label}', [{t.time_constraint.earliest},{t.time_constraint.latest}], fault={t.is_fault}")
    print(f"  Initial marking: {tpn.initial_marking}")
    
    # 调试 φ = 'ab'
    debug_peterg_construction(tpn, ('a', 'b'), fault_transitions)


if __name__ == '__main__':
    main()
