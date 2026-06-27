---
name: odoo-deployment-to-ubuntu-vm
description: Lessons learned deploying the Odoo stack to an Ubuntu VM via Docker Compose
metadata: 
  node_type: memory
  type: project
  originSessionId: db77456c-e97a-4cd2-a596-93edc0415bfe
---

Deployment target: Ubuntu VM at `137.82.146.143`, user `sebastian`, accessed via SSH. Docker Compose setup mirrors local dev. Custom modules at `/home/sebastian/odoo_technical_services/custom_modules/`.

**Deploy command (local → VM):**
```bash
rsync -avz --delete \
    /Users/smedrano/Documents/Odoo_technical_services/custom_modules/ \
    sebastian@137.82.146.143:/home/sebastian/odoo_technical_services/custom_modules/
```
Then SSH in and upgrade modules (see below).

---

## Pre-deploy safety checklist

Run these BEFORE every deploy to production:

**1. Tag the current commit locally:**
```bash
git tag -a v<date> -m "pre-deploy <date>"
git push origin --tags
```

**2. Dump the production DB (on the VM):**
```bash
BACKUP="techservices_$(date +%Y%m%d_%H%M%S).sql"
docker compose exec db pg_dump -U odoo techservices > ~/backups/$BACKUP
echo "Backup saved: $BACKUP"
```

## Rollback procedure

**Code only (module broke but DB is fine):**
```bash
# Locally: checkout the tag and rsync back
git checkout <tag>
rsync -avz --delete \
    /Users/smedrano/Documents/Odoo_technical_services/custom_modules/ \
    sebastian@137.82.146.143:/home/sebastian/odoo_technical_services/custom_modules/
# Then downgrade modules on the VM
```

**Code + data (upgrade corrupted data):**
```bash
# On the VM:
docker compose stop odoo
docker compose exec db psql -U odoo -c "DROP DATABASE techservices;"
docker compose exec db psql -U odoo -c "CREATE DATABASE techservices;"
docker compose exec db psql -U odoo techservices < ~/backups/<backup_file>.sql
docker compose start odoo
```

---

## Module upgrade (on the VM after rsync)

```bash
MODS="techservices_groups,website_lead_forms"
docker compose run --rm odoo odoo -u "$MODS" --stop-after-init -d techservices
docker compose restart odoo
```

## Fresh install command
```bash
MODS="sale_management,account_accountant,crm,repair,project,techservices_groups,instrument_registry,repair_timesheet,opportunity_display,billing_accounts,project_parts"
docker compose run --rm odoo odoo -d techservices -i "$MODS" --without-demo=all --stop-after-init
docker compose up -d
```
Always use a variable for the module list — long one-liners get mangled by the SSH terminal.

**Always include `--without-demo=all`** — otherwise Odoo loads demo data on fresh installs.

**odoo.conf settings for production:**
- `dev_mode =` (empty — remove dev_mode entirely)
- `dbfilter = techservices`
- `list_db = False`

**Port conflicts:**
- VM likely has a local Postgres on 5432 — remove `ports: ["5432:5432"]` from db service in docker-compose.yml.
- Never use `docker compose exec odoo odoo -i ...` while the container is running — use `docker compose run --rm` instead to avoid port 8069 conflict.

**After fresh install — assign admin role:**
- Go to Settings → Users → Administrator → Technical Services → Manager.
- Must do this via ORM (UI), not direct DB insert — direct insert skips implied group propagation.

**Replenish button (product form):**
- Fixed via `_get_view` override using `env.ref('stock.action_product_replenishment')` to resolve the ID at runtime.

**Missing sequence file:**
- `instrument_registry` needs `data/ir_sequence_data.xml` with `ir.sequence` code `service.instrument` (prefix `INST/`, padding 5).
