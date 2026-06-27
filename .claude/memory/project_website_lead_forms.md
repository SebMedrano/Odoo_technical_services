---
name: website_lead_forms
description: Custom module for multi-company public contact forms that route CRM leads to specific salespersons/teams
metadata: 
  node_type: memory
  type: project
  originSessionId: 59e7b01e-7bc0-4e0f-9b1a-b38bee66f07d
---

Module at `custom_modules/website_lead_forms/`. Depends on `website`, `crm`, `website_crm`.

**Why:** Each company needs its own public contact form routing leads to the right salesperson and sales team. `website_crm` must be a dependency — without it, `visitor_page_count` is missing from the CRM opportunity form view.

**How to apply:** The menu is under **Website > Configuration > Contact Forms** (parent XML ID is `website.menu_website_global_configuration`). Forms are served at `/contact/<slug>`.

## Key design decisions

- `website.lead.form` model: name, slug, template (selection), user_id, team_id, company_id, active
- `template` field controls which frontend Qweb template is rendered: `standard` or `ees`
- Customer is NOT added as a follower on the created CRM lead (`mail_create_nosubscribe=True` context)
- Confirmation email sent to submitter immediately after lead creation via `mail.mail` (not a template record)
- Confirmation email from address uses `form.company_id.email`

## Submission flow

1. User fills form → clicks **"Preview before submission"** → POST to `/contact/<slug>/preview`
2. Preview route validates; if invalid renders form with errors; if valid renders preview page
3. Preview page shows all submitted data in a table, plus an instruction note and three buttons:
   - **← Go back** (`history.back()`)
   - **Submit ticket** (hidden-field form POSTing all data to `/contact/<slug>/submit`)
   - **Print** (`window.print()`)
4. Submit route creates the CRM lead and sends confirmation email → success page

## Print behaviour (preview page)

CSS `@media print` hides `.no-print` elements, Odoo navbar/header/footer. The `.print-container` stays in normal document flow — no repositioning. This avoids the duplicate-page bug caused by `position: fixed` and the extra-blank-page bug caused by `position: absolute`.

## Standard template fields
Name, Email, Phone, Subject, Message

## EES template fields
Name, Email, Title of request, Supervisor Name/Research Group (required), Supervisor Email (required), Worktag, Speedchart, Department, Priority, Work Location, Repair Info (Make/Model/Serial), Instrument delivered to shop (Yes/No), Message

All extra EES fields are written into the CRM lead `description` as formatted HTML and included in the confirmation email summary table.

## Forms in production (techservices DB)

| id | name | slug | template |
|----|------|------|----------|
| 3 | EES form | ees-form | ees |
| 4 | MES contact | mes-contact | standard |
