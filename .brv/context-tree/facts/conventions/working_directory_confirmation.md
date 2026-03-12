---
title: Working Directory Confirmation
tags: []
keywords: []
importance: 50
recency: 1
maturity: draft
createdAt: '2026-03-12T05:11:45.405Z'
updatedAt: '2026-03-12T05:11:45.405Z'
---
## Raw Concept
**Task:**
Document working directory confirmation convention

**Changes:**
- Added working directory confirmation rule

**Timestamp:** 2026-03-12

## Narrative
### Structure
Convention for task execution workflow

### Highlights
Must run pwd to confirm current directory before each task, never assume fixed location

### Rules
Rule 1: Always run pwd before starting any task
Rule 2: Never assume working directory is fixed

## Facts
- **working_directory_confirmation**: Must confirm working directory with pwd before each task [convention]
