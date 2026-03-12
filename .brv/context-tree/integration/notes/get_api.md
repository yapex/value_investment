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
Rule 1: 知识库笔记返回note_id
Rule 2: 全局返回统一id
Rule 3: 加入操作有延迟返回
Rule 4: 移除使用note_ids数组
