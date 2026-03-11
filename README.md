# TPN Diagnosability Verification and Enhancement Tool

基于论文 "Observation-Driven Diagnosability Verification and Enhancement for Time Petri Nets" 的实现工具。

## 功能概述

1. **TPN 输入与解析**：支持用户定义 TPN 网络（库所、变迁、弧、时间约束等）
2. **观测同步器构造**（Algorithm 1）：自动生成观测同步器，检测可疑观测前缀
3. **P-ETERG 构造**（Algorithm 2）：为每个可疑观测前缀构造 P-ETERG
4. **可诊断性增强**（Algorithm 3）：通过时间间隔调整增强可诊断性
5. **性能分析与可视化**：记录每步数据，生成性能对比图表

## 项目结构

```
TPN_Diagnosability_Tool/
├── README.md                    # 项目说明
├── requirements.txt             # Python 依赖
├── setup.py                     # 安装配置
├── src/
│   ├── __init__.py
│   ├── tpn/
│   │   ├── __init__.py
│   │   ├── model.py            # TPN 数据结构定义
│   │   ├── parser.py           # TPN 输入解析器
│   │   └── scg.py              # 状态类图生成
│   ├── algorithms/
│   │   ├── __init__.py
│   │   ├── observation_sync.py  # Algorithm 1: 观测同步器
│   │   ├── peterg.py           # Algorithm 2: P-ETERG 构造
│   │   └── enhancement.py      # Algorithm 3: 可诊断性增强
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── metrics.py          # 性能指标计算
│   │   └── visualizer.py       # 数据可视化
│   └── utils/
│       ├── __init__.py
│       └── logger.py           # 日志记录
├── examples/
│   ├── example1.json           # 示例 TPN 网络
│   └── example2.json
├── tests/
│   ├── __init__.py
│   ├── test_tpn.py
│   ├── test_algorithms.py
│   └── test_analysis.py
└── main.py                     # 主程序入口
```

## 输入格式

TPN 网络使用 JSON 格式定义：

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
  "initial_marking": {"p1": 1, "p2": 0, "p3": 0}
}
```

## 输出指标

程序会记录并分析以下性能指标：

1. **状态空间指标**
   - 观测同步器状态数量
   - P-ETERG 节点数量
   - 探索的状态总数

2. **时间性能**
   - 观测同步器构造时间
   - P-ETERG 构造时间
   - 可诊断性增强时间
   - 总执行时间

3. **可诊断性指标**
   - 可疑观测前缀数量
   - 时间模糊路径对数量
   - 成功解决的模糊对数量
   - 无法解决的模糊对数��

4. **增强效果**
   - 调整的时间约束数量
   - 调整前后的可诊断性对比

## 使用方法

```bash
# 安装依赖
pip install -r requirements.txt

# 运行单个 TPN 分析
python main.py --input examples/example1.json --max-length 10

# 批量测试不同规模的 TPN
python main.py --batch examples/ --output results/

# 生成性能对比图表
python main.py --visualize results/
```

## 开发计划

- [ ] Phase 1: 核心数据结构与 TPN 解析器
- [ ] Phase 2: Algorithm 1 实现（观测同步器）
- [ ] Phase 3: Algorithm 2 实现（P-ETERG）
- [ ] Phase 4: Algorithm 3 实现（可诊断性增强）
- [ ] Phase 5: 性能分析与可视化
- [ ] Phase 6: 测试与优化
