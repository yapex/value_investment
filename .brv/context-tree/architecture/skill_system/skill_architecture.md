---
title: Skill Architecture
tags: []
keywords: []
importance: 50
recency: 1
maturity: draft
createdAt: '2026-03-12T05:09:27.107Z'
updatedAt: '2026-03-12T05:09:27.107Z'
---
## Raw Concept
**Task:**
Document Skill architecture pattern for ByteRover

**Changes:**
- New Skill architecture pattern documented

**Flow:**
SKILL.md配置中心 → Agent决策者 → Script零配置执行者

## Narrative
### Structure
三层架构: SKILL.md作为配置中心定义技能元数据, Agent作为决策者选择执行策略, Script作为零配置执行者从环境变量/参数读取配置运行

### Highlights
脚本从环境变量/参数读取配置, 实现零配置执行

## Facts
- **skill_config_center**: SKILL.md是配置中心 [project]
- **skill_decision_maker**: Agent是决策者 [project]
- **skill_executor**: Script是零配置执行者 [project]
- **script_config_source**: 脚本从环境变量/参数读取配置 [convention]
