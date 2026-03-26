# Custom Modules

Place your custom Odoo modules here. Each module is a folder with this structure:

```
my_module/
    ├── __init__.py          # Python package marker + imports
    ├── __manifest__.py      # Module metadata and dependencies
    ├── models/
    │   ├── __init__.py
    │   └── my_model.py      # Python model definitions
    ├── views/
    │   └── my_views.xml     # Form, list, and menu views
    ├── security/
    │   ├── ir.model.access.csv   # Access rights
    │   └── security.xml          # Record rules (optional)
    └── data/
        └── data.xml         # Default data loaded on install (optional)
```

## Modules Planned for This Project

- **repair_timesheet** — Adds a timesheet tab to Repair Orders
- **billing_accounts** — Adds external account code to Analytic Accounts

This folder is mounted into the Odoo container. Odoo reads modules
directly from here — no rebuilding required after code edits.
