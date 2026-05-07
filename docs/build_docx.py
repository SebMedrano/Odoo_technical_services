"""
Build supervisor_workflow.docx from captured screenshots and step content.
Run: python3 build_docx.py
"""
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os, copy

SCREENSHOTS = os.path.join(os.path.dirname(__file__), "screenshots")

# ── Colours ──────────────────────────────────────────────────────────────────
PURPLE      = RGBColor(0x6B, 0x5B, 0x95)
PURPLE_DARK = RGBColor(0x4A, 0x3F, 0x72)
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GREY  = RGBColor(0xF4, 0xF6, 0xF9)
WARN_BG     = RGBColor(0xFF, 0xF8, 0xE6)
INFO_BG     = RGBColor(0xEE, 0xF4, 0xFF)
TIP_BG      = RGBColor(0xED, 0xFB, 0xF3)
GREY_TEXT   = RGBColor(0x66, 0x66, 0x66)


# ── Low-level XML helpers ─────────────────────────────────────────────────────
def set_cell_bg(cell, rgb: RGBColor):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement("w:shd")
    hex_color = str(rgb)
    shd.set(qn("w:val"),   "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"),  hex_color)
    tcPr.append(shd)


def set_run_color(run, rgb: RGBColor):
    run.font.color.rgb = rgb


def set_para_spacing(para, before=0, after=0, line=None):
    pf = para.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after  = Pt(after)
    if line:
        from docx.shared import Pt as _Pt
        pf.line_spacing = _Pt(line)


def add_horizontal_rule(doc):
    p   = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    pb  = OxmlElement("w:pBdr")
    bot = OxmlElement("w:bottom")
    bot.set(qn("w:val"),   "single")
    bot.set(qn("w:sz"),    "4")
    bot.set(qn("w:space"), "1")
    bot.set(qn("w:color"), "CCCCCC")
    pb.append(bot)
    pPr.append(pb)
    set_para_spacing(p, before=2, after=2)
    return p


# ── Reusable paragraph builders ───────────────────────────────────────────────
def add_heading(doc, text, level=1, color=PURPLE_DARK):
    h = doc.add_heading(text, level=level)
    h.style.font.color.rgb = color
    for run in h.runs:
        run.font.color.rgb = color
    set_para_spacing(h, before=14 if level == 1 else 10, after=4)
    return h


def add_body(doc, text, color=None, italic=False, bold=False):
    p   = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(10.5)
    if color:
        run.font.color.rgb = color
    run.italic = italic
    run.bold   = bold
    set_para_spacing(p, before=2, after=4)
    return p


def add_bullet(doc, text, bold_prefix=None):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.left_indent = Inches(0.3)
    p.paragraph_format.space_after  = Pt(3)
    if bold_prefix:
        r = p.add_run(bold_prefix)
        r.bold = True
        r.font.size = Pt(10.5)
        p.add_run(text).font.size = Pt(10.5)
    else:
        p.add_run(text).font.size = Pt(10.5)
    return p


def add_callout(doc, icon, title, body_text, bg: RGBColor):
    tbl = doc.add_table(rows=1, cols=2)
    tbl.style = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.LEFT
    tbl.columns[0].width = Inches(0.45)
    tbl.columns[1].width = Inches(5.85)
    icon_cell, text_cell = tbl.rows[0].cells
    set_cell_bg(icon_cell, bg)
    set_cell_bg(text_cell, bg)
    # icon
    ip = icon_cell.paragraphs[0]
    ip.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ir = ip.add_run(icon)
    ir.font.size = Pt(14)
    # text
    tp = text_cell.paragraphs[0]
    if title:
        tb = tp.add_run(f"{title}  ")
        tb.bold = True
        tb.font.size = Pt(10)
    tp.add_run(body_text).font.size = Pt(10)
    # borders: remove grid lines, keep left accent
    for cell in (icon_cell, text_cell):
        tc   = cell._tc
        tcPr = tc.get_or_add_tcPr()
        tcBdr = OxmlElement("w:tcBdr")
        for side in ("top", "bottom", "right", "left", "insideH", "insideV"):
            el = OxmlElement(f"w:{side}")
            el.set(qn("w:val"),   "none")
            el.set(qn("w:sz"),    "0")
            el.set(qn("w:space"), "0")
            el.set(qn("w:color"), "auto")
            tcBdr.append(el)
        tcPr.append(tcBdr)
    p = doc.add_paragraph()
    set_para_spacing(p, before=0, after=4)
    return tbl


def add_screenshot(doc, filename, caption):
    path = os.path.join(SCREENSHOTS, filename)
    if not os.path.exists(path):
        add_body(doc, f"[Screenshot not found: {filename}]", color=RGBColor(0xCC, 0, 0))
        return
    doc.add_picture(path, width=Inches(6.3))
    cap = doc.add_paragraph(caption)
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in cap.runs:
        run.font.size   = Pt(9)
        run.font.italic = True
        run.font.color.rgb = GREY_TEXT
    set_para_spacing(cap, before=2, after=10)


def add_two_col_table(doc, headers, rows, col_widths=None):
    n = len(headers)
    tbl = doc.add_table(rows=1 + len(rows), cols=n)
    tbl.style = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.LEFT
    # default widths
    if col_widths is None:
        w = Inches(6.3 / n)
        col_widths = [w] * n
    for i, col in enumerate(tbl.columns):
        col.width = col_widths[i]
    # header row
    hdr = tbl.rows[0]
    for i, h in enumerate(headers):
        cell = hdr.cells[i]
        set_cell_bg(cell, PURPLE)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = WHITE
        r.font.size = Pt(10)
    # data rows
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = tbl.rows[ri + 1].cells[ci]
            if ri % 2 == 1:
                set_cell_bg(cell, RGBColor(0xFA, 0xFA, 0xFA))
            p = cell.paragraphs[0]
            if isinstance(val, tuple):  # (bold_part, rest)
                rb = p.add_run(val[0])
                rb.bold = True
                rb.font.size = Pt(10)
                p.add_run(val[1]).font.size = Pt(10)
            else:
                p.add_run(val).font.size = Pt(10)
    p = doc.add_paragraph()
    set_para_spacing(p, before=0, after=6)
    return tbl


def step_divider(doc, num, title, subtitle):
    """Purple step header block."""
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.LEFT
    tbl.columns[0].width = Inches(0.55)
    tbl.columns[1].width = Inches(5.75)
    num_cell, title_cell = tbl.rows[0].cells
    set_cell_bg(num_cell,   PURPLE)
    set_cell_bg(title_cell, PURPLE)
    # number
    np_ = num_cell.paragraphs[0]
    np_.alignment = WD_ALIGN_PARAGRAPH.CENTER
    nr = np_.add_run(str(num))
    nr.bold = True
    nr.font.color.rgb = WHITE
    nr.font.size = Pt(16)
    # title
    tp = title_cell.paragraphs[0]
    tr = tp.add_run(title)
    tr.bold = True
    tr.font.color.rgb = WHITE
    tr.font.size = Pt(13)
    tp.add_run(f"\n{subtitle}").font.color.rgb = RGBColor(0xCC, 0xC4, 0xE8)
    title_cell.paragraphs[0].runs[-1].font.size = Pt(9.5)
    # remove borders
    for cell in (num_cell, title_cell):
        tc   = cell._tc
        tcPr = tc.get_or_add_tcPr()
        tcBdr = OxmlElement("w:tcBdr")
        for side in ("top", "bottom", "right", "left"):
            el = OxmlElement(f"w:{side}")
            el.set(qn("w:val"),   "none")
            el.set(qn("w:sz"),    "0")
            el.set(qn("w:space"), "0")
            el.set(qn("w:color"), "auto")
            tcBdr.append(el)
        tcPr.append(tcBdr)
    p = doc.add_paragraph()
    set_para_spacing(p, before=0, after=6)


# ═════════════════════════════════════════════════════════════════════════════
# Build document
# ═════════════════════════════════════════════════════════════════════════════
doc = Document()

# Page margins
from docx.oxml import OxmlElement as OE
section = doc.sections[0]
section.page_width    = Inches(8.5)
section.page_height   = Inches(11)
section.left_margin   = Inches(1.0)
section.right_margin  = Inches(1.0)
section.top_margin    = Inches(0.9)
section.bottom_margin = Inches(0.9)

# ── Cover / Title ─────────────────────────────────────────────────────────────
title_p = doc.add_paragraph()
title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
tr = title_p.add_run("Supervisor Workflow Guide")
tr.bold = True
tr.font.size  = Pt(26)
tr.font.color.rgb = PURPLE_DARK
set_para_spacing(title_p, before=0, after=6)

sub_p = doc.add_paragraph()
sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
sr = sub_p.add_run("MES Head · Technical Services · Odoo 18")
sr.font.size  = Pt(12)
sr.font.color.rgb = GREY_TEXT
set_para_spacing(sub_p, before=0, after=4)

date_p = doc.add_paragraph()
date_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
dr = date_p.add_run("Last updated: April 22, 2026  ·  techservices database  ·  localhost:8069")
dr.font.size  = Pt(9)
dr.font.color.rgb = GREY_TEXT
dr.italic = True
set_para_spacing(date_p, before=0, after=14)

add_horizontal_rule(doc)

# ── About ─────────────────────────────────────────────────────────────────────
add_heading(doc, "About This Guide", level=1)
add_body(doc,
    "This document walks the MES Head (Supervisor role) through the complete end-to-end "
    "workflow for a new client service request. Screenshots are taken from a live Odoo 18 instance.")

add_bullet(doc, "meshead@chem.ubc.ca", bold_prefix="Login: ")
add_bullet(doc,
    "Supervisor inherits Technician rights, plus Sales, Timesheet Approver, and Account Invoicing access.",
    bold_prefix="Role permissions: ")
add_bullet(doc,
    "A Manager must validate a worktag before an invoice can be posted.",
    bold_prefix="Worktag validation: ")

add_callout(doc, "⚠️", "Permissions note:",
    "Settings, product creation, and worktag validation are restricted to the Manager role. "
    "The Supervisor creates and manages orders; the Manager approves worktags and posts invoices.",
    WARN_BG)

add_horizontal_rule(doc)

# ── Workflow steps reference ───────────────────────────────────────────────────
add_heading(doc, "Workflow at a Glance", level=1)
add_two_col_table(doc,
    headers=["#", "Action", "Location", "Key Field / Button"],
    rows=[
        ("1", "Login as MES Head",            "/odoo/login",                 "Email: meshead@chem.ubc.ca"),
        ("2", "Open CRM Pipeline",            "CRM → Pipeline",              "Main menu grid"),
        ("3", "Create Opportunity",           "CRM → New (list view)",       "Opportunity title"),
        ("4", "Add Contact & Internal Notes", "Opportunity form",            "Contact → Create and edit… / Internal Notes tab"),
        ("5", "Create Quotation",             "Opportunity → New Quotation", "New Quotation button"),
        ("6", "Set Service Type",             "Quotation form",              "Service Type dropdown (required)"),
        ("7", "Select Worktag",               "Quotation form",              "Worktag field (auto-fills Speedchart)"),
        ("8", "Add Labor Product",            "Order Lines tab",             "Add a product → one of 4 labor products"),
        ("9", "Confirm → Sales Order",        "Quotation form",              "Confirm button"),
        ("10","Open Repair Order",            "Sales Order → Repairs button","Repairs N smart button"),
        ("11","Assign to Technician",         "Repair Order form",           "Responsible field"),
        ("12","Create Invoice Draft",         "Sales Order → Create Invoice","Create Invoice → Create Draft"),
    ],
    col_widths=[Inches(0.3), Inches(1.5), Inches(1.9), Inches(2.6)]
)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1
# ═══════════════════════════════════════════════════════════════════════════════
step_divider(doc, 1, "Log In as MES Head",
             "Navigate to Odoo and authenticate with the Supervisor account.")

add_heading(doc, "How To", level=2)
add_bullet(doc, "Go to http://localhost:8069 and select the techservices database.")
add_bullet(doc, "Enter email meshead@chem.ubc.ca and the assigned password, then click Log In.")
add_bullet(doc, "The app opens at Discuss → Inbox. The top-right corner shows MES confirming the correct account.")

add_callout(doc, "ℹ️", None,
    "The Supervisor role grants access to CRM, Sales, Repairs, Timesheets, and Invoicing. "
    "Settings and inventory product creation are restricted to the Manager role.",
    INFO_BG)

add_screenshot(doc, "01_login_dashboard.png",
    "Step 1 — Logged in as MES Head. Discuss inbox confirms correct session.")

add_horizontal_rule(doc)

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2
# ═══════════════════════════════════════════════════════════════════════════════
step_divider(doc, 2, "Open the CRM Pipeline",
             "Navigate to CRM to view and manage service opportunities.")

add_heading(doc, "How To", level=2)
add_bullet(doc, "Click the main menu grid (top-left) and open CRM, or navigate to /odoo/crm.")
add_bullet(doc, "The Kanban pipeline shows stages: New, Needs information or actions, and Won.")
add_bullet(doc, "The default filter is My Pipeline — showing only your assigned opportunities.")

add_callout(doc, "💡", "Tip:",
    "Switch to List view (icon top-right) for a faster overview when managing many opportunities at once.",
    TIP_BG)

add_screenshot(doc, "02_crm_pipeline.png",
    "Step 2 — CRM Pipeline in Kanban view showing current opportunities.")

add_horizontal_rule(doc)

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3
# ═══════════════════════════════════════════════════════════════════════════════
step_divider(doc, 3, "Create a New Opportunity, Add Contact & Internal Notes",
             "Open the full form, create a new client contact, and record intake details.")

add_heading(doc, "New Opportunity", level=2)
add_bullet(doc, "Switch to List view and click New (top-left) to open the full opportunity form.")
add_bullet(doc, 'Enter a descriptive title (e.g. “Instrument Calibration & Repair Request”).')
add_bullet(doc, "The Salesperson is auto-set to MES Head.")

add_heading(doc, "Add a New Contact", level=2)
add_bullet(doc, "Click the Contact field and type the new client's name.")
add_bullet(doc, "Select Create and edit… from the dropdown to open the contact dialog.")
add_bullet(doc, "Select Individual, fill in Name, Phone, and Email, then click Save & Close.")
add_bullet(doc, "The contact's email and phone populate back on the opportunity form.")

add_screenshot(doc, "03_create_contact_dialog.png",
    "Step 3a — Creating a new Individual contact with phone and email from within the opportunity.")

add_heading(doc, "Add Internal Notes", level=2)
add_bullet(doc, "Click the Internal Notes tab on the opportunity form.")
add_bullet(doc, "Type your intake notes — instrument details, priority, timeline, pre-authorised spend.")
add_bullet(doc, "Click the cloud save icon in the breadcrumb to save.")

add_callout(doc, "⚠️", "Internal Notes are private:",
    "Visible only to Odoo users, not to the client. Use the Send message button for client-facing communication.",
    WARN_BG)

add_screenshot(doc, "04_opportunity_with_notes.png",
    "Step 3b — Opportunity form with new contact (Dr. Sarah Mitchell) and internal intake notes.")

add_horizontal_rule(doc)

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4
# ═══════════════════════════════════════════════════════════════════════════════
step_divider(doc, 4, "Create a Quotation",
             "Generate a quotation directly from the opportunity.")

add_heading(doc, "How To", level=2)
add_bullet(doc, "From the saved opportunity, click New Quotation in the action bar.")
add_bullet(doc, "The quotation opens pre-filled with the customer and opportunity name.")
add_bullet(doc, "The Expiration date defaults to 30 days out.")

add_screenshot(doc, "05_new_quotation.png",
    "Step 4 — New Quotation form. Service Type is required (highlighted in red if missing).")

add_horizontal_rule(doc)

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 5
# ═══════════════════════════════════════════════════════════════════════════════
step_divider(doc, 5, "Add Service Type, Worktag & Labor Product",
             "Classify the service, select the billing worktag, and add the labor line.")

add_heading(doc, "Service Type (required)", level=2)
add_body(doc, "Click the Service Type dropdown and choose the appropriate category:")

add_two_col_table(doc,
    headers=["Option", "When to use"],
    rows=[
        ("Repair",        "Fixing or restoring a faulty instrument"),
        ("Manufacturing", "Building or fabricating a component"),
        ("Move",          "Relocating equipment between labs"),
        ("Installation",  "Setting up new equipment on-site"),
        ("Maintenance",   "Scheduled preventive maintenance"),
    ],
    col_widths=[Inches(1.6), Inches(4.7)]
)

add_heading(doc, "Worktag", level=2)
add_bullet(doc, "Click the Worktag field and type the code (e.g. CALREP-2026-001).")
add_bullet(doc, "Worktags are filtered to those linked to the customer's commercial partner.")
add_bullet(doc, "When selected, the Speedchart field auto-populates from the worktag record.")
add_bullet(doc, "Worktags must be validated by a Manager before an invoice can be posted.")

add_callout(doc, "ℹ️", "No worktags showing?",
    "The worktag's Company field must match the customer's commercial partner. "
    "Ask the Manager to create the worktag if none exist.",
    INFO_BG)

add_heading(doc, "Labor Product (Order Lines)", level=2)
add_body(doc, "Click Add a product and select the labor product matching the client's category:")

add_two_col_table(doc,
    headers=["Product", "Client Category"],
    rows=[
        ("Work order / repair order for Chemistry client – Labor",                 "UBC Chemistry department"),
        ("Work order / repair order for UBC (external) client – Labor",            "Other UBC departments"),
        ("Work order / repair order for External to UBC or private client – Labor","Non-UBC / private clients"),
        ("Work order / repair order for Departmental service client – Labor",      "Internal MES department service"),
    ],
    col_widths=[Inches(3.8), Inches(2.5)]
)

add_screenshot(doc, "06_quotation_with_service_worktag.png",
    "Step 5 — Quotation complete: Service Type = Repair, Worktag = CALREP-2026-001, "
    "Speedchart auto-filled, labor product added with 12% GST+PST BC tax.")

add_horizontal_rule(doc)

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 6
# ═══════════════════════════════════════════════════════════════════════════════
step_divider(doc, 6, "Confirm Quotation → Sales Order",
             "Lock in pricing and generate the sale order and linked repair order.")

add_heading(doc, "How To", level=2)
add_bullet(doc, "Review all fields, then click Confirm in the action bar.")
add_bullet(doc, "The status bar moves to Sales Order and the record gets a number (e.g. S00081).")
add_bullet(doc, "A Repairs smart button appears — the system auto-creates a linked repair order.")

add_callout(doc, "💡", "Tip:",
    "Once confirmed, pricing is locked. To make changes, cancel and recreate, "
    "or use Lock/Unlock controls (visible to managers).",
    TIP_BG)

add_screenshot(doc, "07_sales_order_confirmed.png",
    "Step 6 — Sales Order S00081 confirmed. The Repairs smart button shows 1 linked repair order.")

add_horizontal_rule(doc)

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 7
# ═══════════════════════════════════════════════════════════════════════════════
step_divider(doc, 7, "Open the Repair / Work Order",
             "Access the auto-created repair order and review its details.")

add_heading(doc, "How To", level=2)
add_bullet(doc, "From the confirmed sales order, click the Repairs smart button (top bar).")
add_bullet(doc, "The repair order opens pre-filled with customer, opportunity, service type, and scheduled date.")
add_bullet(doc, "Stage bar: New → Confirmed → Under Repair → Repaired. New repair orders land in Confirmed.")
add_bullet(doc, "The Parts tab is where technicians add physical components used during the repair.")
add_bullet(doc, "The Timesheets tab records labour hours against this order.")

add_screenshot(doc, "08_repair_order.png",
    "Step 7 — Repair Order WH/RO/00057 in Confirmed state, linked to Sale Order S00081.")

add_horizontal_rule(doc)

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 8
# ═══════════════════════════════════════════════════════════════════════════════
step_divider(doc, 8, "Assign the Repair Order to a Technician",
             "Change the Responsible field to the staff member who will carry out the work.")

add_heading(doc, "How To", level=2)
add_bullet(doc, "Click the Responsible field (right column of the repair order header).")
add_bullet(doc, "Clear the current value and type the technician's name (e.g. Tech 1).")
add_bullet(doc, "Select the correct user from the dropdown and save using the cloud save icon.")

add_callout(doc, "💡", "Tip:",
    "The assigned technician will see this repair order in their own queue. "
    "They can log timesheet entries directly from the repair order's Timesheets tab.",
    TIP_BG)

add_screenshot(doc, "09_repair_assigned_to_staff.png",
    "Step 8 — Repair order WH/RO/00057 assigned to Tech 1.")

add_horizontal_rule(doc)

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 9
# ═══════════════════════════════════════════════════════════════════════════════
step_divider(doc, 9, "Create Invoice Draft",
             "Return to the sales order and generate a draft invoice for Manager review.")

add_heading(doc, "Pre-requisite: Worktag Validation", level=2)
add_callout(doc, "⚠️", "Manager action required:",
    "A Manager must check the Validated field on the worktag before this step succeeds. "
    "Otherwise Odoo blocks invoice creation: "
    "\"worktag has not been validated — a manager must check the Validated field on the worktag first.\"",
    WARN_BG)

add_heading(doc, "How To", level=2)
add_bullet(doc, "Click the breadcrumb sales order link or use the Sale Orders smart button to return to S00081.")
add_bullet(doc, "Click Create Invoice (top-left action bar).")
add_bullet(doc, "The dialog defaults to Regular invoice — leave this selected.")
add_bullet(doc, "Click Create Draft.")
add_bullet(doc, "The draft invoice opens with all lines, taxes, worktag, and customer details pre-populated.")

add_screenshot(doc, "10_create_invoice_dialog.png",
    "Step 9a — Create Invoice(s) dialog. Select Regular invoice and click Create Draft.")

add_screenshot(doc, "11_invoice_draft.png",
    "Step 9b — Draft Customer Invoice. Shows labor line at $100 + 12% GST/PST BC. "
    "Ready for Manager review and posting.")

add_heading(doc, "What Happens Next", level=2)
add_bullet(doc, "The Supervisor's job ends here — the draft sits in Accounting → Customer Invoices with status Draft.")
add_bullet(doc, "A Manager reviews and clicks Confirm to post the invoice and generate journal entries.")
add_bullet(doc, "Once posted, the invoice can be emailed to the client directly from Odoo.")

# ── Save ──────────────────────────────────────────────────────────────────────
out = os.path.join(os.path.dirname(__file__), "supervisor_workflow.docx")
doc.save(out)
print(f"Saved: {out}")
