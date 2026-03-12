---
title: Multi-Candidate Handling Rule
tags: []
keywords: []
importance: 50
recency: 1
maturity: draft
createdAt: '2026-03-12T05:11:48.288Z'
updatedAt: '2026-03-12T05:11:48.288Z'
---
## Raw Concept
**Task:**
Document user interaction convention for handling multiple candidate addresses

**Changes:**
- Added multi-candidate handling rule

**Flow:**
Detect multiple candidates -> List options -> User selects -> Confirm selection

## Narrative
### Structure
Rule for handling multiple address candidates in user interactions

### Highlights
When multiple candidate addresses are found, always list options for user to choose. Never make decisions on behalf of the user.

### Rules
Rule 1: List all candidate options to user
Rule 2: Wait for user selection before proceeding
Rule 3: Do not auto-select or prioritize any candidate

## Facts
- **multi_candidate_handling**: When there are multiple candidate addresses, list options for user to choose, do not decide on own [convention]
