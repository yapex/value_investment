---
children_hash: c2a70dfb10a88380270e349f06ab664c1f946370776bff7f8d49e5af72af339d
compression_ratio: 0.993006993006993
condensation_order: 1
covers: [get_api.md]
covers_token_total: 143
summary_level: d1
token_count: 142
type: summary
---
## get_api.md
---
title: Get笔记API
tags: []
keywords: []
importance: 50
recency: 1
maturity: draft
createdAt: '2026-03-12T05:11:48.406Z'
updatedAt: '2026-03-12T05:11:48.406Z'
---
## Raw Concept
**Task:**
Document Get笔记API behavior for knowledge base notes

**Changes:**
- 知识库笔记返回note_id
- 全局返回id
- 加入有延迟返回
- 移除用note_ids数组

**Flow:**
获取笔记 -> 返回note_id -> 添加操作有延迟 -> 移除使用note_ids数组

## Narrative
### Structure
笔记API返回note_id作为知识库笔记标识，全局使用统一id返回

### Highlights
添加笔记操作有延迟返回特性，移除笔记使用note_ids数组批量处理

### Rules
Rule 1: 知识库笔记返回no
[summary compaction; truncated from 143 tokens]