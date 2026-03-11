# TPN 可诊断性验证与增强工具 - 使用指南

## 项目概述

本工具基于论文 "Observation-Driven Diagnosability Verification and Enhancement for Time Petri Nets" 实现，提供完整的 TPN 故障诊断方法自动化执行。

## 核心功能

### 1. TPN 输入与解析
- 支持 JSON 格式定义 TPN 网络
- 包含库所、变迁、弧、时间约束等完整信息
- 区分正常/故障变迁、可观测/不可观测变迁
- 支持软/硬时间约束

### 2. 观测同步器构造（Algorithm 1）
- 基于 BFS 算法构造观测同步器
- 自动识别可疑观测前缀
- 记录状态空间探索数据

### 3. P-ETERG 构造（Algorithm 2）
- 为每个可疑观测前缀构造 P-ETERG
- 区分正常路径和故障路径
- 计算时间区间 [tmin, tmax]
- 检测时间模糊性

### 4. 可诊断性增强（Algorithm 3）
- 三阶段调整策略：
  1. 仅调整正常路径变迁
  2. 仅调整故障路径变迁
  3. 调整共享变迁
- 自动计算所需时间间隔增量
- 仅调整软时间约束

### 5. 性能分析与可视化
- 记录每步执行数据
- 生成多维度性能指标
- 自动生成对比图表

## 安装步骤

```bash
# 1. 进入项目目录
cd ~/Desktop/TPN_Diagnosability_Tool

# 2. 安装依赖
pip install -r requirements.txt

# 3. 验证安装
python main.py --help
```

## 使用方法

### 方式 1: 分析单个 TPN

```bash
python main.py --input examples/example1.json --max-length 10
```

**参数说明：**
- `--input`: TPN 文件路径
- `--max-length`: 最大观测前缀长度（默认 10）
- `--epsilon`: 时间间隔增量（默认 0.1）
- `--output`: 输出目录（默认 results）

**输出：**
- `results/example1_metrics.json`: 性能指标数据
- `results/plots/example1_detailed.png`: 详细分析图表
- 控制台输出：完整分析过程和结果摘要

### 方式 2: 批量分析

```bash
python main.py --batch examples/ --output batch_results/
```

**功能：**
- 自动处理目录下所有 `.json` 文件
- 为每个 TPN 生成独立的指标文件
- 生成性能对比图表
- 生成每个 TPN 的详细分析图表

**输出：**
- `batch_results/*_metrics.json`: 各个 TPN 的指标
- `batch_results/plots/TPN_Performance_Comparison.png`: 对比图表
- `batch_results/plots/*_detailed.png`: 各个 TPN 的详细图表

### 方式 3: 从已有结果生成图表

```bash
python main.py --visualize results/
```

**功能：**
- 读取目录下所有 `*_metrics.json` 文件
- 重新生成所有图表
- 适用于调整可视化参数后重新绘图

## TPN 输入格式

### 完整示例

```json
{
  "places": ["p1", "p2", "p3"],
  "transitions": [
    {
      "name": "t1",
      "type": "normal",
      "observable": true,
      "label": "a",
      "time_constraint": {
        "type": "soft",
        "earliest": 1,
        "latest": 3
      }
    },
    {
      "name": "t2",
      "type": "fault",
      "observable": false,
      "label": "epsilon",
      "time_constraint": {
        "type": "hard",
        "earliest": 0,
        "latest": 2
      }
    }
  ],
  "arcs": [
    {"from": "p1", "to": "t1"},
    {"from": "t1", "to": "p2"},
    {"from": "p2", "to": "t2"},
    {"from": "t2", "to": "p3"}
  ],
  "initial_marking": {
    "p1": 1,
    "p2": 0,
    "p3": 0
  }
}
```

### 字段说明

**places**: 库所列表
- 字符串数组，每个元素是库所名称

**transitions**: 变迁列表
- `name`: 变迁名称（唯一标识）
- `type`: 变迁类型
  - `"normal"`: 正常变迁
  - `"fault"`: 故障变迁
- `observable`: 是否可观测
  - `true`: 可观测
  - `false`: 不可观测
- `label`: 观测标签
  - 可观测变迁：使用实际标签（如 "a", "b"）
  - 不可观测变迁：使用 "epsilon"
- `time_constraint`: 时间约束
  - `type`: 约束类型
    - `"soft"`: 软约束（可调整）
    - `"hard"`: 硬约束（不可调整）
  - `earliest`: 最早触发时间
  - `latest`: 最晚触发时间

**arcs**: 弧列表
- `from`: 源节点（库所或变迁名称）
- `to`: 目标节点（库所或变迁名称）
- `weight`: 弧权重（可选，默认 1）

**initial_marking**: 初始标识
- 键值对，键为库所名称，值为 token 数量

## 输出指标说明

### TPN 基本信息
- `places`: 库所数量
- `transitions`: 变迁数量
- `arcs`: 弧数量
- `fault_transitions`: 故障变迁数量

### 观测同步器指标
- `states`: 状态数量
- `edges`: 边数量
- `suspect_prefixes`: 可疑观测前缀数量
- `time`: 构造时间（秒）

### P-ETERG 指标
- `count`: P-ETERG 数量
- `total_nodes`: 总节点数
- `total_edges`: 总边数
- `construction_time`: 构造时间（秒）
- `details`: 每个 P-ETERG 的详细信息

### 可诊断性指标
- `ambiguous_pairs`: 时间模糊对数量
- `resolved_pairs`: 成功解决的模糊对数量
- `unresolved_pairs`: 无���解决的模糊对数量
- `adjustments_made`: 执行的调整次数
- `enhancement_time`: 增强时间（秒）

### 总体性能
- `total_time`: 总执行时间（秒）
- `total_states_explored`: 探索的状态总数

## 可视化图表说明

### 对比图表（6 个子图）

1. **State Space Size Comparison**
   - 观测同步器状态数 vs P-ETERG 节点数
   - 反映状态空间规模

2. **Time Performance Comparison**
   - 各阶段耗时对比
   - 识别性能瓶颈

3. **Diagnosability Analysis**
   - 模糊对、已解决、未解决数量
   - 评估可诊断性

4. **P-ETERG Scale Analysis**
   - P-ETERG 数量和平均节点数
   - 分析复杂度

5. **Enhancement Effectiveness**
   - 解决率和调整次数
   - 评估增强效果

6. **Overall Performance**
   - 总时间和总状态数
   - 整体性能评估

### 详细分析图表（4 个子图）

1. **Time Distribution**
   - 各阶段时间占比饼图

2. **State Space Distribution**
   - 不同类型状态数量柱状图

3. **P-ETERG Details**
   - 前 10 个 P-ETERG 的节点分布

4. **Enhancement Results**
   - 增强结果柱状图

## 实验建议

### 1. 参数调优

**max-length（最大观测前缀长度）**
- 较小值（5-10）：快速测试，适合初步验证
- 中等值（10-20）：平衡性能和完整性
- 较大值（>20）：完整分析，但可能耗时较长

**epsilon（时间间隔增量）**
- 较小值（0.01-0.1）：精细调整，但可能需要更多调整
- 中等值（0.1-0.5）：平衡精度和效率
- 较大值（>0.5）：快速解决，但可能过度调整

### 2. 性能测试

创建不同规模的 TPN 进行对比：
- 小规模：3-5 个库所，5-8 个变迁
- 中规模：5-10 个库所，10-15 个变迁
- 大规模：>10 个库所，>15 个变迁

### 3. 可诊断性研究

- 变化故障变迁数量
- 调整可观测变迁比例
- 修改时间约束范围
- 对比软/硬约束影响

## 常见问题

### Q1: 程序运行很慢怎么办？
A: 
- 减小 `--max-length` 参数
- 简化 TPN 网络结构
- 减少可疑观测前缀数量

### Q2: 无法解决所有模糊对？
A:
- 检查是否有足够的软时间约束
- 增大 `--epsilon` 参数
- 手动调整 TPN 结构

### Q3: 图表显示不正常？
A:
- 确保安装了 matplotlib
- 检查中文字体支持
- 使用 `--visualize` 重新生成

### Q4: 如何扩展功能？
A:
- 修改 `src/algorithms/` 中的算法实现
- 在 `src/analysis/` 中添加新的指标
- 在 `src/analysis/visualizer.py` 中添加新图表

## 下一步开发

当前实现的简化之处：

1. **路径回溯**：P-ETERG 中需要完整记录路径信息
2. **可疑前缀识别**：需要更精确的算法
3. **时间约束调整**：可以实现更智能的调整策略
4. **并行处理**：批量分析可以并行化
5. **增量构造**：避免重复计算

## 联系方式

如有问题或建议，请联系开发者。
