"""
数据可视化模块 - 使用 matplotlib 生成性能对比图表
"""
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import numpy as np
from typing import List, Dict, Any
from pathlib import Path
from .metrics import PerformanceMetrics


class PerformanceVisualizer:
    """性能数据可视化器"""
    
    def __init__(self, output_dir: str = "results/plots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置中文字体支持
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    
    def plot_comparison(self, metrics_list: List[PerformanceMetrics], title: str = "Performance Comparison"):
        """生成多个 TPN 的性能对比图表"""
        if not metrics_list:
            return
        
        # 创建子图
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        # 提取数据
        names = [m.tpn_name for m in metrics_list]
        
        # 1. 状态空间大小对比
        self._plot_state_space(axes[0, 0], metrics_list, names)
        
        # 2. 时间性能对比
        self._plot_time_performance(axes[0, 1], metrics_list, names)
        
        # 3. 可诊断性指标对比
        self._plot_diagnosability(axes[0, 2], metrics_list, names)
        
        # 4. P-ETERG 规模对比
        self._plot_peterg_scale(axes[1, 0], metrics_list, names)
        
        # 5. 增强效果对比
        self._plot_enhancement_effect(axes[1, 1], metrics_list, names)
        
        # 6. 总体性能对比
        self._plot_overall_performance(axes[1, 2], metrics_list, names)
        
        plt.tight_layout()
        output_path = self.output_dir / f"{title.replace(' ', '_')}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Performance comparison plot saved to: {output_path}")
    
    def _plot_state_space(self, ax, metrics_list, names):
        """绘制状态空间大小对比"""
        sync_states = [m.sync_states for m in metrics_list]
        peterg_nodes = [m.total_peterg_nodes for m in metrics_list]
        
        x = np.arange(len(names))
        width = 0.35
        
        ax.bar(x - width/2, sync_states, width, label='Sync States', alpha=0.8)
        ax.bar(x + width/2, peterg_nodes, width, label='P-ETERG Nodes', alpha=0.8)
        
        ax.set_xlabel('TPN Networks')
        ax.set_ylabel('Number of States')
        ax.set_title('State Space Size Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
    
    def _plot_time_performance(self, ax, metrics_list, names):
        """绘制时间性能对比"""
        sync_time = [m.sync_time for m in metrics_list]
        peterg_time = [m.peterg_construction_time for m in metrics_list]
        enhancement_time = [m.enhancement_time for m in metrics_list]
        
        x = np.arange(len(names))
        width = 0.25
        
        ax.bar(x - width, sync_time, width, label='Sync Construction', alpha=0.8)
        ax.bar(x, peterg_time, width, label='P-ETERG Construction', alpha=0.8)
        ax.bar(x + width, enhancement_time, width, label='Enhancement', alpha=0.8)
        
        ax.set_xlabel('TPN Networks')
        ax.set_ylabel('Time (seconds)')
        ax.set_title('Time Performance Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
    
    def _plot_diagnosability(self, ax, metrics_list, names):
        """绘制可诊断性指标对比"""
        ambiguous = [m.ambiguous_pairs for m in metrics_list]
        resolved = [m.resolved_pairs for m in metrics_list]
        unresolved = [m.unresolved_pairs for m in metrics_list]
        
        x = np.arange(len(names))
        width = 0.25
        
        ax.bar(x - width, ambiguous, width, label='Ambiguous Pairs', alpha=0.8, color='red')
        ax.bar(x, resolved, width, label='Resolved', alpha=0.8, color='green')
        ax.bar(x + width, unresolved, width, label='Unresolved', alpha=0.8, color='orange')
        
        ax.set_xlabel('TPN Networks')
        ax.set_ylabel('Number of Pairs')
        ax.set_title('Diagnosability Analysis')
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
    
    def _plot_peterg_scale(self, ax, metrics_list, names):
        """绘制 P-ETERG 规模对比"""
        peterg_count = [m.peterg_count for m in metrics_list]
        avg_nodes = [m.total_peterg_nodes / max(m.peterg_count, 1) for m in metrics_list]
        
        x = np.arange(len(names))
        
        ax2 = ax.twinx()
        
        bars = ax.bar(x, peterg_count, alpha=0.8, color='steelblue', label='P-ETERG Count')
        line = ax2.plot(x, avg_nodes, 'ro-', linewidth=2, markersize=8, label='Avg Nodes per P-ETERG')
        
        ax.set_xlabel('TPN Networks')
        ax.set_ylabel('Number of P-ETERGs', color='steelblue')
        ax2.set_ylabel('Average Nodes', color='red')
        ax.set_title('P-ETERG Scale Analysis')
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha='right')
        
        # 合并图例
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        ax.grid(axis='y', alpha=0.3)
    
    def _plot_enhancement_effect(self, ax, metrics_list, names):
        """绘制增强效果对比"""
        resolution_rate = [
            (m.resolved_pairs / max(m.ambiguous_pairs, 1)) * 100 
            for m in metrics_list
        ]
        adjustments = [m.adjustments_made for m in metrics_list]
        
        x = np.arange(len(names))
        
        ax2 = ax.twinx()
        
        bars = ax.bar(x, resolution_rate, alpha=0.8, color='green', label='Resolution Rate (%)')
        line = ax2.plot(x, adjustments, 'bo-', linewidth=2, markersize=8, label='Adjustments Made')
        
        ax.set_xlabel('TPN Networks')
        ax.set_ylabel('Resolution Rate (%)', color='green')
        ax2.set_ylabel('Number of Adjustments', color='blue')
        ax.set_title('Enhancement Effectiveness')
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha='right')
        ax.set_ylim([0, 105])
        
        # 合并图例
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        ax.grid(axis='y', alpha=0.3)
    
    def _plot_overall_performance(self, ax, metrics_list, names):
        """绘制总体性能对比"""
        total_time = [m.total_time for m in metrics_list]
        total_states = [m.total_states_explored for m in metrics_list]
        
        x = np.arange(len(names))
        
        ax2 = ax.twinx()
        
        bars = ax.bar(x, total_time, alpha=0.8, color='purple', label='Total Time (s)')
        line = ax2.plot(x, total_states, 'go-', linewidth=2, markersize=8, label='Total States Explored')
        
        ax.set_xlabel('TPN Networks')
        ax.set_ylabel('Total Time (seconds)', color='purple')
        ax2.set_ylabel('Total States', color='green')
        ax.set_title('Overall Performance')
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha='right')
        
        # 合并图例
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        ax.grid(axis='y', alpha=0.3)
    
    def plot_single_analysis(self, metrics: PerformanceMetrics):
        """为单个 TPN 生成详细分析图表"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f"Detailed Analysis: {metrics.tpn_name}", fontsize=16, fontweight='bold')
        
        # 1. 时间分布饼图
        self._plot_time_distribution(axes[0, 0], metrics)
        
        # 2. 状态空间分布
        self._plot_state_distribution(axes[0, 1], metrics)
        
        # 3. P-ETERG 详细信息
        self._plot_peterg_details(axes[1, 0], metrics)
        
        # 4. 增强结果
        self._plot_enhancement_results(axes[1, 1], metrics)
        
        plt.tight_layout()
        output_path = self.output_dir / f"{metrics.tpn_name}_detailed.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Detailed analysis plot saved to: {output_path}")
    
    def _plot_time_distribution(self, ax, metrics):
        """绘制时间分布饼图"""
        labels = ['Sync Construction', 'P-ETERG Construction', 'Enhancement', 'Other']
        sizes = [
            metrics.sync_time,
            metrics.peterg_construction_time,
            metrics.enhancement_time,
            max(0, metrics.total_time - metrics.sync_time - 
                metrics.peterg_construction_time - metrics.enhancement_time)
        ]
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
        
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.set_title('Time Distribution')
    
    def _plot_state_distribution(self, ax, metrics):
        """绘制状态空间分布"""
        categories = ['Sync States', 'P-ETERG Nodes', 'Total Explored']
        values = [metrics.sync_states, metrics.total_peterg_nodes, metrics.total_states_explored]
        
        ax.bar(categories, values, color=['steelblue', 'orange', 'green'], alpha=0.7)
        ax.set_ylabel('Number of States')
        ax.set_title('State Space Distribution')
        ax.grid(axis='y', alpha=0.3)
        
        # 添加数值标签
        for i, v in enumerate(values):
            ax.text(i, v, str(v), ha='center', va='bottom')
    
    def _plot_peterg_details(self, ax, metrics):
        """绘制 P-ETERG 详细信息"""
        if not metrics.peterg_details:
            ax.text(0.5, 0.5, 'No P-ETERG details available', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title('P-ETERG Details')
            return
        
        # 提取前 10 个 P-ETERG 的节点数
        details = metrics.peterg_details[:10]
        indices = [f"P{i+1}" for i in range(len(details))]
        nodes = [d.get('nodes', 0) for d in details]
        
        ax.bar(indices, nodes, color='coral', alpha=0.7)
        ax.set_xlabel('P-ETERG Index')
        ax.set_ylabel('Number of Nodes')
        ax.set_title('P-ETERG Node Distribution (Top 10)')
        ax.grid(axis='y', alpha=0.3)
    
    def _plot_enhancement_results(self, ax, metrics):
        """绘制增强结果"""
        categories = ['Ambiguous', 'Resolved', 'Unresolved']
        values = [metrics.ambiguous_pairs, metrics.resolved_pairs, metrics.unresolved_pairs]
        colors = ['red', 'green', 'orange']
        
        ax.bar(categories, values, color=colors, alpha=0.7)
        ax.set_ylabel('Number of Pairs')
        ax.set_title('Enhancement Results')
        ax.grid(axis='y', alpha=0.3)
        
        # 添加数值标签
        for i, v in enumerate(values):
            ax.text(i, v, str(v), ha='center', va='bottom')
