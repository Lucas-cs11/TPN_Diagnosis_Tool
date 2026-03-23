# P-ETERG 算法修复方案

## 对比论文发现的问题

### 问题 1：观测匹配逻辑错误

**论文算法（Algorithm 2, Line 12-15）**：
```
for each t ∈ Enabled(M) do
    if t is observable and λ(t) = φ[k+1] then
        // 匹配成功，k' = k + 1
    else if t is unobservable then
        // k' = k
```

**当前代码问题**：
```python
# 错误：在触发变迁之前检查观测
if t.is_observable():
    if k < m and t.label != self.observation_prefix[k]:
        continue  # 跳过不匹配的观测
```

**修复方案**：
- 观测匹配应该基于**已触发的观测数量 k**
- 如果 `t` 是可观测的且 `λ(t) == φ[k]`（注意是 k 不是 k+1），则 `k' = k + 1`
- 如果 `k >= m`（已匹配完所有观测），则不再扩展可观测变迁

---

### 问题 2：初始节点构造错误

**论文算法（Algorithm 2, Line 3-5）**：
```
S ← {S₀}
Q ← {S₀}
where S₀ = (M₀, 0, 0, 0, N)
```

**当前代码问题**：
```python
# 错误：创建了两个初始节点
S0_normal = ETERGNode(M0, 0, 0, 0, 'N')
S0_fault = ETERGNode(M0, 0, 0, 0, 'F')
```

**修复方案**：
- 只创建一个初始节点 `S₀ = (M₀, 0, 0, 0, N)`
- 路径标签 `δ` 在触发故障变迁时才变为 `F`

---

### 问题 3：状态去重条件不完整

**论文定义（Definition 12）**：
P-ETERG 节点定义为 `S = (M, k, t_min, t_max, δ)`

**当前代码问题**：
```python
def __eq__(self, other):
    return (self.marking == other.marking and
            self.k == other.k and
            self.delta == other.delta)
    # 缺少时间区间的比较！
```

**修复方案**：
根据论文，两个节点相同当且仅当：
- `M == M'`
- `k == k'`
- `δ == δ'`
- `[t_min, t_max] == [t_min', t_max']`（或者时间区间完全重叠）

但这会导致节点数爆炸！论文中可能使用了**时间区间合并**策略：
- 如果 `(M, k, δ)` 相同但时间区间不同，则合并为一个节点
- 新节点的时间区间为 `[min(t_min, t_min'), max(t_max, t_max')]`

---

### 问题 4：端到端延迟计算错误

**论文方法**：
- `ED_min(π)` = 从初始节点到当前节点的最短路径的 `t_min` 之和
- `ED_max(π)` = 从初始节点到当前节点的最长路径的 `t_max` 之和

**当前代码问题**：
```python
# 简单累加，没有考虑路径选择
tmin_prime = tmin + t.time_constraint.earliest
tmax_prime = tmax + t.time_constraint.latest
```

**修复方案**：
- 每个节点应该记录**从初始节点到达该节点的最小和最大延迟**
- 如果多条路径到达同一节点，应该取：
  - `t_min = min(所有路径的 t_min)`
  - `t_max = max(所有路径的 t_max)`

---

## 修复优先级

1. **高优先级**：修复观测匹配逻辑（问题 1）
2. **高优先级**：修复初始节点构造（问题 2）
3. **中优先级**：修复状态去重条件（问题 3）
4. **中优先级**：修复端到端延迟计算（问题 4）

---

## 测试验证

修复后，应该满足：
- Example 1, φ = 'a': 3 个节点，NOT time-ambiguous
- Example 1, φ = 'ab': 5 个节点，time-ambiguous
- Example 2, φ = 'ac': 可诊断（NOT time-ambiguous）
- Example 2, φ = 'ab': 不可诊断（time-ambiguous）
