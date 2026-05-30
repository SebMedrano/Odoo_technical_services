# Odoo 18 Community — Dev Environment

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- [VS Code](https://code.visualstudio.com/) installed
- [Git](https://git-scm.com/) installed

## VS Code Extensions to Install

Open VS Code, go to Extensions (Ctrl+Shift+X) and install:

- **Dev Containers** — ms-vscode-remote.remote-containers
- **Python** — ms-python.python
- **XML** — redhat.vscode-xml
- **Docker** — ms-azuretools.vscode-docker

---

## First Time Setup

### 1. Start the environment

```bash
cd odoo-dev
docker compose up -d
```

Wait about 30 seconds for Odoo and PostgreSQL to initialize.

### 2. Open Odoo in the browser

Go to: http://localhost:8069

### 3. Create your development database

On the database manager screen:
- Master Password: (leave empty first time, or set one)
- Database Name: techservices
- Email: admin@example.com
- Password: admin
- Language: English
- Country: (your country)
- Demo data: NO (use `--without-demo=all` on CLI installs)

### 4. Install all custom modules (fresh install)

Use this command to install Odoo's required apps and all custom modules in one shot.
Always use a shell variable for the module list — long one-liners get mangled by SSH terminals.

```bash
MODS="sale_management,account_accountant,crm,repair,project,techservices_groups,instrument_registry,repair_timesheet,opportunity_display,billing_accounts,project_parts"
docker compose run --rm odoo odoo -d techservices -i "$MODS" --without-demo=all --stop-after-init
docker compose up -d
```

> **Note:** Use `docker compose run --rm` (not `docker exec`) — running `docker exec` while the
> container is up causes a port 8069 conflict and the install fails silently.

After the install finishes, go to Settings → Users → Administrator → Technical Services → Manager
to assign the admin role (must be done via the UI, not direct DB insert).

---

## Daily Use

### Start the environment
```bash
docker compose up -d
```

### Stop the environment
```bash
docker compose down
```

### View live Odoo logs (essential for debugging)
```bash
docker compose logs -f odoo
```

### Restart only Odoo (after config changes)
```bash
docker compose restart odoo
```

### Open a shell inside the Odoo container
```bash
docker exec -it odoo18_dev bash
```

---

## Installing / Upgrading Your Custom Modules

After editing code in the `custom_modules/` folder:

**Option A — Via the Odoo UI:**
1. Settings → Activate Developer Mode (if not already on)
2. Apps → search your module → click Upgrade

**Option B — Via command line (faster):**
```bash
docker compose run --rm odoo odoo -u your_module_name -d techservices --stop-after-init
docker compose up -d
```

Replace `your_module_name` with your actual module name (e.g. `repair_timesheet`).

> **Why `run --rm` and not `docker exec`?** Running `docker exec` against a live container
> triggers a port 8069 conflict — the upgrade command fails. `docker compose run --rm` spins up
> a separate, temporary container that exits cleanly after `--stop-after-init`.

---

## Editing Code in VS Code

Your custom modules live in `custom_modules/`. Edit them directly in VS Code —
the folder is mounted into the container so Odoo sees changes immediately after
a module upgrade. No need to rebuild the Docker image.

```
custom_modules/
    ├── repair_timesheet/       ← timesheet tab on repair orders
    │   ├── __init__.py
    │   ├── __manifest__.py
    │   ├── models/
    │   └── views/
    └── billing_accounts/       ← external account code on analytic accounts
        ├── __init__.py
        ├── __manifest__.py
        ├── models/
        └── views/
```

---

## Connecting to the Database Directly (Optional)

If you want to inspect the database with a tool like DBeaver or TablePlus:

- Host: localhost
- Port: 5432
- Database: techservices
- User: odoo
- Password: odoo_dev_password

> **On a VM:** The host likely runs a local Postgres on 5432. Remove `ports: ["5432:5432"]`
> from the `db` service in `docker-compose.yml` to avoid the conflict.

---

## Resetting the Dev Database (Nuclear Option)

If your database gets into a bad state and you want to start fresh:

```bash
docker compose down -v      # -v removes the data volumes too
docker compose up -d
```

Then go to http://localhost:8069 and create a new database.

---

## Git Workflow

```bash
# Initialize git (first time only)
git init
git add .
git commit -m "initial dev environment setup"

# Before starting new work
git checkout -b feature/repair-timesheet

# Save your work
git add custom_modules/
git commit -m "add timesheet tab to repair order"

# Merge back when working and tested
git checkout main
git merge feature/repair-timesheet
```

---

## Troubleshooting

**Odoo won't start:**
```bash
docker compose logs odoo
```
Look for the error near the bottom of the output.

**Module not showing in Apps:**
Make sure your module folder has a valid `__manifest__.py` file and the
`addons_path` in `odoo.conf` includes `/mnt/extra-addons`.

**Changes not taking effect:**
You must upgrade the module after every Python or XML change. Saving the
file alone is not enough.

**Port 8069 already in use:**
Another service is using that port. Change `"8069:8069"` to `"8070:8069"`
in docker-compose.yml and access Odoo at http://localhost:8070 instead.
