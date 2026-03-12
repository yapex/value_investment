---
title: Test File Location Rule
tags: []
keywords: []
importance: 50
recency: 1
maturity: draft
createdAt: '2026-03-12T05:10:33.030Z'
updatedAt: '2026-03-12T05:10:33.030Z'
---
## Raw Concept
**Task:**
Define where experimental test files should be stored

**Changes:**
- Added rule: test files go to /tmp/ instead of workspace

**Flow:**
Write test code -> Save to /tmp/ -> Run tests -> Cleanup

## Narrative
### Structure
Convention for handling experimental test code

### Dependencies
Requires /tmp/ directory to be writable

### Highlights
All test files for experiments must be written to /tmp/ directory to avoid polluting the working directory

## Facts
- **test_file_location**: 所有测试文件写到/tmp/, 不污染工作区 [convention]
