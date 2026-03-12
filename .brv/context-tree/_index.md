---
children_hash: e8ba0c16d28aedff926a18bf1f9ab04deaae24867acbdbcf262b06ec0364bb32
compression_ratio: 0.39290586630286495
condensation_order: 3
covers: [architecture/_index.md, automation/_index.md, data/_index.md, documentation/_index.md, facts/_index.md, integration/_index.md]
covers_token_total: 2199
summary_level: d3
token_count: 864
type: summary
---
# Value Investment Tool Architecture

## Overview

Comprehensive knowledge management system for a value investment analysis tool supporting A-share, HK-share, and US-share markets. The architecture spans six interconnected domains: project structure, automation, caching, documentation, factual conventions, and external integrations.

## Core Architecture (architecture/)

Three architectural systems operate in concert:

**Project Architecture** — Modular Python system with entry points (api.py, cli.py), data layer supporting multi-market acquisition via akshare, indicator calculations, and type-specific caching. Uses uv for package management and pytest for testing.

**Memory Architecture** — Three-tier hierarchy: core layer (MEMORY.md as hub), extension layer (modules/), and logging layer (.learnings/). Implements on-demand loading.

**Skill System** — Three-layer pattern: SKILL.md (configuration), Agent (decision maker), Script (zero-config executor). Evolution protected by MEMORY.md process enforcement, HEARTBEAT health checks, and self-evolution rules. Falls back to LEARNINGS.md on timeout.

*Drill-down: `project_architecture.md`, `memory_hierarchical_architecture.md`, `skill_architecture.md`, `evolution_mechanism.md`*

## Data Caching Strategy (data/)

Type-specific TTLs reflecting market dynamics:

- **A-share stocks**: Next day midnight (daily refresh)
- **HK/US stocks**: Next June 30 (annual fiscal cycle)
- **Historical prices**: 1 year expiration
- **Financial reports**: Next June 30

*Drill-down: `cache_ttl_strategy.md`*

## Automation (automation/)

Clipboard-based Chinese text input on macOS: copy text → clipboard paste → arrow key candidate selection. Required for programmatic non-ASCII entry.

*Drill-down: `macos_chinese_input_automation.md`*

## Documentation (documentation/)

Central index at docs/README.md with two key references: market indicator differences across A/HK/US markets (docs/market_indicator_differences.md) and IFRS field standardization (docs/ifrs_standard_fields.md).

*Drill-down: `documentation_index.md`*

## Conventions & Configuration (facts/)

Four operational rules following validate→execute→confirm pattern:

- **working_directory_confirmation** — Verify pwd before tasks
- **long_running_task_rule** — Spawn child processes for >30s tasks
- **multi_candidate_handling_rule** — Present options, never auto-select
- **test_file_location_rule** — Write experimental tests to /tmp/

Personal configuration: knowledge base ID `jnZm6R1J`, 60-second sync interval. Project standards: market-specific annual report directories (a_annual_reports/, hk_annual_reports/, us_annual_reports/), skill storage at `/Volumes/yapex_ssd/yapex-bot/workspace/skills/`, macOS iCloud permission workaround via Terminal Full Disk Access.

*Drill-down: `conventions/`, `personal/`, `project/`*

## External Integrations (integration/)

**Email** — QQ SMTP via EmailMessage class with RFC2231 Chinese filename encoding and inline image embedding.

**Notes** — Get笔记 API returns note_id, add operations have delayed response, remove uses note_ids array.

*Drill-down: `email/qq.md`, `notes/get_api.md`*

## Key Relationships

Skill system evolution depends on memory hierarchical architecture. All domains enforce explicit confirmation steps before proceeding. Data caching strategy directly enables project architecture performance. Automation enables Chinese text entry required for A-share market analysis.