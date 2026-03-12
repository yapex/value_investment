---
children_hash: 86b5b66dd02485ef28be2a77cb18fd189476fb8406e2389ce964bc17d517a9bc
compression_ratio: 0.7479091995221028
condensation_order: 2
covers: [overview/_index.md, skill_system/_index.md]
covers_token_total: 837
summary_level: d2
token_count: 626
type: summary
---
# Architecture Domain

This domain covers two interconnected architectural systems: the overall project architecture for the value investment tool and the skill system that enables skill definition and execution.

## Project Architecture

The value investment analysis tool supports fundamental analysis across three markets: A-share (6-digit codes starting with 0/3/6), HK-share (5-digit codes), and US-share (letter codes). The modular Python architecture consists of entry points (api.py, cli.py), a data layer in data/providers/ for multi-market acquisition, indicator calculations in indicators/, and data/mapper.py with CORE_FIELD_MAPPING. The system uses the akshare library for data sourcing and uv for package management. A caching strategy with type-specific TTLs optimizes performance, while pytest provides testing coverage.

*Drill-down: `project_architecture.md` for full implementation details*

## Memory Architecture

Documentation and knowledge management follow a three-tier hierarchical structure: the core layer uses MEMORY.md as the central documentation hub, the extension layer employs modules/ for modular extensions, and the logging layer uses .learnings/ for learning logs. Core implements on-demand loading for efficiency.

*Drill-down: `memory_hierarchical_architecture.md` for details*

## Skill System Architecture

The skill system implements a three-layer architecture pattern: SKILL.md serves as the configuration center defining skill metadata, the Agent acts as the decision maker selecting execution strategies, and the Script functions as a zero-config executor reading configuration from environment variables. This separation enables declarative skill definition without hardcoded configuration.

Skill evolution is protected by three layers: MEMORY.md enforces the evolution process ensuring changes go through proper documentation, HEARTBEAT provides scheduled health checks monitoring skill integrity, and self-evolution rules govern automatic improvements. When ByteRover encounters a timeout, it falls back to LEARNINGS.md as alternative learning storage.

*Drill-down: `skill_architecture.md` for complete architecture pattern, `evolution_mechanism.md` for full protection mechanism details*

## Key Relationships

The skill system's evolution mechanism depends on the memory hierarchical architecture for MEMORY.md structure. Both architectural systems reference each other as related documentation, creating a interconnected knowledge management ecosystem.