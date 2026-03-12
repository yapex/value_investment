---
children_hash: a748facc4a684264812739270a4a9fd7952fb9414033d1cb689405c12e7af7e3
compression_ratio: 0.7034220532319392
condensation_order: 1
covers: [evolution_mechanism.md, skill_architecture.md]
covers_token_total: 526
summary_level: d1
token_count: 370
type: summary
---
# Skill System Architecture

The skill system implements a three-layer architecture for skill definition and execution, protected by a three-layer evolution mechanism.

## Architecture Pattern

The system follows a **SKILL.md → Agent → Script** flow:

- **SKILL.md** serves as the configuration center, defining skill metadata
- **Agent** acts as the decision maker, selecting execution strategies
- **Script** functions as a zero-config executor that reads configuration from environment variables and parameters

This separation enables skills to be defined declaratively while remaining executable without hardcoded configuration.

## Evolution Protection Mechanism

Skill evolution is guarded by three layers:

1. **MEMORY.md** — Enforces the evolution process, ensuring all changes go through proper documentation
2. **HEARTBEAT** — Provides scheduled health checks to monitor skill integrity
3. **Self-evolution rules** — Govern automatic improvements to skills

When ByteRover encounters a timeout, it falls back to **LEARNINGS.md** as an alternative learning storage, ensuring continuity even under failure conditions.

## Key Relationships

- Evolution mechanism depends on `memory_hierarchical_architecture` for MEMORY.md structure
- Both entries reference each other as related documentation

**Drill-down entries:**
- `evolution_mechanism.md` — Full details on the three-layer protection mechanism
- `skill_architecture.md` — Complete architecture pattern documentation