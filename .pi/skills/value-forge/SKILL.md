---
name: value-forge
description: 财务分析技能生成器 - 读取分析师文档，自动创建可用于任意股票的分析技能。Use when 用户提供分析文档，需要生成可复用的分析技能。
---

# value-forge

> Meta Skill: 技能生成器，用于将分析师文档转化为可执行的分析技能。

## 架构说明

| 文件 | 职责 |
|------|------|
| **SKILL.md** | 流程和要求（如何生成 skill） |
| **SKILL_TEMPLATE.md** | 内容格式（生成的 SKILL.md 模板） |

---

## 流程（严格禁止跳过）

```
Step 1: 查看系统字段     → v-invest fields
Step 2: 查看系统指标     → v-invest indicators
Step 3: 阅读分析师文档   → 理解结构和需要的字段
Step 4: 映射字段名       → 文档字段 → 系统字段
Step 5: 生成 SKILL.md    → 基于 SKILL_TEMPLATE.md 填空
Step 6: 验证字段         → v-invest query 测试（必须！）
Step 7: 生成 REFERENCE.md
```

**禁止**：在未执行 Step 1-2 的情况下，直接使用文档中的字段名。
**禁止**：在未执行 Step 6 验证的情况下，完成 skill 生成。

---

## Step 1-2: 查看系统可用字段和指标

```bash
v-invest fields
v-invest indicators
```

## Step 3-4: 阅读分析师文档并映射字段

- 直接阅读文档，提取需要的字段
- 将文档字段名映射到系统字段名

## Step 5: 生成 SKILL.md

**参考 [SKILL_TEMPLATE.md](./SKILL_TEMPLATE.md) 模板，按 `{}` 填空**

## Step 6: 验证字段（必须！）

```bash
v-invest query 600519 -r "{所有字段}" -y 1
```

如果出现 `Missing fields` 或 `Unknown fields`，必须修正。

## Step 7: 生成 REFERENCE.md

```bash
cp "docs/分析师文档.md" ".pi/skills/{skill-name}/REFERENCE.md"
```

---

## 输出格式

```
✅ Skill 已创建: .pi/skills/{skill-name}/

包含：
- SKILL.md      # 数据获取指令
- REFERENCE.md  # 分析师文档

验证：v-invest query 测试通过（10年/XX个字段）
```
