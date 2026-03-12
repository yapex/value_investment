---
children_hash: 3f6143d86546b6b3f26770807a14d0ef6b85b002fa44b62d43b32fa2c59a0ef1
compression_ratio: 0.5078369905956113
condensation_order: 1
covers: [memory_hierarchical_architecture.md, project_architecture.md]
covers_token_total: 638
summary_level: d1
token_count: 324
type: summary
---
# Architecture Overview

## Memory Architecture
Three-tier hierarchical structure for documentation and knowledge management:
- **Core layer**: MEMORY.md as central documentation
- **Extension layer**: modules/ for modular extensions
- **Logging layer**: .learnings/ for learning logs
- Core implements on-demand loading for efficiency

*See `memory_hierarchical_architecture.md` for details*

## Project Architecture
Value investment analysis tool supporting A-share, HK-share, and US-share fundamental analysis with modular Python architecture.

### Core Components
- **Entry points**: api.py (API interface), cli.py (command line interface)
- **Data layer**: data/providers/ for multi-market data acquisition
- **Processing**: indicators/ for indicator calculations, data/mapper.py with CORE_FIELD_MAPPING
- **Data source**: akshare library
- **Package management**: uv

### Market Support
- **A-share**: 6-digit codes (starting with 0/3/6)
- **HK-share**: 5-digit codes
- **US-share**: letter codes

### Data Flow
User input → CLI/API → Data providers → Indicators calculation → Analysis output

### Features
- Caching strategy with type-specific TTLs
- CLI commands for historical data and financial reports
- pytest-based testing

*See `project_architecture.md` for implementation details*