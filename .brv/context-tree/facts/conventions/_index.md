---
children_hash: f55a6ebe42f6b18edc3c143a3dc69f9d54216ae49c0dff702bc032c83ce2013c
compression_ratio: 0.4502923976608187
condensation_order: 1
covers: [long_running_task_rule.md, multi_candidate_handling_rule.md, test_file_location_rule.md, working_directory_confirmation.md]
covers_token_total: 855
summary_level: d1
token_count: 385
type: summary
---
# Conventions Summary

Domain for documenting project-wide conventions and workflow rules.

## Overview

This domain contains operational conventions that govern task execution, user interaction patterns, and file handling practices. All rules are marked as draft and should be refined through practical application.

## Child Entries

### Task Execution Rules

- **working_directory_confirmation**: Requires running `pwd` before each task to confirm current directory. Never assumes fixed location.
- **long_running_task_rule**: Tasks exceeding 30 seconds must spawn child processes (Python multiprocessing, Node child_process) to avoid blocking the main process.

### User Interaction Rules

- **multi_candidate_handling_rule**: When multiple candidate addresses are found, always list options for user selection. Never auto-select or prioritize any candidate.

### File Handling Rules

- **test_file_location_rule**: All experimental test files must be written to `/tmp/` directory to avoid polluting the working directory.

## Key Relationships

All four conventions follow a common pattern: **validate → execute → confirm**. The working directory confirmation is a prerequisite for other rules, while test file location and long-running task rules govern implementation details.

## Patterns

- All rules use explicit confirmation steps before proceeding
- User agency is prioritized (multi-candidate handling)
- Process isolation is used for resource-intensive operations
- Workspace cleanliness is enforced via `/tmp/` for experiments