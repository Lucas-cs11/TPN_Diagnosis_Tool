# TPN 可诊断性验证与增强工具 - 用户手册

**版本**: 1.0  
**日期**: 2026-03-11  
**作者**: Based on "Observation-Driven Diagnosability Verification and Enhancement for Time Petri Nets"

---

## 目录

1. [简介](#1-简介)
2. [系统要求](#2-系统要求)
3. [安装指南](#3-安装指南)
4. [快速开始](#4-快速开始)
5. [输入格式详解](#5-输入格式详解)
6. [命令行参数](#6-命令行参数)
7. [输出结果说明](#7-输出结果说明)
8. [算法原理](#8-算法原理)
9. [使用示例](#9-使用示例)
10. [常见问题](#10-常见问题)
11. [性能优化建议](#11-性能优化建议)
12. [故障排除](#12-故障排除)

---

## 1. 简介

### 1.1 工具概述

本工具实现了基于时间 Petri 网（Time Petri Nets, TPN）的故障可诊断性验证与增强算法。主要功能包括：

- **可诊断性验证**：检测 TPN 网络是否满足可诊断性要求
- **时间模糊性识别**：识别导致诊断歧义的时间区间重叠
- **自动增强**：通过调整时间约束来提高可诊断性
- **性能分析**：详细的性能指标收集和可视化

### 1.2 核心特性

✅ **三个核心算法**
- Algorithm 1: 观测同步器构造
- Algorithm 2: P-ETERG（部分极值时间扩展可达图）构造
- Algorithm 3: 可诊断性增强

✅ **完整的工作流程**
- TPN 网络解析
- 状态空间探索
- 时间模糊性检测
- 自动增强建议

✅ **丰富的输出**
- JSON 格式性能指标
- 6 种可视化图表
- 详细的控制台报告

### 1.3 适用场景

- 离散事件系统故障诊断研究
- TPN 网络可诊断性分析
- 时间约束优化
- 学术论文实验验证

---

## 2. 系统要求

### 2.1 硬件要求

- **最低配置**：
  - CPU: 双核 1.5GHz
  - 内存: 2GB RAM
  - 存储: 100MB 可用空间

- **推荐配置**：
  - CPU: 四核 2.0GHz 或更高
  - 内存: 4GB RAM 或更多
  - 存储: 500MB 可用空间

### 2.2 软件要求

- **操作系统**：
  - macOS 10.14 或更高
  - Linux (Ubuntu 18.04+, CentOS 7+)
  - Windows 10/11 (需要 Python 环境)

- **Python 环境**：
  - Python 3.7 或更高版本
  - pip 包管理器

- **依赖库**：
  - matplotlib >= 3.5.0
  - numpy >= 1.21.0

---

## 3. 安装指南

### 3.1 获取工具

工具位于：`~/Desktop/TPN_Diagnosability_Tool/`

### 3.2 安装依赖

```bash
cd ~/Desktop/TPN_Diagnosability_Tool
pip3 install -r requirements.txt
```

### 3.3 验证安装

```bash
python3 main.py --help
```

如果看到帮助信息，说明安装成功。

### 3.4 运行测试

```bash
./test.sh
```

或手动运行：

```bash
python3 -m unittest discover tests/ -v
```

---

## 4. 快速开始

### 4.1 分析单个 TPN 网络

```bash
python3 main.py --input examples/example1.json --max-length 10
```

### 4.2 批量分析

```bash
python3 main.py --batch examples/ --output results/
```

### 4.3 查看结果

- **性能指标**：`results/<tpn_name>_metrics.json`
- **可视化图表**：`results/plots/`
- **控制台输出**：实时显示分析进度

---

## 5. 输入格式详解

### 5.1 JSON 文件结构

TPN 网络使用 JSON 格式定义，包含四个主要部分：

```json
{
  "places": [...],
  "transitions": [...],
  "arcs": [...],
  "initial_marking": {...}
}
```

### 5.2 库所（Places）

库所是 TPN 的基本组成部分，用字符串数组表示：

```json
"places": ["p1", "p2", "p3", "p4"]
```

**说明**：
- 每个库所有唯一的名称
- 名称可以是任意字符串（建议使用 p1, p2, ... 的命名规范）

### 5.3 变迁（Transitions）

变迁定义了 TPN 的动态行为：

```json
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
  }
]
```

**字段说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | 变迁唯一标识符 |
| `type` | string | ✅ | 变迁类型：`"normal"` 或 `"fault"` |
| `observable` | boolean | ✅ | 是否可观测 |
| `label` | string | ✅ | 观测标签（不可观测变迁使用 `"epsilon"`） |
| `time_constraint` | object | ✅ | 时间约束对象 |

**时间约束字段**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | string | ✅ | 约束类型：`"soft"` 或 `"hard"` |
| `earliest` | number | ✅ | 最早触发时间（≥ 0） |
| `latest` | number | ✅ | 最晚触发时间（≥ earliest） |

**约束类型说明**：
- **soft（软约束）**：可以被增强算法调整
- **hard（硬约束）**：不能被调整，保持固定

### 5.4 弧（Arcs）

弧连接库所和变迁：

```json
"arcs": [
  {"from": "p1", "to": "t1"},
  {"from": "t1", "to": "p2"},
  {"from": "p2", "to": "t2", "weight": 2}
]
```

**字段说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `from` | string | ✅ | 源节点名称（库所或变迁） |
| `to` | string | ✅ | 目标节点名称（库所或变迁） |
| `weight` | number | ❌ | 弧权重（默认 1） |

**弧的方向**：
- 库所 → 变迁：输入弧（Pre）
- 变迁 → 库所：输出弧（Post）

### 5.5 初始标识（Initial Marking）

定义初始状态下各库所的 token 数量：

```json
"initial_marking": {
  "p1": 1,
  "p2": 0,
  "p3": 0
}
```

**说明**：
- 键：库所名称
- 值：token 数量（非负整数）
- 未列出的库所默认为 0

### 5.6 完整示例

```json
{
  "places": ["p1", "p2", "p3", "p4", "p5"],
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
    },
    {
      "name": "t3",
      "type": "normal",
      "observable": true,
      "label": "b",
      "time_constraint": {
        "type": "soft",
        "earliest": 2,
        "latest": 4
      }
    }
  ],
  "arcs": [
    {"from": "p1", "to": "t1"},
    {"from": "t1", "to": "p2"},
    {"from": "p2", "to": "t2"},
    {"from": "p2", "to": "t3"},
    {"from": "t2", "to": "p3"},
    {"from": "t3", "to": "p4"}
  ],
  "initial_marking": {
    "p1": 1,
    "p2": 0,
    "p3": 0,
    "p4": 0,
    "p5": 0
  }
}
```

---


## 6. 命令行参数

### 6.1 基本语法

```bash
python3 main.py [OPTIONS]
```

### 6.2 参数列表

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--input` | string | ❌ | - | 单个 TPN 输入文件路径 |
| `--batch` | string | ❌ | - | 批量分析的目录路径 |
| `--max-length` | int | ❌ | 10 | 最大观测前缀长度 |
| `--epsilon` | float | ❌ | 0.1 | 时间间隔增量 |
| `--output` | string | ❌ | results | 输出目录路径 |

**注意**：`--input` 和 `--batch` 必须指定其中一个。

### 6.3 参数详解

#### 6.3.1 --input

指定单个 TPN 网络文件进行分析。

```bash
python3 main.py --input examples/example1.json
```

#### 6.3.2 --batch

指定包含多个 TPN 文件的目录进行批量分析。

```bash
python3 main.py --batch examples/
```

程序会自动查找目录中所有 `.json` 文件并逐个分析。

#### 6.3.3 --max-length

设置观测同步器构造的最大观测前缀长度。

```bash
python3 main.py --input example.json --max-length 15
```

**影响**：
- 值越大，探索的状态空间越大
- 分析更全面，但耗时更长
- 建议范围：5-20

#### 6.3.4 --epsilon

设置可诊断性增强时的最小时间间隔增量。

```bash
python3 main.py --input example.json --epsilon 0.5
```

**影响**：
- 值越大，时间约束调整幅度越大
- 更容易解决时间模糊性，但可能过度调整
- 建议范围：0.1-1.0

#### 6.3.5 --output

指定输出目录。

```bash
python3 main.py --input example.json --output my_results/
```

输出目录结构：
```
my_results/
├── <tpn_name>_metrics.json
└── plots/
    ├── <tpn_name>_detailed.png
    └── TPN_Batch_Analysis_Comparison.png (批量分析时)
```

### 6.4 使用示例

#### 示例 1：基本分析

```bash
python3 main.py --input examples/example1.json
```

#### 示例 2：自定义参数

```bash
python3 main.py \
  --input examples/example1.json \
  --max-length 15 \
  --epsilon 0.2 \
  --output results/custom/
```

#### 示例 3：批量分析

```bash
python3 main.py \
  --batch examples/ \
  --max-length 10 \
  --output results/batch_analysis/
```

---

## 7. 输出结果说明

### 7.1 输出文件结构

```
results/
├── example1_metrics.json          # 性能指标 JSON
├── example2_metrics.json
└── plots/                         # 可视化图表目录
    ├── example1_detailed.png      # 单个 TPN 详细分析
    ├── example2_detailed.png
    └── TPN_Batch_Analysis_Comparison.png  # 批量对比图
```

### 7.2 性能指标 JSON

#### 7.2.1 文件结构

```json
{
  "tpn_info": {...},
  "observation_synchronizer": {...},
  "peterg": {...},
  "diagnosability": {...},
  "overall": {...}
}
```

#### 7.2.2 TPN 信息

```json
"tpn_info": {
  "name": "example1",
  "places": 5,
  "transitions": 5,
  "arcs": 10,
  "fault_transitions": 1
}
```

#### 7.2.3 观测同步器统计

```json
"observation_synchronizer": {
  "states": 12,
  "edges": 15,
  "time": 0.0234,
  "suspect_prefixes": 3
}
```

**字段说明**：
- `states`: 观测同步器状态数量
- `edges`: 边的数量
- `time`: 构造耗时（秒）
- `suspect_prefixes`: 可疑观测前缀数量

#### 7.2.4 P-ETERG 统计

```json
"peterg": {
  "count": 3,
  "total_nodes": 28,
  "total_edges": 35,
  "construction_time": 0.0456,
  "details": [...]
}
```

**字段说明**：
- `count`: P-ETERG 数量
- `total_nodes`: 所有 P-ETERG 的节点总数
- `total_edges`: 所有 P-ETERG 的边总数
- `construction_time`: 构造耗时（秒）
- `details`: 每个 P-ETERG 的详细信息

#### 7.2.5 可诊断性分析

```json
"diagnosability": {
  "ambiguous_pairs": 2,
  "resolved_pairs": 2,
  "unresolved_pairs": 0,
  "adjustments_made": 2,
  "enhancement_time": 0.0123,
  "details": [...]
}
```

**字段说明**：
- `ambiguous_pairs`: 时间模糊对数量
- `resolved_pairs`: 成功解决的模糊对数量
- `unresolved_pairs`: 无法解决的模糊对数量
- `adjustments_made`: 时间约束调整次数
- `enhancement_time`: 增强耗时（秒）

**可诊断性判断**：
- `ambiguous_pairs = 0`: TPN 是可诊断的 ✅
- `resolved_pairs = ambiguous_pairs`: 通过增强实现可诊断 ✅
- `unresolved_pairs > 0`: 存在无法解决的模糊性 ⚠️

#### 7.2.6 总体性能

```json
"overall": {
  "total_time": 0.0813,
  "total_states_explored": 40
}
```

### 7.3 可视化图表

#### 7.3.1 单个 TPN 详细分析图

文件名：`<tpn_name>_detailed.png`

包含 4 个子图：
1. **时间分布饼图**：各阶段耗时占比
2. **状态空间分布**：不同类型状态数量
3. **P-ETERG 详细信息**：各 P-ETERG 节点数
4. **增强结果**：模糊对解决情况

#### 7.3.2 批量分析对比图

文件名：`TPN_Batch_Analysis_Comparison.png`

包含 6 个子图：
1. **状态空间大小对比**：观测同步器 vs P-ETERG
2. **时间性能对比**：各阶段耗时
3. **可诊断性指标对比**：模糊对数量
4. **P-ETERG 规模对比**：数量和平均节点数
5. **增强效果对比**：解决率和调整次数
6. **总体性能对比**：总耗时和状态数

### 7.4 控制台输出

#### 7.4.1 实时进度

```
============================================================
Analyzing TPN: examples/example1.json
============================================================

[1/4] Loading TPN...
  Places: 5
  Transitions: 5 (Fault: 1)
  Arcs: 10

[2/4] Building Observation Synchronizer (max_length=10)...
  States: 12
  Edges: 15
  Time: 0.0234s

[3/4] Building P-ETERGs...
  Building P-ETERG 1/3 for prefix ('o0',)...
  Building P-ETERG 2/3 for prefix ('o0', 'o1')...
  Building P-ETERG 3/3 for prefix ('o0', 'o1', 'o2')...
  Total P-ETERGs: 3
  Total Nodes: 28
  Total Edges: 35
  Time: 0.0456s

[4/4] Diagnosability Enhancement...
  Found 2 ambiguous pairs
  Resolved: 2
  Unresolved: 0
  Adjustments Made: 2
  Time: 0.0123s

[Results]
  Metrics saved to: results/example1_metrics.json
```

#### 7.4.2 性能摘要

```
============================================================
TPN Diagnosability Analysis Results: example1
============================================================

[TPN Information]
  Places: 5
  Transitions: 5 (Fault: 1)
  Arcs: 10

[Observation Synchronizer]
  States: 12
  Edges: 15
  Suspect Prefixes: 3
  Construction Time: 0.0234s

[P-ETERG Construction]
  Number of P-ETERGs: 3
  Total Nodes: 28
  Total Edges: 35
  Construction Time: 0.0456s

[Diagnosability Enhancement]
  Ambiguous Pairs: 2
  Resolved: 2
  Unresolved: 0
  Adjustments Made: 2
  Enhancement Time: 0.0123s

[Overall Performance]
  Total States Explored: 40
  Total Time: 0.0813s
============================================================
```

---

## 8. 算法原理

### 8.1 Algorithm 1: 观测同步器构造

**目的**：识别可疑观测前缀

**方法**：
1. 从初始标识开始 BFS 探索
2. 记录每个状态的观测前缀长度
3. 识别具有相同观测但不同标识的状态

**输出**：观测同步器 M_syn = (S, E, S0)

### 8.2 Algorithm 2: P-ETERG 构造

**目的**：为每个可疑观测前缀构造时间扩展可达图

**方法**：
1. 分别构造正常路径和故障路径
2. 计算每个节点的时间区间 [tmin, tmax]
3. 仅展开与观测前缀匹配的路径

**输出**：P-ETERG = (S, E, S0)，包含时间信息

### 8.3 Algorithm 3: 可诊断性增强

**目的**：通过调整时间约束消除时间模糊性

**三阶段策略**：
1. 仅调整正常路径独占变迁
2. 仅调整故障路径独占变迁
3. 调整共享变迁

**优先级**：软约束 > 硬约束

---

## 9. 使用示例

### 9.1 创建自己的 TPN 网络

#### 步骤 1：定义网络结构

假设要建模一个简单的生产系统：
- 正常流程：start → process → end
- 故障流程：start → fault → process → end

#### 步骤 2：编写 JSON 文件

```json
{
  "places": ["idle", "processing", "done"],
  "transitions": [
    {
      "name": "start",
      "type": "normal",
      "observable": true,
      "label": "start_event",
      "time_constraint": {
        "type": "soft",
        "earliest": 0,
        "latest": 1
      }
    },
    {
      "name": "fault",
      "type": "fault",
      "observable": false,
      "label": "epsilon",
      "time_constraint": {
        "type": "hard",
        "earliest": 1,
        "latest": 2
      }
    },
    {
      "name": "process",
      "type": "normal",
      "observable": true,
      "label": "process_event",
      "time_constraint": {
        "type": "soft",
        "earliest": 3,
        "latest": 5
      }
    },
    {
      "name": "end",
      "type": "normal",
      "observable": true,
      "label": "end_event",
      "time_constraint": {
        "type": "hard",
        "earliest": 1,
        "latest": 2
      }
    }
  ],
  "arcs": [
    {"from": "idle", "to": "start"},
    {"from": "start", "to": "processing"},
    {"from": "processing", "to": "fault"},
    {"from": "fault", "to": "processing"},
    {"from": "processing", "to": "process"},
    {"from": "process", "to": "done"},
    {"from": "done", "to": "end"}
  ],
  "initial_marking": {
    "idle": 1,
    "processing": 0,
    "done": 0
  }
}
```

#### 步骤 3：保存并分析

```bash
# 保存为 my_system.json
python3 main.py --input my_system.json --max-length 10
```

### 9.2 批量分析多个网络

#### 步骤 1：准备多个 TPN 文件

```
my_tpns/
├── system1.json
├── system2.json
└── system3.json
```

#### 步骤 2：运行批量分析

```bash
python3 main.py --batch my_tpns/ --output results/comparison/
```

#### 步骤 3：查看对比结果

```bash
open results/comparison/plots/TPN_Batch_Analysis_Comparison.png
```

### 9.3 调整参数优化性能

#### 场景 1：网络规模较大

```bash
# 减小 max-length 以加快分析
python3 main.py --input large_system.json --max-length 5
```

#### 场景 2：需要更精细的增强

```bash
# 减小 epsilon 以获得更精细的调整
python3 main.py --input system.json --epsilon 0.05
```

#### 场景 3：需要更全面的分析

```bash
# 增大 max-length 以探索更深的状态空间
python3 main.py --input system.json --max-length 20
```

---

## 10. 常见问题

### Q1: 如何判断我的 TPN 是否可诊断？

**A**: 查看输出的 `ambiguous_pairs` 指标：
- `ambiguous_pairs = 0`: 可诊断 ✅
- `ambiguous_pairs > 0 且 resolved_pairs = ambiguous_pairs`: 通过增强可诊断 ✅
- `unresolved_pairs > 0`: 不可诊断 ⚠️

### Q2: 程序运行很慢怎么办？

**A**: 尝试以下方法：
1. 减小 `--max-length` 参数（如从 10 降到 5）
2. 简化 TPN 网络结构
3. 减少变迁数量
4. 使用更快的硬件

### Q3: 如何解读时间约束调整结果？

**A**: 查看 `diagnosability.details` 中的调整信息：
- `adjustment_type = "normal_only"`: 仅调整了正常路径
- `adjustment_type = "fault_only"`: 仅调整了故障路径
- `adjustment_type = "shared"`: 调整了共享变迁
- `adjustment_type = "failed"`: 无法通过时间调整解决

### Q4: 为什么有些模糊对无法解决？

**A**: 可能的原因：
1. 所有相关变迁都是硬约束（不可调整）
2. 时间重叠太严重，需要禁用某些事件
3. 网络结构本身存在逻辑问题

### Q5: 如何导出增强后的 TPN？

**A**: 当前版本暂不支持自动导出。建议：
1. 查看 `adjustment_details` 了解哪些变迁被调整
2. 手动修改原始 JSON 文件中的时间约束
3. 重新运行验证

### Q6: 可以分析非时间 Petri 网吗？

**A**: 不可以。本工具专门针对时间 Petri 网（TPN）设计。如果要分析普通 Petri 网，需要为所有变迁添加时间约束（可以设置为 [0, ∞]）。

### Q7: 如何解释 P-ETERG 节点数？

**A**: 
- 节点数越多，状态空间越大
- 与观测前缀长度和网络复杂度相关
- 相比传统 SCG 方法，P-ETERG 通常节点数更少

### Q8: 批量分析时如何选择合适的参数？

**A**: 建议：
1. 先用默认参数（max-length=10）试运行
2. 根据耗时和结果质量调整
3. 对所有网络使用相同参数以便对比

---

## 11. 性能优化建议

### 11.1 参数调优

| 场景 | max-length | epsilon | 说明 |
|------|------------|---------|------|
| 快速验证 | 5 | 0.1 | 快速得到初步结果 |
| 标准分析 | 10 | 0.1 | 平衡性能和准确性 |
| 深度分析 | 15-20 | 0.05 | 更全面但耗时更长 |
| 大规模网络 | 3-5 | 0.2 | 减少计算量 |

### 11.2 网络设计建议

1. **控制变迁数量**：建议 ≤ 20 个变迁
2. **减少不可观测变迁**：提高可诊断性
3. **合理设置时间约束**：避免过度重叠
4. **使用软约束**：便于自动增强

### 11.3 硬件优化

- 使用 SSD 存储
- 增加内存（推荐 ≥ 4GB）
- 使用多核 CPU（未来版本将支持并行化）

---

## 12. 故障排除

### 12.1 常见错误

#### 错误 1: ModuleNotFoundError

```
ModuleNotFoundError: No module named 'matplotlib'
```

**解决方法**：
```bash
pip3 install matplotlib numpy
```

#### 错误 2: JSON 解析错误

```
json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes
```

**解决方法**：
- 检查 JSON 文件格式
- 确保所有字符串使用双引号
- 使用 JSON 验证工具检查语法

#### 错误 3: 时间约束无效

```
ValueError: Invalid time constraint: [3, 1]
```

**解决方法**：
- 确保 `earliest ≤ latest`
- 检查时间值为非负数

#### 错误 4: 内存不足

```
MemoryError
```

**解决方法**：
- 减小 `--max-length` 参数
- 简化 TPN 网络
- 增加系统内存

### 12.2 调试技巧

1. **启用详细输出**：观察控制台输出
2. **检查中间结果**：查看生成的 JSON 文件
3. **逐步测试**：先用小规模网络测试
4. **查看日志**：检查错误信息

### 12.3 获取帮助

如遇到无法解决的问题：
1. 检查本手册的常见问题部分
2. 查看 `README.md` 和 `PROJECT_SUMMARY.md`
3. 运行测试脚本验证环境：`./test.sh`
4. 查看示例文件：`examples/`

---

## 附录 A: 术语表

| 术语 | 英文 | 说明 |
|------|------|------|
| 时间 Petri 网 | Time Petri Net (TPN) | 带时间约束的 Petri 网 |
| 库所 | Place | TPN 的基本组成单元 |
| 变迁 | Transition | TPN 的动作单元 |
| 标识 | Marking | 库所中 token 的分布 |
| 可诊断性 | Diagnosability | 能否区分正常和故障行为 |
| 观测同步器 | Observation Synchronizer | 用于识别可疑观测前缀的自动机 |
| P-ETERG | Prefix-based Extended Timed Execution Reachability Graph | 部分极值时间扩展可达图 |
| 时间模糊性 | Time Ambiguity | 正常和故障路径时间区间重叠 |

---

## 附录 B: 文件清单

```
TPN_Diagnosability_Tool/
├── README.md                    # 项目说明
├── QUICKSTART.md                # 快速开始
├── USER_MANUAL.md               # 用户手册（本文档）
├── PROJECT_SUMMARY.md           # 开发总结
├── requirements.txt             # Python 依赖
├── test.sh                      # 测试脚本
├── main.py                      # 主程序
├── src/                         # 源代码目录
│   ├── tpn/                     # TPN 模块
│   ├── algorithms/              # 算法模块
│   ├── analysis/                # 分析模块
│   └── utils/                   # 工具模块
├── examples/                    # 示例文件
│   ├── example1.json
│   └── example2.json
├── tests/                       # 测试文件
│   ├── test_tpn.py
│   └── test_algorithms.py
└── results/                     # 输出目录（运行后生成）
```

---

**文档版本**: 1.0  
**最后更新**: 2026-03-11  
**反馈**: 如有问题或建议，请查看 PROJECT_SUMMARY.md 中的联系方式

