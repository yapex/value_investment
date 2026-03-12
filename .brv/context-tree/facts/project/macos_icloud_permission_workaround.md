---
title: macOS iCloud Permission Workaround
tags: []
keywords: []
importance: 50
recency: 1
maturity: draft
createdAt: '2026-03-12T05:09:21.823Z'
updatedAt: '2026-03-12T05:09:21.823Z'
---
## Raw Concept
**Task:**
Document macOS iCloud Full Disk Access permission issue and workaround

**Changes:**
- Documented iCloud permission workaround for Python subprocess

**Flow:**
Python subprocess lacks FDA -> Authorize Terminal -> Shell wrapper inherits permissions

## Narrative
### Structure
macOS security restricts Python subprocess from accessing iCloud/Full Disk Access. Solution: grant Full Disk Access to Terminal app, then use shell wrapper script to spawn Python subprocess so it inherits Terminal's permissions.

### Highlights
Shell wrapper approach allows Python subprocess to inherit Terminal's Full Disk Access permissions on macOS

## Facts
- **macos_fda_permission**: Python subprocess on macOS does not have Full Disk Access permission by default [environment]
- **permission_inheritance**: Granting Full Disk Access to Terminal allows shell wrapper to inherit those permissions for Python subprocess [environment]
