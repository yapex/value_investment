---
title: QQ邮箱发送功能
tags: []
keywords: []
importance: 50
recency: 1
maturity: draft
createdAt: '2026-03-12T05:11:22.872Z'
updatedAt: '2026-03-12T05:11:22.872Z'
---
## Raw Concept
**Task:**
实现QQ邮箱发送功能，支持附件和中文文件名编码

**Changes:**
- 新增QQ邮箱发送功能
- 支持图片内嵌预览
- 支持中文文件名RFC2231编码

**Flow:**
EmailMessage创建 -> add_attachment()添加附件 -> 发送邮件

**Timestamp:** 2026-03-12

## Narrative
### Structure
使用EmailMessage类进行邮件构建，通过add_attachment()方法添加附件

### Dependencies
需要QQ邮箱SMTP配置

### Highlights
支持图片内嵌预览，支持中文文件名RFC2231编码解决附件名乱码问题

## Facts
- **qq_email_api**: QQ邮箱发送功能使用 EmailMessage 类配合 add_attachment() 方法 [project]
- **image_embedding**: 支持图片内嵌预览功能 [project]
- **chinese_filename_encoding**: 支持中文文件名RFC2231编码 [project]
