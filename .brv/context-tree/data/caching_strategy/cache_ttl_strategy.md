---
title: Cache TTL Strategy
tags: []
keywords: []
importance: 50
recency: 1
maturity: draft
createdAt: '2026-03-12T05:01:51.470Z'
updatedAt: '2026-03-12T05:01:51.470Z'
---
## Raw Concept
**Task:**
Define caching strategy for different data types across markets

**Changes:**
- Established cache TTL policies

## Narrative
### Structure
Cache TTL varies by data type and market. Stock info: next day (A-share) or next June 30 (HK/US). Historical prices: 1 year. Financial reports: next June 30.

### Highlights
Different TTLs optimize data freshness vs API rate limits. A-share stock info expires daily (faster market changes), while HK/US stock info expires annually.

### Rules
Stock info cache: A-share expires next day at midnight, HK/US shares expire next June 30
Historical price cache: expires after 1 year
Financial report cache: expires next June 30

## Facts
- **a_share_stock_ttl**: A-share stock info cache expires next day at midnight [project]
- **hk_us_stock_ttl**: HK/US stock info cache expires next June 30 [project]
- **historical_price_ttl**: Historical price cache expires after 1 year [project]
- **financial_report_ttl**: Financial report cache expires next June 30 [project]
