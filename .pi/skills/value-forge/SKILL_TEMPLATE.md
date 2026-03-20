---
name: {skill-name}
description: {从文档中提取的描述}
---

# {文档标题}

## 使用方式

```
用户: "{分析场景}"
Skill: 执行以下数据获取，然后阅读 [REFERENCE.md](./REFERENCE.md) 输出分析报告
```

## 数据获取

```bash
v-invest query {股票} -r "{字段}" -e {年份} -y {年数}
```

## 执行

**必须按 [REFERENCE.md](./REFERENCE.md) 中的要求执行分析！**

1. 获取财务数据
2. 阅读 [REFERENCE.md](./REFERENCE.md)（分析师文档）
3. **严格按 REFERENCE.md 中的段落结构、阈值标准、判定规则执行分析**
4. 输出报告
