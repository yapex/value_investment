---
children_hash: b4853f217589e1db1f61fccf85379fa289cb52570ac3747deef5bc042dc9c1c3
compression_ratio: 0.40798045602605865
condensation_order: 2
covers: [context.md, conventions/_index.md, personal/_index.md, project/_index.md]
covers_token_total: 1228
summary_level: d2
token_count: 501
type: summary
---
# Domain: facts

## Overview
Central repository for personal configuration, project conventions, and operational workflow rules. Organizes knowledge into three subdomains: personal settings, project standards, and execution conventions.

## Subdomains

### conventions/
Operational rules governing task execution, user interaction, and file handling. Four core rules follow a **validate → execute → confirm** pattern:

- **working_directory_confirmation** — Always verify current directory via `pwd` before tasks
- **long_running_task_rule** — Spawn child processes for tasks >30 seconds to avoid blocking
- **multi_candidate_handling_rule** — Present options to user when multiple candidates exist; never auto-select
- **test_file_location_rule** — Write experimental tests to `/tmp/` to keep workspace clean

### personal/
Personal knowledge base configuration and execution guidelines:

- **get_knowledge_base_configuration** — Get笔记待二刷 knowledge base ID: `jnZm6R1J`, auto-sync interval: 60 seconds
- **work_style_principles** — Execute proactively when goal/path is clear; seek input only when multiple solutions exist, exceptions occur, or time expectations exceeded

### project/
Project-level standards for file organization and environment configuration:

- **annual_reports_directory_structure** — Market-specific structure: `a_annual_reports/`, `hk_annual_reports/`, `us_annual_reports/` with standardized naming: `{stock_code}_{company_name}_{year}_{type}.pdf`
- **skill_storage_convention** — Non-system skills stored at `/Volumes/yapex_ssd/yapex-bot/workspace/skills/`
- **macos_icloud_permission_workaround** — Grant Full Disk Access to Terminal, then spawn Python via shell wrapper to inherit permissions

## Key Relationships

All subdomains enforce explicit confirmation steps before proceeding. Personal configuration feeds into execution guidelines; project conventions enable consistent file discoverability; operational rules apply universally across personal and project contexts.