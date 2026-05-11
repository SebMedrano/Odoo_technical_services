---
name: instrument_registry module
description: State and structure of the instrument_registry custom Odoo module
type: project
originSessionId: 36785d4c-7291-4fc6-a025-f92af3be6ee8
---
Custom Odoo 18 module at `custom_modules/instrument_registry`. Tracks instruments/equipment for repair operations.

**Models:** `service.instrument`, `service.instrument.type`, `service.building`, `repair.order` (inherited), `instrument.document` (inherits `ir.attachment` via `_inherits`)

**instrument.document fields:** `ir_attachment_id`, `instrument_id`, `description` (Char), `active`, `sequence` — plus all `ir.attachment` fields via delegation (`name`, `datas`, `create_uid`, `create_date`, `file_size`, etc.)

**Documents view:** List (Name, Description, Type, Size, Uploaded On, Uploaded By) + Form (Document Name, Description, Instrument, File upload). Views explicitly pinned in `action_open_documents()` via `env.ref()` to avoid falling back to the default `ir.attachment` form.

**Known gaps remaining:** `_compute_display_name()` missing `@api.depends`, no duplicate serial number constraint, no multi-stage workflow, no tests.
