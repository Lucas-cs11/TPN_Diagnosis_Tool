"""
详细追踪 Example 2 φ='ac' 的路径构造
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from tpn.model import TPN, Transition, TimeConstraint
from algorithms.peterg_fixed import PETERGBuilder, ETERGNode
from collections import deque


def load_tpn(json_path):
    with open(json_path) as f:
        data = json.load(f)
    
    place_ids = [p['id'] for p in data['places']]
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
    
    return TPN(place_ids, transitions, initial_marking)


def trace_paths(tpn, observation_prefix, fault_transitions):
    """手动追踪所有可能的路径"""
    print(f"追踪观测前缀 φ = {observation_prefix} 的所有路径\n")
    
    m = len(observation_prefix)
    M0 = tpn.initial_marking
    fault_set = set(fault_transitions)
    
    # 使用 DFS 追踪所有路径
    # 状态: (marking, k, tmin, tmax, delta, path)
    stack = [(M0, 0, 0.0, 0.0, 'N', [])]
    complete_paths = []
    
    while stack:
        M, k, tmin, tmax, delta, path = stack.pop()
        
        if k == m:
            # 完整路径
            complete_paths.append((M, tmin, tmax, delta, path))
            continue
        
        # 获取使能变迁
        for t in tpn.transitions:
            is_enabled = all(M.get(p, 0) >= w for p, w in t.pre.items())
            if not is_enabled:
                continue
            
            # 计算新标识
            M_new = M.copy()
            for p, w in t.pre.items():
                M_new[p] = M_new.get(p, 0) - w
            for p, w in t.post.items():
                M_new[p] = M_new.get(p, 0) + w
            
            # 计算新标签
            delta_new = 'F' if (delta == 'F' or t in fault_set) else 'N'
            
            # 计算新的 k
            is_obs = (t.label is not None and t.label != '')
            
            if is_obs:
                if k < m and t.label == observation_prefix[k]:
                    k_new = k + 1
                else:
                    continue
            else:
                k_new = k
            
            # 计算新的时间
            tmin_new = tmin + t.time_constraint.earliest
            tmax_new = tmax + t.time_constraint.latest
            
            # 添加到栈
            new_path = path + [(t.id, t.label, t.time_constraint.earliest, t.time_constraint.latest, delta_new)]
            stack.append((M_new, k_new, tmin_new, tmax_new, delta_new, new_path))
    
    # 显示所有完整路径
    print(f"找到 {len(complete_paths)} 条完整路径:\n")
    
    normal_paths = [p for p in complete_paths if p[3] == 'N']
    fault_paths = [p for p in complete_paths if p[3] == 'F']
    
    print(f"正常路径 ({len(normal_paths)} 条):")
    for i, (M, tmin, tmax, delta, path) in enumerate(normal_paths, 1):
        print(f"\n  路径 {i}: [{tmin:.2f}, {tmax:.2f}]")
        for t_id, label, e, l, d in path:
            obs_str = f"观测='{label}'" if label else "不可观测"
            print(f"    → {t_id} ({obs_str}, [{e},{l}], δ={d})")
    
    print(f"\n故障路径 ({len(fault_paths)} 条):")
    for i, (M, tmin, tmax, delta, path) in enumerate(fault_paths, 1):
        print(f"\n  路径 {i}: [{tmin:.2f}, {tmax:.2f}]")
        for t_id, label, e, l, d in path:
            obs_str = f"观测='{label}'" if label else "不可观测"
            fault_mark = " ⚠️ FAULT" if label is None and d == 'F' else ""
            print(f"    → {t_id} ({obs_str}, [{e},{l}], δ={d}){fault_mark}")
    
    return normal_paths, fault_paths


def main():
    tpn = load_tpn("examples/example2.json")
    fault_transitions = [t for t in tpn.transitions if t.is_fault]
    
    print("="*80)
    print("Example 2 详细路径追踪")
    print("="*80)
    print()
    
    print("TPN 结构:")
    print(f"  Places: {tpn.places}")
    print(f"  Initial marking: {tpn.initial_marking}")
    print(f"\n  Transitions:")
    for t in tpn.transitions:
        fault_str = " (FAULT)" if t.is_fault else ""
        label_str = f"'{t.label}'" if t.label else "ε"
        print(f"    {t.id}: {label_str}, [{t.time_constraint.earliest},{t.time_constraint.latest}]{fault_str}")
        print(f"         pre={t.pre}, post={t.post}")
    print()
    
    # 追踪 φ='ac'
    print("="*80)
    normal, fault = trace_paths(tpn, ('a', 'c'), fault_transitions)
    print("="*80)
    
    # 检查重叠
    if normal and fault:
        print("\n时间区间重叠分析:")
        for n_M, n_min, n_max, n_d, n_path in normal:
            for f_M, f_min, f_max, f_d, f_path in fault:
                overlap_start = max(n_min, f_min)
                overlap_end = min(n_max, f_max)
                if overlap_start <= overlap_end:
                    print(f"  ⚠️  重叠: Normal [{n_min:.2f},{n_max:.2f}] ∩ Fault [{f_min:.2f},{f_max:.2f}] = [{overlap_start:.2f},{overlap_end:.2f}]")
                else:
                    print(f"  ✓  无重叠: Normal [{n_min:.2f},{n_max:.2f}] ∩ Fault [{f_min:.2f},{f_max:.2f}] = ∅")


if __name__ == '__main__':
    main()
