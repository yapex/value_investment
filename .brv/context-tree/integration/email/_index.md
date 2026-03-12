---
children_hash: eadfbef2b85d427dd6e2ad4cd6803bbbfde9ec717fc76d9524bb57b28bc481b3
compression_ratio: 0.8352272727272727
condensation_order: 1
covers: [qq.md]
covers_token_total: 176
summary_level: d1
token_count: 147
type: summary
---
## Email Integration

### Overview
Domain for email sending and receiving integrations across different email providers.

### Topics

**QQ Email Sending** (`integration/email/qq.md`)
- Implements QQ email sending via SMTP using `EmailMessage` class
- Supports attachments via `add_attachment()` method
- Handles Chinese filename encoding using RFC2231 standard
- Includes image embedding for inline previews

### Key Patterns
- All email integrations follow: `EmailMessage` creation → attachment handling → send operation
- Encoding solutions address cross-platform filename compatibility