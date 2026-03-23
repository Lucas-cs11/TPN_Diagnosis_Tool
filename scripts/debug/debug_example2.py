"""
调试 Example 2 的 P-ETERG 构造
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from tpn.model import TPN, Transition, TimeConstraint
from algorithms.peterg_fixed import build_peterg


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


def main():
    # 加载 Example 2
    tpn = load_tpn_from_json("examples/example2.json")
    fault_transitions = [t for t in tpn.transitions if t.is_fault]
    
    print("Example 2 TPN 信息:")
    print(f"  Places: {tpn.places}")
    print(f"  Transitions:")
    for t in tpn.transitions:
        print(f"    {t.id}: label='{t.label}', [{t.time_constraint.earliest},{t.time_constraint.latest}], fault={t.is_fault}")
    print(f"  Initial marking: {tpn.initial_marking}")
    print(f"  Fault transitions: {[t.id for t in fault_transitions]}")
    
    # 测试 φ = 'ac' (应该可诊断)
    print(f"\n{'='*80}")
    print("测试 φ = ('a', 'c')")
    print(f"{'='*80}")
    
    result = build_peterg(tpn, ('a', 'c'), fault_transitions)
    
    print(f"\n节点数: {len(result.nodes)}")
    print(f"边数: {len(result.edges)}")
    
    # 显示所有终端节点
    terminal_nodes = result.get_terminal_nodes()
    print(f"\n终端节点 (k=2):")
    for node in terminal_nodes:
        print(f"  M={dict(node.marking)}, [{node.tmin:.2f},{node.tmax:.2f}], δ={node.delta}")
    
    # 显示正常和故障路径
    normal_intervals = result.get_normal_paths()
    fault_intervals = result.get_fault_paths()
    
    print(f"\n正常路径时间区间:")
    for i, (tmin, tmax) in enumerate(normal_intervals, 1):
        print(f"  路径 {i}: [{tmin:.2f}, {tmax:.2f}]")
    
    print(f"\n故障路径时间区间:")
    for i, (tmin, tmax) in enumerate(fault_intervals, 1):
        print(f"  路径 {i}: [{tmin:.2f}, {tmax:.2f}]")
    
    # 检查时间模糊性
    has_ambiguity = result.has_time_ambiguity()
    print(f"\n时间模糊性: {'存在' if has_ambiguity else '不存在'}")
    print(f"可诊断性: {'不可诊断' if has_ambiguity else '可诊断'}")
    
    # 检查重叠
    if normal_intervals and fault_intervals:
        print(f"\n时间区间重叠检查:")
        for n_min, n_max in normal_intervals:
            for f_min, f_max in fault_intervals:
                overlap_start = max(n_min, f_min)
                overlap_end = min(n_max, f_max)
                if overlap_start <= overlap_end:
                    print(f"  ⚠️  重叠: Normal [{n_min:.2f}, {n_max:.2f}] ∩ Fault [{f_min:.2f}, {f_max:.2f}] = [{overlap_start:.2f}, {overlap_end:.2f}]")
                else:
                    print(f"  ✓  无重叠: Normal [{n_min:.2f}, {n_max:.2f}] ∩ Fault [{f_min:.2f}, {f_max:.2f}] = ∅")


if __name__ == '__main__':
    main()
