"""
测试修复后的 P-ETERG 算法
对比论文中的 Example 1 和 Example 2
"""
import json
import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from tpn.model import TPN, Place, Transition, TimeConstraint


def load_tpn_from_json(json_path):
    """从 JSON 文件加载 TPN"""
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # 创建 places (使用字符串 ID)
    places = data['places']
    place_ids = [p['id'] for p in places]
    
    # 创建 transitions
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
        
        # 设置前置和后置条件 (使用字符串 place ID)
        t.pre = {p: w for p, w in t_data['pre'].items()}
        t.post = {p: w for p, w in t_data['post'].items()}
        
        transitions.append(t)
    
    # 创建初始标识 (使用字符串 place ID)
    initial_marking = {p: w for p, w in data['initial_marking'].items()}
    
    # 创建 TPN
    tpn = TPN(
        places=place_ids,
        transitions=transitions,
        initial_marking=initial_marking
    )
    
    return tpn


def test_example(example_name, json_path, test_cases):
    """测试一个案例"""
    print(f"\n{'='*60}")
    print(f"测试 {example_name}")
    print(f"{'='*60}")
    
    # 加载 TPN
    tpn = load_tpn_from_json(json_path)
    
    # 获取故障变迁
    fault_transitions = [t for t in tpn.transitions if t.is_fault]
    
    print(f"\nTPN 信息:")
    print(f"  Places: {tpn.places}")
    print(f"  Transitions: {[t.id for t in tpn.transitions]}")
    print(f"  Observable labels: {set(t.label for t in tpn.transitions if t.label)}")
    print(f"  Fault transitions: {[t.id for t in fault_transitions]}")
    
    # 导入修复后的算法
    from algorithms.peterg_fixed import build_peterg
    
    # 测试每个观测前缀
    for prefix, expected_nodes, expected_diagnosable in test_cases:
        print(f"\n{'-'*60}")
        print(f"观测前缀: φ = {prefix}")
        print(f"论文预期: {expected_nodes} 个节点, {'可诊断' if expected_diagnosable else '不可诊断'}")
        
        # 构造 P-ETERG
        result = build_peterg(tpn, prefix, fault_transitions)
        
        # 统计结果
        actual_nodes = len(result.nodes)
        has_ambiguity = result.has_time_ambiguity()
        actual_diagnosable = not has_ambiguity
        
        print(f"实际结果: {actual_nodes} 个节点, {'可诊断' if actual_diagnosable else '不可诊断'}")
        
        # 显示终端节点的时间区间
        normal_intervals = result.get_normal_paths()
        fault_intervals = result.get_fault_paths()
        
        print(f"\n正常路径时间区间:")
        for i, (tmin, tmax) in enumerate(normal_intervals, 1):
            print(f"  路径 {i}: [{tmin:.2f}, {tmax:.2f}]")
        
        print(f"\n故障路径时间区间:")
        for i, (tmin, tmax) in enumerate(fault_intervals, 1):
            print(f"  路径 {i}: [{tmin:.2f}, {tmax:.2f}]")
        
        # 检查是否有重叠
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
        
        # 验证结果
        nodes_match = (actual_nodes == expected_nodes) if expected_nodes else True
        diagnosable_match = (actual_diagnosable == expected_diagnosable)
        
        if nodes_match and diagnosable_match:
            print(f"\n✅ 测试通过")
        else:
            print(f"\n❌ 测试失败:")
            if not nodes_match:
                print(f"   节点数不匹配: 预期 {expected_nodes}, 实际 {actual_nodes}")
            if not diagnosable_match:
                print(f"   可诊断性不匹配: 预期 {'可诊断' if expected_diagnosable else '不可诊断'}, 实际 {'可诊断' if actual_diagnosable else '不可诊断'}")


def main():
    """主测试函数"""
    print("P-ETERG 算法修复验证")
    print("对比论文 Example 1 和 Example 2")
    
    # Example 1 测试用例
    # 根据论文：
    # - φ = 'a': 3 个节点, 可诊断 (Normal [2,3] ∩ Fault [4,5] = ∅)
    # - φ = 'ab': 5 个节点, 不可诊断 (有时间重叠)
    example1_tests = [
        (('a',), 3, True),   # 可诊断
        (('a', 'b'), 5, False),  # 不可诊断
    ]
    
    test_example(
        "Example 1",
        "examples/example1.json",
        example1_tests
    )
    
    # Example 2 测试用例
    # 根据论文：
    # - φ = 'ab': 不可诊断
    # - φ = 'ac': 可诊断
    example2_tests = [
        (('a', 'b'), None, False),  # 不可诊断
        (('a', 'c'), None, True),   # 可诊断
    ]
    
    test_example(
        "Example 2",
        "examples/example2.json",
        example2_tests
    )
    
    print(f"\n{'='*60}")
    print("测试完成")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
