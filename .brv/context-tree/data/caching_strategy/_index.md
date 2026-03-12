---
children_hash: 111a886aeb8c24a0600ea24729b3481e3c244baf62a2c7b74705b468abd45bc2
compression_ratio: 0.6
condensation_order: 1
covers: [cache_ttl_strategy.md]
covers_token_total: 300
summary_level: d1
token_count: 180
type: summary
---
# Cache TTL Strategy

## Overview
Defines caching time-to-live (TTL) policies for different data types across markets, balancing data freshness with API rate limit optimization.

## TTL Policies by Data Type

**Stock Information**
- A-share: Expires next day at midnight
- HK/US shares: Expires next June 30

**Historical Data**
- Historical prices: Expires after 1 year

**Financial Reports**
- Expires next June 30

## Key Design Decisions
Differentiated TTLs reflect market dynamics—A-share requires daily refresh due to faster market changes, while HK/US markets use annual expiration aligned with fiscal year cycles.

## Reference
See **cache_ttl_strategy.md** for detailed implementation rules and fact definitions.