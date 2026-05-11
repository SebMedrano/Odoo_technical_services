---
name: Odoo Dev Environment
description: Key facts about the local Odoo development setup at ~/Documents/Developer/odoo-dev
type: project
originSessionId: 36785d4c-7291-4fc6-a025-f92af3be6ee8
---
Docker Compose project at `/Users/sebastianmedrano/Documents/Developer/odoo-dev`. Two containers: `odoo18_dev` (Odoo 18.0) and `odoo18_db` (Postgres 15). Runs on `localhost:8069`.

**Why:** Active Odoo customization project with custom modules.

**How to apply:** Always use `-d techservices` (not `-d odoo`) for all `odoo -u/-i` commands. The live database is `techservices`. Custom modules live in `custom_modules/` which is mounted at `/mnt/extra-addons` inside the container.

After every module upgrade, restart the container:
```
docker compose exec odoo odoo -u <module> --stop-after-init -d techservices
docker compose restart odoo
```
