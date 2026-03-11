# TPN 可诊断性验证与增强工具 - 快速开始

## 安装

```bash
cd ~/Desktop/TPN_Diagnosability_Tool
pip install -r requirements.txt
```

## 基本使用

### 1. 分析单个 TPN 网络

```bash
python main.py --input examples/example1.json --max-length 10
```

参数说明：
- `--input`: TPN 输入文件（JSON 格式）
- `--max-length`: 最大观测前缀长度（默认 10）
- `--epsilon`: 时间间隔增量（默认 0.1）
- `--output`: 输出目录（默认 results）

### 2. 批量分析

```bash
python main.py --batch examples/ --output results/
```

### 3. 运行测试

```bash
python -m pytest tests/ -v
```

或使用 unittest：

```bash
python -m unittest discover tests/
```

## 输入格式

TPN 网络使用 JSON 格式定义，示例：

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
    }
  ],
  "arcs": [
    {"from": "p1", "to": "t1"},
    {"from": "t1", "to": "p2"}
  ],
  "initial_marking": {
    "p1": 1,
    "p2": 0
  }
}
```

### 字段说明

**Transition 字段：**
- `name`: 变迁名称
- `type`: 变迁类型（`normal` 或 `fault`）
- `observable`: 是否可观测（`true` 或 `false`）
- `label`: 观测标签（不可观测变迁使用 `"epsilon"`）
- `time_constraint`: 时间约束
  - `type`: 约束类型（`soft` 或 `hard`）
  - `earliest`: 最早触发时间
  - `latest`: 最晚触发时间

**Arc 字段：**
- `from`: 源节点（库所或变迁名称）
- `to`: 目标节点（库所或变迁名称）
- `weight`: 弧权重（可选，默认 1）

**Initial Marking：**
- 键：库所名称
- 值：token 数量

## 输出结果

程序会生成以下输出：

1. **性能指标 JSON**：`results/<tpn_name>_metrics.json`
   - TPN 基本信息
   - 观测同步器统计
   - P-ETERG 构造统计
   - 可诊断性分析结果
   - 时间性能数据

2. **可视化图表**：`results/plots/`
   - 单个 TPN 详细分析图
   - 批量分析对比图

3. **控制台输出**：
   - 实时进度信息
   - 性能摘要

## 示例输出

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

## 下一步

1. 准备你的 TPN 网络 JSON 文件
2. 运行分析程序
3. 查看生成的性能指标和可视化图表
4. 根据结果调整 TPN 网络或参数

## 常见问题

**Q: 如何创建自己的 TPN 网络？**

A: 参考 `examples/` 目录中的示例文件，按照 JSON 格式定义你的网络。

**Q: 最大观测前缀长度应该设置多少？**

A: 取决于你的 TPN 规模和复杂度。建议从 10 开始，如果需要更深入的分析可以增加。

**Q: 程序运行很慢怎么办？**

A: 尝试减小 `--max-length` 参数，或者简化 TPN 网络结构。

**Q: 如何解读可诊断性结果？**

A: 
- `Ambiguous Pairs = 0`: TPN 是可诊断的
- `Resolved > 0`: 通过时间约束调整成功增强了可诊断性
- `Unresolved > 0`: 存在无法通过时间调整解决的模糊性，可能需要禁用某些事件

## 技术支持

如有问题，请查看：
- README.md：完整项目文档
- 论文：算法理论基础
- 代码注释：实现细节
