# 修正计划

## 问题清单

### 问题1: 港股数据字段映射不完整
- **现象**: 港股数据返回的中文列名太多，英文列名很少
- **影响**: 开发者需要混用中英文列名才能完成计算
- **根因**: `mapper.py` 中港股字段的英文映射不完整

### 问题2: CLI 指标查询不支持多年历史
- **现象**: `v-invest indicator roe -s 00700 -m HK -y 10` 只返回当前值
- **影响**: 无法批量获取多年历史数据进行趋势分析
- **根因**: CLI 的 indicator 命令实现逻辑问题

### 问题3: API 使用复杂度高
- **现象**: 需要手动合并多个数据源（资产负债表+利润表+现金流量表）才能计算ROE
- **影响**: 使用门槛高，不够便捷
- **根因**: 缺乏统一的财务指标历史数据获取接口

---

## 修正计划

### Phase 1: 完善港股字段映射 (Priority: High) ✅ 已验证

- [x] 1.1 分析当前港股数据返回的完整列名列表
- [x] 1.2 在 `mapper.py` 中补充港股字段的中英文映射（已存在）
- [x] 1.3 验证映射生效

**发现**: 字段映射已存在且有效，但 API 层的 `get_balance_sheet()` 等方法没有自动应用映射

**结论**: 
- Mapper 映射已完整 ✓
- 需要修改 API 使 `get_*_sheet` 方法默认返回映射后的数据

### Phase 1.1: 修复 API 层字段映射 (Priority: High) ✅ 已完成

- [x] 1.1.1 修改 `get_balance_sheet` 方法，默认应用 DataMapper 映射
- [x] 1.1.2 修改 `get_profit_sheet` 方法，默认应用 DataMapper 映射
- [x] 1.1.3 修改 `get_cashflow_sheet` 方法，默认应用 DataMapper 映射
- [x] 1.1.4 添加参数控制是否应用映射（`map_fields` 参数，向后兼容）

**文件**: `src/value_investment/api.py`

### Phase 2: 改进 CLI 指标查询 (Priority: High) ✅ 已完成

- [x] 2.1 检查 CLI indicator 命令实现
- [x] 2.2 支持多年历史数据返回（表格形式）
- [x] 2.3 测试验证

**文件**: `src/value_investment/cli.py` 或相关模块

### Phase 3: 增强 API 便捷性 (Priority: Medium) ✅ 已完成

- [x] 3.1 在 `ValueInvestment` 类中添加批量获取财务指标历史数据的方法 `get_indicator_history`
- [x] 3.2 支持一次性获取 ROE/ROA/净利润率等核心指标多年数据
- [x] 3.3 测试验证

**文件**: `src/value_investment/api.py`

**使用方法**:
```python
vi = ValueInvestment(market='HK')
df = vi.get_indicator_history('roe,roa,net_profit_margin,gross_margin', '00700', years=10)
```

### Phase 4: 更新文档 (Priority: Medium) ✅ 已完成

- [x] 4.1 更新 SKILL.md 中的命令示例
- [x] 4.2 更新 ROE 分析框架文档（添加 Python API 使用方法）
- [x] 4.3 补充港股数据字段参考文档（DataMapper 已自动处理）

**文件**: 
- `skills/v-invest/SKILL.md`
- `skills/v-invest/REFERENCES/roe_analysis_framework/deep_analysis.md`

---

## 修正总结

### 已完成的修改

| 文件 | 修改内容 |
|:-----|:---------|
| `src/value_investment/api.py` | 1. `get_balance_sheet` 添加 `map_fields` 参数<br>2. `get_profit_sheet` 添加 `map_fields` 参数<br>3. `get_cashflow_sheet` 添加 `map_fields` 参数<br>4. 新增 `get_indicator_history` 方法 |
| `src/value_investment/cli.py` | indicator 命令支持多年历史数据返回 |
| `skills/v-invest/SKILL.md` | 更新命令示例，添加多年数据说明 |
| `skills/v-invest/REFERENCES/roe_analysis_framework/deep_analysis.md` | 添加 Python API 使用方法 |

### 测试验证

```bash
# CLI 测试 - 获取10年ROE数据
v-invest indicator roe -s 00700 -m HK -y 10

# Python API 测试
vi = ValueInvestment(market='HK')
df = vi.get_indicator_history('roe,roa,net_profit_margin', '00700', years=10)
```

---

## 预期结果

1. 港股数据可以使用英文列名直接访问：`df['net_profit']`、`df['total_revenue']`
2. CLI 命令 `v-invest indicator roe -s 00700 -m HK -y 10` 返回10年历史数据
3. API 调用更简洁：`vi.get_financial_indicator_history('00700', years=10)`

---

## 执行顺序

1. 先完成 Phase 1（字段映射）
2. 再完成 Phase 2（CLI改进）
3. 然后 Phase 3（API增强）
4. 最后 Phase 4（文档更新）
