---
children_hash: 4d8894d5f5ee8b3c2d29fe9f0dad6ee816ccf042af9de7efb4c1796ea4e3cf2f
compression_ratio: 0.5416666666666666
condensation_order: 2
covers: [caching_strategy/_index.md]
covers_token_total: 240
summary_level: d2
token_count: 130
type: summary
---
# Cache TTL Strategy

## Overview
Caching time-to-live policies differentiated by data type and market dynamics.

## TTL Policies
- **A-share stocks**: Next day midnight (daily refresh required)
- **HK/US stocks**: Next June 30 (annual fiscal cycle)
- **Historical prices**: 1 year expiration
- **Financial reports**: Next June 30

## Design Rationale
TTLs reflect market speed—A-shares require daily updates while HK/US align with annual fiscal cycles.

**Reference**: `cache_ttl_strategy.md` for implementation details.