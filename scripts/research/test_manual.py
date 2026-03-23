#!/usr/bin/env python3
"""
手动测试脚本 - 使用真实观测前缀验证算法
"""
import json
import sys
from src.tpn.parser import load_tpn
from src.algorithms.peterg import build_peterg
from src.algorithms.observation_sync import build_observation_synchronizer


def load_tpn_model(filepath):
    """加载 TPN 模型"""
    return load_tpn(filepath)


def extract_observable_labels(tpn):
    """提取所有可观测变迁的标签"""
    labels = set()
    for t in tpn.transitions:
        if t.is_observable():
            labels.add(t.label)
    return sorted(labels)


def test_example(filepath, test_prefixes):
    """测试指定的观测前缀"""
    print(f"\n{'='*60}")
    print(f"Testing: {filepath}")
    print(f"{'='*60}\n")
    
    # 加载模型
    tpn = load_tpn_model(filepath)
    print(f"TPN Model:")
    print(f"  Places: {len(tpn.places)}")
    print(f"  Transitions: {len(tpn.transitions)}")
    print(f"  Observable labels: {extract_observable_labels(tpn)}")
    print(f"  Initial marking: {tpn.initial_marking}")
    
    # 测试每个观测前缀
    for i, prefix in enumerate(test_prefixes):
        print(f"\n{'-'*60}")
        print(f"Test {i+1}: Observation prefix = {prefix}")
        print(f"{'-'*60}")
        
        # 构造 P-ETERG
        peterg, stats = build_peterg(tpn, prefix)
        
        print(f"\nP-ETERG Statistics:")
        print(f"  Nodes: {len(peterg.nodes)}")
        print(f"  Edges: {len(peterg.edges)}")
        print(f"  Nodes explored: {stats['nodes_explored']}")
        
        # 分析终止节点
        terminal_nodes = peterg.get_terminal_nodes()
        normal_nodes = peterg.get_normal_terminal_nodes()
        fault_nodes = peterg.get_fault_terminal_nodes()
        
        print(f"\nTerminal Nodes:")
        print(f"  Total: {len(terminal_nodes)}")
        print(f"  Normal (N): {len(normal_nodes)}")
        print(f"  Fault (F): {len(fault_nodes)}")
        
        if normal_nodes:
            print(f"\n  Normal terminal nodes:")
            for node in sorted(normal_nodes, key=lambda n: (n.tmin, n.tmax)):
                print(f"    {node}")
        
        if fault_nodes:
            print(f"\n  Fault terminal nodes:")
            for node in sorted(fault_nodes, key=lambda n: (n.tmin, n.tmax)):
                print(f"    {node}")
        
        # 检查时间模糊性
        has_ambiguity = peterg.has_time_ambiguity()
        print(f"\nTime Ambiguity: {'YES ❌' if has_ambiguity else 'NO ✅'}")
        
        if has_ambiguity:
            pairs = peterg.get_ambiguous_pairs()
            print(f"  Ambiguous pairs: {len(pairs)}")
            for n_node, f_node in pairs:
                print(f"    Normal: [{n_node.tmin:.2f}, {n_node.tmax:.2f}]")
                print(f"    Fault:  [{f_node.tmin:.2f}, {f_node.tmax:.2f}]")
                print(f"    Overlap: [{max(n_node.tmin, f_node.tmin):.2f}, {min(n_node.tmax, f_node.tmax):.2f}]")
                print()


def main():
    # Example 1 测试用例
    # 论文预期结果：
    # - 'a': 3 个节点，不可诊断
    # - 'ab': 5 个节点，不可诊断
    example1_prefixes = [
        ('a',),           # 预期: 3 nodes, 不可诊断
        ('a', 'b'),       # 预期: 5 nodes, 不可诊断
    ]
    
    # Example 2 测试用例
    # 论文预期结果：
    # - 'ab': 不可诊断
    # - 'ac': 可诊断
    # - 其他: 'abc', 'aca', 'acb', 'abcc', 'acab', 'acbb', 'abccd', 'acabd', 'acbbd'
    example2_prefixes = [
        ('a', 'b'),       # 预期: 不可诊断
        ('a', 'c'),       # 预期: 可诊断
        ('a', 'b', 'c'),
        ('a', 'c', 'a'),
        ('a', 'c', 'b'),
        ('a', 'b', 'c', 'c'),
        ('a', 'c', 'a', 'b'),
        ('a', 'c', 'b', 'b'),
        ('a', 'b', 'c', 'c', 'd'),
        ('a', 'c', 'a', 'b', 'd'),
        ('a', 'c', 'b', 'b', 'd'),
    ]
    
    # 测试 Example 1
    try:
        test_example('examples/example1.json', example1_prefixes)
    except Exception as e:
        print(f"\n❌ Example 1 failed: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试 Example 2
    try:
        test_example('examples/example2.json', example2_prefixes)
    except Exception as e:
        print(f"\n❌ Example 2 failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
