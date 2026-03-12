---
title: Annual Reports Directory Structure
tags: []
keywords: []
importance: 60
recency: 1
maturity: draft
updateCount: 2
createdAt: '2026-03-12T05:05:05.284Z'
updatedAt: '2026-03-12T05:10:47.526Z'
---
## Raw Concept
**Task:**
Document financial report file naming and directory structure convention

**Changes:**
- Updated naming convention to include report type placeholder for flexibility

**Flow:**
Market prefix -> reports folder -> {stock_code}_{company_name}_{year}_{type}.pdf

## Narrative
### Structure
Financial reports stored in market-specific directories: a_annual_reports (A股), hk_annual_reports (港股), us_annual_reports (美股). File naming: {stock_code}_{company_name}_{year}_{type}.pdf for flat storage ease of search and deduplication.

### Highlights
Market prefixes: a_ for A股, hk_ for 港股, us_ for 美股. Type placeholder supports 年报, 半年报, 季报, etc.

## Facts
- **a_share_reports_dir**: A股报表目录: a_annual_reports/ [convention]
- **hk_share_reports_dir**: 港股报表目录: hk_annual_reports/ [convention]
- **us_share_reports_dir**: 美股报表目录: us_annual_reports/ [convention]
- **financial_report_filename**: 报表文件命名格式: {股票代码}_{公司名}_{年份}_{类型}.pdf [convention]
