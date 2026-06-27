---
name: techservices_groups module
description: Custom roles, menu restrictions, product form customizations, and contact type extension built in techservices_groups
type: project
originSessionId: db77456c-e97a-4cd2-a596-93edc0415bfe
---
Custom module at `custom_modules/techservices_groups`. Key things built:

**Roles** (security/techservices_groups.xml):
- Technician → implies stock.group_stock_user + hr_timesheet user
- Supervisor → implies Technician + sales salesman + timesheet approver + account invoicing
- Manager → implies Supervisor + stock manager + timesheet manager + account manager + base.group_system

**Inventory menu restrictions** (views/inventory_menu_restrictions.xml):
- Technician/Supervisor see only Inventory → Products section
- Overview, Operations, Reporting, Configuration restricted to `techservices_groups.group_manager`
- Uses our own Manager group, NOT stock.group_stock_manager

**Product form restrictions** (views/product_form_restrictions.xml):
- Hidden from Technician/Supervisor via `groups="techservices_groups.group_manager"`:
  - Purchase checkbox, Invoicing Policy, Create Repair, Reference, Barcode
  - Forecasted, Reordering Rules (×2), In/Out smart buttons
  - Replenish header button (via `_get_view` using `env.ref('stock.action_product_replenishment')`)
  - Print Labels button
- Spans across 5 separate inherited views (product, account, sale, repair, stock)

**Product form new fields** (models/product_template.py + views/product_template_fields.xml):
- `x_make` (Char) — brand/manufacturer
- `x_make_part_number` (Char) — manufacturer's own part number (below x_make)
- `x_supplier_id` (Many2one → res.partner, domain: is_supplier=True, context sets default_is_supplier+default_is_company) — primary supplier
- `x_supplier_part_number` (Char) — vendor part code; followed by hint text "Add any additional suppliers in the internal notes section"
- Placed in group_general after the type field, visible to all roles
- Also searchable in product list and repair catalog search views

**Supplier contact type** (models/res_partner.py):
- Added `is_supplier = fields.Boolean(store=True)` to res.partner
- Extended `company_type` selection with `('supplier', 'Supplier')` third option
- Overrode `_compute_company_type`, `_write_company_type`, `onchange_company_type`
- Supplier contacts have is_company=True + is_supplier=True

**Supplier visibility** (views/res_partner_views.xml + static/src/company_type_field.js):
- 'Supplier' radio option HIDDEN from the Contacts form via a custom OWL widget `company_type_no_supplier`
  - Widget shows 'supplier' option only when the record is already a supplier (for display on existing records)
  - Applied via view inherit on `base.view_partner_form` using `widget="company_type_no_supplier"`
- Suppliers EXCLUDED from the main Contacts list via domain override on `contacts.action_contacts`
- Suppliers accessible at **Inventory → Products → Suppliers** (action: `action_inventory_suppliers`, parent menu: `stock.menu_stock_inventory_control`)
  - Domain: `[('is_supplier', '=', True)]`; context defaults `is_supplier=True, is_company=True` for new records

**Why:** `ondelete` for selection_add must be a lambda (not 'set default') when the base field has no default.
**How to apply:** When restricting menus, always use our custom group not stock groups. The contacts module XML ID for the main action is `contacts.action_contacts` (not `base.action_contacts`). The Inventory Products parent menu is `stock.menu_stock_inventory_control` (not `stock.menu_product_nav`).
