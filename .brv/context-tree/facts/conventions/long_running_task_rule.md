---
title: Long Running Task Rule
tags: []
keywords: []
importance: 50
recency: 1
maturity: draft
createdAt: '2026-03-12T05:10:32.645Z'
updatedAt: '2026-03-12T05:10:32.645Z'
---
## Raw Concept
**Task:**
Document long-running task handling convention

**Changes:**
- Added rule for tasks exceeding 30 seconds

**Flow:**
Task check -> spawn child process if > 30s -> execute -> return result

**Timestamp:** 2026-03-12

## Narrative
### Structure
Rule applies to any task that may take longer than 30 seconds to complete

### Highlights
Use child process spawning (e.g., Python multiprocessing, Node child_process) for long-running operations

### Rules
Rule: Tasks exceeding 30 seconds must spawn child processes to avoid blocking the main process

## Facts
- **long_running_task_threshold**: Tasks exceeding 30 seconds must spawn child processes [convention]
- **process_blocking_prevention**: Child processes are used to avoid blocking the main process [convention]
