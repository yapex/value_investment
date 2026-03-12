---
children_hash: a97a262d69d1e9e38c8c3592b09c120fc055f6985bd40c79d9b8c85b81398150
compression_ratio: 0.3531645569620253
condensation_order: 1
covers: [annual_reports_directory_structure.md, context.md, macos_icloud_permission_workaround.md, skill_storage_convention.md]
covers_token_total: 790
summary_level: d1
token_count: 279
type: summary
---
# Domain: project

Project-level conventions and standards covering file organization, naming patterns, and environment-specific configurations.

## Conventions

**Financial Reports** — Market-specific directory structure with standardized file naming:
- A股 reports: `a_annual_reports/`
- 港股 reports: `hk_annual_reports/`
- 美股 reports: `us_annual_reports/`
- File format: `{stock_code}_{company_name}_{year}_{type}.pdf`

See `annual_reports_directory_structure.md` for details.

**Skill Storage** — Non-system skills centralized at `/Volumes/yapex_ssd/yapex-bot/workspace/skills/`

See `skill_storage_convention.md` for details.

## Environment Configuration

**macOS Full Disk Access** — Python subprocess lacks FDA permission by default. Workaround: grant FDA to Terminal app, then spawn Python via shell wrapper to inherit permissions.

See `macos_icloud_permission_workaround.md` for details.

## Key Relationships

- All conventions enforce consistent naming for discoverability
- Skill storage location enables centralized skill management
- macOS workaround enables file system access for automated workflows