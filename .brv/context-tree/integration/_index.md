---
children_hash: 4780f809be3e4319e86b18af4037cda322e53a403836ab5eb164f6cd25b6e3ad
compression_ratio: 0.5941320293398533
condensation_order: 2
covers: [email/_index.md, notes/_index.md]
covers_token_total: 409
summary_level: d2
token_count: 243
type: summary
---
# Integration Domain

## Overview
Domain for external service integrations including email providers and note-taking systems.

## Topics

### Email Integration (`integration/email/qq.md`)
- QQ email sending via SMTP using `EmailMessage` class
- Attachment support via `add_attachment()` method
- Chinese filename encoding using RFC2231 standard
- Image embedding for inline previews

### Notes Integration (`integration/notes/get_api.md`)
- Get笔记API returns `note_id` for knowledge base notes
- Global unified `id` return across operations
- Add operations have delayed response characteristics
- Remove operations use `note_ids` array for batch processing

## Key Patterns
- Email: `EmailMessage` creation → attachment handling → send operation
- Notes: Fetch note → return note_id → add has delay → remove uses array

## Relationships
- Both integrations follow creation→operation→response pattern
- Email handles cross-platform encoding; Notes handles async responses