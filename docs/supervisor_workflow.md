# Supervisor Workflow Guide
**MES Head · Technical Services · Odoo 18**  
Last updated: July 25, 2026 · `techservices` database · localhost:8069

---

## About This Guide

This document walks the MES Head (Supervisor role) through the complete end-to-end workflow for a new client service request.

**Login:** your chem email

---

## Workflow at a Glance

| # | Action | Location | Key Field / Button |
|---|--------|----------|--------------------|
| 1 | Login as MES Head | `/odoo/login` | Email: your email |
| 2 | Open CRM Pipeline | CRM → Pipeline | Main menu grid |
| 3 | Create Opportunity | CRM → New (list view) | Opportunity title |
| 4 | Add Contact & Internal Notes | Opportunity form | Contact → Create and edit… / Internal Notes tab |
| 5 | Create Quotation | Opportunity → New Quotation | New Quotation button |
| 6 | Set Service Type | Quotation form | Service Type dropdown (required) |
| 7 | Select Worktag | Quotation form | Worktag field (auto-fills Speedchart) |
| 8 | Add Labor Product | Order Lines tab | Add a product → one of 4 labor products |
| 9 | Confirm → Sales Order | Quotation form | Confirm button |
| 10 | Open Repair Order | Sales Order → Repairs button | Repairs N smart button |
| 11 | Assign to Technician | Repair Order form | Responsible field |
| 12 | Create Invoice Draft | Sales Order → Create Invoice | Create Invoice → Create Draft |

---

## Step 1 — Log In as MES Head

Navigate to Odoo and authenticate with the Supervisor account.

**How To**

1. Go to `http://137.82.146.143:8069` and select the `techservices` database.
2. Enter your email and the assigned password, then click **Log In**.
3. The app opens at Discuss → Inbox. The top-right corner shows **MES** confirming the correct account.

> **ℹ️ Note:** The Supervisor role grants access to CRM, Sales, Repairs, Timesheets, and Invoicing. Settings and inventory product creation are restricted to the Manager role.  
> The Supervisor **cannot** see the Cost, Purchase Taxes, Sales, Inventory, or Billing tabs on product forms — these are restricted to the Manager role.

---

`[SCREENSHOT PLACEHOLDER — Step 1: Logged in as MES Head. Discuss inbox confirms correct session.]`

---

## Step 2 — Open the CRM Pipeline

Navigate to CRM to view and manage service opportunities.

**How To**

1. Click the main menu grid (top-left) and open **CRM**, or navigate to `/odoo/crm`.
2. The Kanban pipeline shows stages: **New**, **Needs information or actions**, and **Won**.
3. The default filter is **My Pipeline** — showing only your assigned opportunities.

> **💡 Tip:** Switch to List view (icon top-right) for a faster overview when managing many opportunities at once.

---

`[SCREENSHOT PLACEHOLDER — Step 2: CRM Pipeline in Kanban view showing current opportunities.]`

---

## Step 3 — Create a New Opportunity, Add Contact & Internal Notes

Open the full form, create a new client contact, and record intake details.

### New Opportunity

1. Switch to **List view** and click **New** (top-left) to open the full opportunity form.
2. Enter a descriptive title (e.g. "Instrument Calibration & Repair Request").
3. The **Salesperson** is auto-set to MES Head. The dropdown only shows users belonging to the same company.

### Add a New Contact

1. Click the **Contact** field and type the new client's name.
2. Select **Create and edit…** from the dropdown to open the contact dialog.
3. Select **Individual**, fill in Name, Phone, and Email, then click **Save & Close**.
4. The contact's email and phone populate back on the opportunity form.

---

`[SCREENSHOT PLACEHOLDER — Step 3a: Creating a new Individual contact with phone and email from within the opportunity.]`

### Add Internal Notes

1. Click the **Internal Notes** tab on the opportunity form.
2. Type your intake notes — instrument details, priority, timeline, pre-authorised spend.
3. Click the cloud save icon in the breadcrumb to save.

> **⚠️ Important:** Internal Notes are private — visible only to Odoo users, not to the client. Use the **Send message** button for client-facing communication.

---

`[SCREENSHOT PLACEHOLDER — Step 3b: Opportunity form with new contact and internal intake notes.]`

---

## Step 4 — Create a Quotation

Generate a quotation directly from the opportunity.

**How To**

1. From the saved opportunity, click **New Quotation** in the action bar.
2. The quotation opens pre-filled with the customer and opportunity name.
3. The Expiration date defaults to 30 days out.

---

`[SCREENSHOT PLACEHOLDER — Step 4: New Quotation form. Service Type is required (highlighted in red if missing).]`

---

## Step 5 — Add Service Type, Worktag & Labor Product

Classify the service, select the billing worktag, and add the labor line.

### Service Type (required)

Click the **Service Type** dropdown and choose the appropriate category:

| Option | When to use |
|--------|-------------|
| Repair | Fixing or restoring a faulty instrument |
| Manufacturing | Building or fabricating a component |
| Move | Relocating equipment between labs |
| Installation | Setting up new equipment on-site |
| Maintenance | Scheduled preventive maintenance |

### Worktag

1. Click the **Worktag** field and type the code (e.g. `CALREP-2026-001`).
2. Worktags are filtered to those linked to the customer's commercial partner.
3. When selected, the **Speedchart** field auto-populates from the worktag record.
4. Worktags must be **validated** by a Manager before an invoice can be posted.

> **ℹ️ No worktags showing?** A worktag must be linked to the client's company via its **Companies** field (a worktag can belong to multiple companies). Ask the Manager to create the worktag or link it to the correct company if none appear. See [Managing Worktags on a Company Contact](#managing-worktags-on-a-company-contact) below.

### Labor Product (Order Lines)

Click **Add a product** and select the labor product matching the client's category:

| Product | Client Category |
|---------|----------------|
| Work order / repair order for Chemistry client – Labor | UBC Chemistry department |
| Work order / repair order for UBC (external) client – Labor | Other UBC departments |
| Work order / repair order for External to UBC or private client – Labor | Non-UBC / private clients |
| Work order / repair order for Departmental service client – Labor | Internal MES department service |

---

`[SCREENSHOT PLACEHOLDER — Step 5: Quotation complete: Service Type = Repair, Worktag selected, Speedchart auto-filled, labor product added with 12% GST+PST BC tax.]`

---

## Step 6 — Confirm Quotation → Sales Order

Lock in pricing and generate the sale order and linked repair order.

**How To**

1. Review all fields, then click **Confirm** in the action bar.
2. The status bar moves to **Sales Order** and the record gets a number (e.g. `S00081`).
3. A **Repairs** smart button appears — the system auto-creates a linked repair order.

> **💡 Tip:** Once confirmed, pricing is locked. To make changes, cancel and recreate, or use Lock/Unlock controls (visible to managers).

---

`[SCREENSHOT PLACEHOLDER — Step 6: Sales Order confirmed. The Repairs smart button shows 1 linked repair order.]`

---

## Step 7 — Open the Repair / Work Order

Access the auto-created repair order and review its details.

**How To**

1. From the confirmed sales order, click the **Repairs** smart button (top bar).
2. The repair order opens pre-filled with customer, opportunity, service type, and scheduled date.
3. Stage bar: **New → Confirmed → Under Repair → Repaired**. New repair orders land in **Confirmed**.
4. The **Parts** tab is where technicians add physical components used during the repair.
5. The **Timesheets** tab records labour hours against this order.

> **⚠️ Blocked repairs:** If a technician sets a repair to **Blocked** (e.g. waiting for parts or client information), a yellow warning banner appears at the top of the form explaining the reason. A blocked repair cannot progress until the issue is resolved. The technician is required to log a note explaining the reason for the block.

---

`[SCREENSHOT PLACEHOLDER — Step 7: Repair Order in Confirmed state, linked to the Sale Order.]`

`[SCREENSHOT PLACEHOLDER — Step 7b: Repair Order in Blocked state showing the yellow warning banner.]`

---

## Step 8 — Assign the Repair Order to a Technician

Change the **Responsible** field to the staff member who will carry out the work.

**How To**

1. Click the **Responsible** field (right column of the repair order header).
2. Clear the current value and type the technician's name (e.g. Tech 1). The dropdown only shows users belonging to the same company.
3. Select the correct user from the dropdown and save using the cloud save icon.

> **💡 Tip:** The assigned technician will see this repair order in their own queue. They can log timesheet entries directly from the repair order's **Timesheets** tab.

---

`[SCREENSHOT PLACEHOLDER — Step 8: Repair order assigned to a technician.]`

---

## Step 9 — Create Invoice Draft

Return to the sales order and generate a draft invoice for Manager review.

### Pre-requisite: Worktag Validation

> **⚠️ Manager action required:** A Manager must check the **Validated** field on the worktag before this step succeeds. Otherwise Odoo blocks invoice creation with the message: *"worktag has not been validated — a manager must check the Validated field on the worktag first."*

**How To**

1. Click the breadcrumb sales order link or use the **Sale Orders** smart button to return to the sales order.
2. Click **Create Invoice** (top-left action bar).
3. The dialog defaults to **Regular invoice** — leave this selected.
4. Click **Create Draft**.
5. The draft invoice opens with all lines, taxes, worktag, and customer details pre-populated.

---

`[SCREENSHOT PLACEHOLDER — Step 9a: Create Invoice(s) dialog. Select Regular invoice and click Create Draft.]`

`[SCREENSHOT PLACEHOLDER — Step 9b: Draft Customer Invoice with labor line, taxes, and worktag. Ready for Manager review and posting.]`

### What Happens Next

- The Supervisor's job ends here — the draft sits in **Accounting → Customer Invoices** with status **Draft**.
- A Manager reviews and clicks **Confirm** to post the invoice and generate journal entries.
- Once posted, the invoice can be emailed to the client directly from Odoo.

---

## Managing Worktags on a Company Contact

Worktags are master records shared across companies. A single worktag (e.g. a cost centre code) can be linked to multiple client companies.

### Viewing a Company's Worktags

1. Go to **Contacts** and open a company record.
2. Click the **Worktags** tab.
3. All worktags currently linked to this company are listed with their code, name, cost centre, speedchart, category, status, and validation state.

---

`[SCREENSHOT PLACEHOLDER — Contacts: Worktags tab on a company record showing linked worktags.]`

### Adding an Existing Worktag to a Company

1. On the **Worktags** tab, click **Add**.
2. A search dialog opens — type the worktag code.
3. Select the matching worktag from the results. All its fields (name, cost centre, speedchart, category, status) auto-populate in the row.
4. Save the record.

> **ℹ️ Note:** Worktag details (code, cost centre, etc.) are managed centrally from **Accounting → Configuration → Worktags**. Editing them from the contact form affects all companies they are linked to.

---

`[SCREENSHOT PLACEHOLDER — Contacts: Adding an existing worktag by code — details auto-populate on selection.]`

### Creating a New Worktag

New worktags should be created by a Manager from **Accounting → Configuration → Worktags** to ensure all required fields (including **Validated**) are properly set before the worktag is used on a sale order.

---

## Product Catalogue — What the Supervisor Can See

When browsing inventory products (Inventory → Products), the Supervisor view is intentionally restricted:

### Product List View

The table shows these columns by default (additional optional columns can be toggled via the column chooser):

| Column | Notes |
|--------|-------|
| Product Name | Always visible |
| Product's description | Optional — visible by default |
| Make | Optional — visible by default |
| Make Part Number | Optional — visible by default |
| Supplier | Optional — visible by default |
| Supplier Part Number | Optional — visible by default |
| Sales Price | Always visible |
| Unit of Measure | Always visible |
| Date Added | Optional — visible by default |

### Product Form View

Fields visible to the Supervisor on the General Information tab:

- Product's description
- Make / Make Part Number
- Supplier / Supplier Part Number
- Alternative Supplier / Alternative Supplier Part Number
- Room Location / Drawer Location

> **⚠️ Restricted fields:** The Supervisor **cannot** see Cost (standard price), Purchase Taxes, Product Type radio button, or the Sales, Inventory, and Billing tabs. These are visible only to Managers.

---

`[SCREENSHOT PLACEHOLDER — Product form as seen by the Supervisor role, showing available fields and hidden tabs.]`
