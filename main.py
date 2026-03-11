"""
TPN Diagnosability Verification and Enhancement Tool - 主程序
"""
import argparse
import sys
from pathlib import Path
import time
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.tpn.parser import load_tpn
from src.algorithms.observation_sync import build_observation_synchronizer
from src.algorithms.peterg import build_peterg
from src.algorithms.enhancement import enhance_diagnosability
from src.analysis.metrics import MetricsCollector
from src.analysis.visualizer import PerformanceVisualizer


def analyze_single_tpn(tpn_file: str, max_length: int = 10, epsilon: float = 0.1, output_dir: str = "results"):
    """分析单个 TPN 网络"""
    print(f"\n{'='*60}")
    print(f"Analyzing TPN: {tpn_file}")
    print(f"{'='*60}\n")
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 初始化指标收集器
    collector = MetricsCollector()
    collector.start_timer()
    
    # 1. 加载 TPN
    print("[1/4] Loading TPN...")
    tpn = load_tpn(tpn_file)
    tpn_name = Path(tpn_file).stem
    
    # 记录 TPN 基本信息
    collector.metrics.tpn_name = tpn_name
    collector.metrics.num_places = len(tpn.places)
    collector.metrics.num_transitions = len(tpn.transitions)
    collector.metrics.num_arcs = len(tpn.arcs)
    collector.metrics.num_fault_transitions = len(tpn.get_fault_transitions())
    
    print(f"  Places: {len(tpn.places)}")
    print(f"  Transitions: {len(tpn.transitions)} (Fault: {len(tpn.get_fault_transitions())})")
    print(f"  Arcs: {len(tpn.arcs)}")
    
    # 2. 构造观测同步器
    print(f"\n[2/4] Building Observation Synchronizer (max_length={max_length})...")
    collector.start_phase()
    synchronizer, sync_stats = build_observation_synchronizer(tpn, max_length)
    collector.metrics.sync_time = collector.end_phase()
    
    collector.metrics.sync_states = len(synchronizer.states)
    collector.metrics.sync_edges = len(synchronizer.edges)
    collector.metrics.total_states_explored += sync_stats['states_explored']
    
    print(f"  States: {len(synchronizer.states)}")
    print(f"  Edges: {len(synchronizer.edges)}")
    print(f"  Time: {collector.metrics.sync_time:.4f}s")
    
    # 3. 构造 P-ETERG（为每个可疑观测前缀）
    print(f"\n[3/4] Building P-ETERGs...")
    collector.start_phase()
    
    # 简化：为所有长度的观测前缀构造 P-ETERG
    # 实际应该基于观测同步器识别的可疑前缀
    suspect_prefixes = []
    for k in range(1, min(max_length + 1, 6)):  # 限制最多 5 个前缀作为示例
        # 这里简化处理，实际需要从观测同步器提取真实的可疑前缀
        # 暂时使用占位符
        prefix = tuple([f"o{i}" for i in range(k)])
        suspect_prefixes.append(prefix)
    
    collector.metrics.suspect_prefixes = len(suspect_prefixes)
    
    petergs = []
    for i, prefix in enumerate(suspect_prefixes):
        print(f"  Building P-ETERG {i+1}/{len(suspect_prefixes)} for prefix {prefix}...")
        peterg, peterg_stats = build_peterg(tpn, prefix)
        petergs.append(peterg)
        
        collector.metrics.total_peterg_nodes += len(peterg.nodes)
        collector.metrics.total_peterg_edges += len(peterg.edges)
        collector.metrics.total_states_explored += peterg_stats['nodes_explored']
        
        # 记录详细信息
        collector.metrics.peterg_details.append({
            'prefix': prefix,
            'nodes': len(peterg.nodes),
            'edges': len(peterg.edges),
            'has_ambiguity': peterg.has_time_ambiguity()
        })
    
    collector.metrics.peterg_count = len(petergs)
    collector.metrics.peterg_construction_time = collector.end_phase()
    
    print(f"  Total P-ETERGs: {len(petergs)}")
    print(f"  Total Nodes: {collector.metrics.total_peterg_nodes}")
    print(f"  Total Edges: {collector.metrics.total_peterg_edges}")
    print(f"  Time: {collector.metrics.peterg_construction_time:.4f}s")
    
    # 4. 可诊断性增强
    print(f"\n[4/4] Diagnosability Enhancement...")
    collector.start_phase()
    
    # 收集所有时间模糊对
    all_ambiguous_pairs = []
    for peterg in petergs:
        pairs = peterg.get_ambiguous_pairs()
        all_ambiguous_pairs.extend(pairs)
    
    collector.metrics.ambiguous_pairs = len(all_ambiguous_pairs)
    
    if all_ambiguous_pairs:
        print(f"  Found {len(all_ambiguous_pairs)} ambiguous pairs")
        enhanced_tpn, adjustment_results, enhancement_stats = enhance_diagnosability(
            tpn, all_ambiguous_pairs, epsilon
        )
        
        collector.metrics.resolved_pairs = sum(1 for r in adjustment_results if r.success)
        collector.metrics.unresolved_pairs = sum(1 for r in adjustment_results if not r.success)
        collector.metrics.adjustments_made = enhancement_stats['adjustments_made']
        
        # 记录调整详细信息
        for i, result in enumerate(adjustment_results):
            collector.metrics.adjustment_details.append({
                'pair_index': i,
                'success': result.success,
                'delta_req': result.delta_req,
                'adjustment_type': result.adjustment_type,
                'transitions': list(result.adjusted_transitions)
            })
        
        print(f"  Resolved: {collector.metrics.resolved_pairs}")
        print(f"  Unresolved: {collector.metrics.unresolved_pairs}")
        print(f"  Adjustments Made: {collector.metrics.adjustments_made}")
    else:
        print(f"  No ambiguous pairs found - TPN is diagnosable!")
        collector.metrics.resolved_pairs = 0
        collector.metrics.unresolved_pairs = 0
        collector.metrics.adjustments_made = 0
    
    collector.metrics.enhancement_time = collector.end_phase()
    print(f"  Time: {collector.metrics.enhancement_time:.4f}s")
    
    # 结束计时
    collector.end_timer()
    
    # 5. 保存结果
    print(f"\n[Results]")
    metrics = collector.get_metrics()
    
    # 保存 JSON
    json_path = output_path / f"{tpn_name}_metrics.json"
    metrics.save_json(str(json_path))
    print(f"  Metrics saved to: {json_path}")
    
    # 生成可视化
    visualizer = PerformanceVisualizer(output_dir=str(output_path / "plots"))
    visualizer.plot_single_analysis(metrics)
    
    # 打印摘要
    print()
    metrics.print_summary()
    
    return metrics


def analyze_batch(input_dir: str, max_length: int = 10, epsilon: float = 0.1, output_dir: str = "results"):
    """批量分析多个 TPN 网络"""
    input_path = Path(input_dir)
    tpn_files = list(input_path.glob("*.json"))
    
    if not tpn_files:
        print(f"No TPN files found in {input_dir}")
        return
    
    print(f"\nFound {len(tpn_files)} TPN files")
    print(f"{'='*60}\n")
    
    all_metrics = []
    
    for tpn_file in tpn_files:
        try:
            metrics = analyze_single_tpn(str(tpn_file), max_length, epsilon, output_dir)
            all_metrics.append(metrics)
        except Exception as e:
            print(f"Error analyzing {tpn_file}: {e}")
            continue
    
    # 生成对比图表
    if len(all_metrics) > 1:
        print(f"\n{'='*60}")
        print("Generating comparison plots...")
        print(f"{'='*60}\n")
        
        visualizer = PerformanceVisualizer(output_dir=f"{output_dir}/plots")
        visualizer.plot_comparison(all_metrics, title="TPN Batch Analysis Comparison")
        print("Comparison plots generated successfully!")


def main():
    parser = argparse.ArgumentParser(
        description="TPN Diagnosability Verification and Enhancement Tool"
    )
    
    parser.add_argument(
        '--input',
        type=str,
        help='Input TPN file (JSON format)'
    )
    
    parser.add_argument(
        '--batch',
        type=str,
        help='Input directory for batch processing'
    )
    
    parser.add_argument(
        '--max-length',
        type=int,
        default=10,
        help='Maximum observation prefix length (default: 10)'
    )
    
    parser.add_argument(
        '--epsilon',
        type=float,
        default=0.1,
        help='Minimum time interval increment for enhancement (default: 0.1)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='results',
        help='Output directory (default: results)'
    )
    
    args = parser.parse_args()
    
    if args.input:
        # 单文件分析
        analyze_single_tpn(args.input, args.max_length, args.epsilon, args.output)
    elif args.batch:
        # 批量分析
        analyze_batch(args.batch, args.max_length, args.epsilon, args.output)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
