---
name: techservices_groups module
description: Custom roles, menu restrictions, product form customizations, and contact type extension built in techservices_groups
type: project
originSessionId: f1bbee57-f287-4117-a9dd-f7854f24a3c1
---
Custom module at `custom_modules/techservices_groups`. Key things built:

**Roles** (security/techservices_groups.xml):
- Technician → implies stock.group_stock_user + hr_timesheet user
- Supervisor → implies Technician + sales salesman + timesheet approver + account invoicing
- Manager → implies Supervisor + stock manager + timesheet manager + account manager + base.group_system

**Inventory menu restrictions** (views/inventory_menu_restrictions.xml):
- Technician/Supervisor see only Inventory → Products section
- Overview, Operations, Reporting, Configuration restricted to `techservices_groups.group_manager`
- Uses our own Manager group, NOT stock.group_stock_manager (learned: stock group can be directly assigned to users independently)

**Product form restrictions** (views/product_form_restrictions.xml):
- Hidden from Technician/Supervisor via `groups="techservices_groups.group_manager"`:
  - Purchase checkbox, Invoicing Policy, Create Repair, Reference, Barcode
  - Forecasted, Reordering Rules (×2), In/Out smart buttons
  - Replenish header button (targeted by numeric action ID 428, not string)
  - Print Labels button
- Spans across 5 separate inherited views (product, account, sale, repair, stock)

**Product form new fields** (models/product_template.py + views/product_template_fields.xml):
- `x_make` (Char) — brand/manufacturer
- `x_supplier_id` (Many2one → res.partner, domain: is_supplier=True) — filtered to Supplier contacts only
- `x_supplier_part_number` (Char) — vendor part code
- Placed in group_general after the type field, visible to all roles

**Supplier contact type** (models/res_partner.py):
- Added `is_supplier = fields.Boolean(store=True)` to res.partner
- Extended `company_type` selection with `('supplier', 'Supplier')` third option
- Overrode `_compute_company_type`, `_write_company_type`, `onchange_company_type`
- Supplier contacts have is_company=True + is_supplier=True
- Radio button on contact form shows automatically (no view changes needed)

**Why:** `ondelete` for selection_add must be a lambda (not 'set default') when the base field has no default.
**How to apply:** When restricting menus, always use our custom group not stock groups — users can be manually assigned to stock groups independently of our role hierarchy.
