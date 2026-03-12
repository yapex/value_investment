---
title: Project Architecture
tags: []
keywords: []
importance: 53
recency: 1
maturity: draft
accessCount: 1
createdAt: '2026-03-12T05:01:51.468Z'
updatedAt: '2026-03-12T05:01:51.468Z'
---
## Raw Concept
**Task:**
Value investment analysis tool supporting A-share/HK-share/US-share fundamental analysis

**Changes:**
- Initial project structure established

**Files:**
- src/value_investment/api.py
- src/value_investment/cli.py
- src/value_investment/data/providers/
- src/value_investment/indicators/
- src/value_investment/data/mapper.py

**Flow:**
User input -> CLI/API -> Data providers -> Indicators calculation -> Analysis output

## Narrative
### Structure
Python project with modular architecture. Core modules: api.py (API entry point), cli.py (command line interface), data/providers/ (data acquisition for A/HK/US markets), indicators/ (indicator calculations), data/mapper.py (field mapping with CORE_FIELD_MAPPING). Data source: akshare.

### Dependencies
Uses akshare for data acquisition. Python project managed with uv.

### Highlights
Supports three markets: A-share (6-digit numbers), HK-share (5-digit numbers), US-share (letter codes). Includes caching strategy with different TTLs per data type.

### Examples
CLI commands: uv run python -m value_investment.cli --help
uv run python -m value_investment.cli hist 600519 --end 20241231
uv run python -m value_investment.cli financial 600519 --end 2024

Test command: uv run python -m pytest tests/ -v

## Facts
- **data_source**: Data source is akshare [project]
- **tech_stack**: Project uses Python and uv package manager [project]
- **a_share_format**: A-share codes are 6-digit numbers (starting with 0/3/6) [project]
- **hk_share_format**: HK-share codes are 5-digit numbers [project]
- **us_share_format**: US-share codes are letter codes [project]
