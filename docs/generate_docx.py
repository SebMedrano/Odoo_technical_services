"""Generate supervisor_workflow.docx from the Markdown source."""
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

doc = Document()

# ── Page margins ────────────────────────────────────────────────────────────
section = doc.sections[0]
section.page_width  = Inches(8.5)
section.page_height = Inches(11)
section.left_margin   = Inches(1)
section.right_margin  = Inches(1)
section.top_margin    = Inches(1)
section.bottom_margin = Inches(1)

# ── Colour palette ───────────────────────────────────────────────────────────
C_DARK   = RGBColor(0x2C, 0x3E, 0x50)   # headers / title
C_ACCENT = RGBColor(0x27, 0x6B, 0xBD)   # step number badges
C_LIGHT  = RGBColor(0xEC, 0xF0, 0xF1)   # table header bg
C_INFO   = RGBColor(0xD6, 0xEA, 0xF8)   # info box bg
C_WARN   = RGBColor(0xFE, 0xF9, 0xE7)   # warning box bg
C_TIP    = RGBColor(0xE9, 0xF7, 0xEF)   # tip box bg
C_MUTED  = RGBColor(0x7F, 0x8C, 0x8D)   # placeholder text
C_WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
C_BLACK  = RGBColor(0x00, 0x00, 0x00)
C_RED    = RGBColor(0xC0, 0x39, 0x2B)

# ── Helpers ──────────────────────────────────────────────────────────────────

def set_cell_bg(cell, rgb: RGBColor):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement('w:shd')
    hex_color = f"{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  hex_color)
    tcPr.append(shd)


def set_para_border(para, side='left', color='276BBD', space='6', sz='24'):
    """Add a coloured left border to a paragraph (for callout boxes)."""
    pPr  = para._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bd   = OxmlElement(f'w:{side}')
    bd.set(qn('w:val'),   'single')
    bd.set(qn('w:sz'),    sz)
    bd.set(qn('w:space'), space)
    bd.set(qn('w:color'), color)
    pBdr.append(bd)
    pPr.append(pBdr)


def set_para_shading(para, fill_hex: str):
    pPr = para._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  fill_hex)
    pPr.append(shd)


def hr(doc):
    """Thin horizontal rule."""
    p   = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bot  = OxmlElement('w:bottom')
    bot.set(qn('w:val'),   'single')
    bot.set(qn('w:sz'),    '4')
    bot.set(qn('w:space'), '1')
    bot.set(qn('w:color'), 'CCCCCC')
    pBdr.append(bot)
    pPr.append(pBdr)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after  = Pt(4)


def heading1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after  = Pt(4)
    run = p.add_run(text)
    run.bold      = True
    run.font.size = Pt(16)
    run.font.color.rgb = C_DARK
    hr(doc)
    return p


def heading2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after  = Pt(2)
    run = p.add_run(text)
    run.bold      = True
    run.font.size = Pt(13)
    run.font.color.rgb = C_ACCENT
    return p


def heading3(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after  = Pt(2)
    run = p.add_run(text)
    run.bold      = True
    run.font.size = Pt(11)
    run.font.color.rgb = C_DARK
    return p


def body(doc, text, bold_parts=None, space_after=Pt(4)):
    """Plain body paragraph. bold_parts is a list of substrings to bold."""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = space_after
    if bold_parts:
        remaining = text
        for bp in bold_parts:
            idx = remaining.find(bp)
            if idx == -1:
                continue
            if idx > 0:
                r = p.add_run(remaining[:idx])
                r.font.size = Pt(10.5)
            r = p.add_run(bp)
            r.bold = True
            r.font.size = Pt(10.5)
            remaining = remaining[idx + len(bp):]
        if remaining:
            r = p.add_run(remaining)
            r.font.size = Pt(10.5)
    else:
        run = p.add_run(text)
        run.font.size = Pt(10.5)
    return p


def bullet(doc, text, level=0, bold_parts=None):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.left_indent   = Inches(0.25 + 0.2 * level)
    p.paragraph_format.space_after   = Pt(2)
    p.paragraph_format.space_before  = Pt(1)
    if bold_parts:
        remaining = text
        for bp in bold_parts:
            idx = remaining.find(bp)
            if idx == -1:
                continue
            if idx > 0:
                r = p.add_run(remaining[:idx])
                r.font.size = Pt(10.5)
            r = p.add_run(bp)
            r.bold = True
            r.font.size = Pt(10.5)
            remaining = remaining[idx + len(bp):]
        if remaining:
            r = p.add_run(remaining)
            r.font.size = Pt(10.5)
    else:
        run = p.add_run(text)
        run.font.size = Pt(10.5)
    return p


def numbered(doc, text, bold_parts=None):
    p = doc.add_paragraph(style='List Number')
    p.paragraph_format.left_indent  = Inches(0.25)
    p.paragraph_format.space_after  = Pt(2)
    p.paragraph_format.space_before = Pt(1)
    if bold_parts:
        remaining = text
        for bp in bold_parts:
            idx = remaining.find(bp)
            if idx == -1:
                continue
            if idx > 0:
                r = p.add_run(remaining[:idx])
                r.font.size = Pt(10.5)
            r = p.add_run(bp)
            r.bold = True
            r.font.size = Pt(10.5)
            remaining = remaining[idx + len(bp):]
        if remaining:
            r = p.add_run(remaining)
            r.font.size = Pt(10.5)
    else:
        run = p.add_run(text)
        run.font.size = Pt(10.5)
    return p


def callout(doc, text, kind='info'):
    """Shaded callout box with a coloured left border."""
    colours = {
        'info':    ('276BBD', 'D6EAF8'),
        'warning': ('E67E22', 'FEF9E7'),
        'tip':     ('1E8449', 'E9F7EF'),
    }
    border_hex, fill_hex = colours.get(kind, colours['info'])
    icons = {'info': 'ℹ️  ', 'warning': '⚠️  ', 'tip': '💡  '}
    icon = icons.get(kind, '')

    p = doc.add_paragraph()
    p.paragraph_format.space_before    = Pt(6)
    p.paragraph_format.space_after     = Pt(6)
    p.paragraph_format.left_indent     = Inches(0.15)
    p.paragraph_format.right_indent    = Inches(0.15)
    set_para_shading(p, fill_hex)
    set_para_border(p, side='left', color=border_hex, sz='24', space='8')
    run = p.add_run(icon + text)
    run.font.size = Pt(10)
    run.font.italic = True
    return p


def screenshot_placeholder(doc, label):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after  = Pt(8)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Draw a simple shaded box via paragraph shading
    set_para_shading(p, 'F2F3F4')
    run = p.add_run(f'[ SCREENSHOT — {label} ]')
    run.font.size   = Pt(9)
    run.font.italic = True
    run.font.color.rgb = C_MUTED
    return p


def add_table(doc, headers, rows, col_widths=None):
    n_cols = len(headers)
    tbl = doc.add_table(rows=1 + len(rows), cols=n_cols)
    tbl.style = 'Table Grid'
    tbl.alignment = WD_TABLE_ALIGNMENT.LEFT

    # Header row
    hdr_row = tbl.rows[0]
    for i, h in enumerate(headers):
        cell = hdr_row.cells[i]
        set_cell_bg(cell, C_DARK)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h)
        run.bold = True
        run.font.size = Pt(10)
        run.font.color.rgb = C_WHITE

    # Data rows
    for r_idx, row_data in enumerate(rows):
        row = tbl.rows[r_idx + 1]
        for c_idx, cell_text in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            if (r_idx % 2) == 1:
                set_cell_bg(cell, RGBColor(0xF8, 0xF9, 0xFA))
            p = cell.paragraphs[0]
            run = p.add_run(str(cell_text))
            run.font.size = Pt(10)

    # Column widths
    if col_widths:
        for i, w in enumerate(col_widths):
            for row in tbl.rows:
                row.cells[i].width = Inches(w)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return tbl


# ════════════════════════════════════════════════════════════════════════════
# DOCUMENT CONTENT
# ════════════════════════════════════════════════════════════════════════════

# ── Title block ──────────────────────────────────────────────────────────────
title_p = doc.add_paragraph()
title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
title_p.paragraph_format.space_before = Pt(0)
title_p.paragraph_format.space_after  = Pt(4)
tr = title_p.add_run('Supervisor Workflow Guide')
tr.bold = True
tr.font.size = Pt(22)
tr.font.color.rgb = C_DARK

sub_p = doc.add_paragraph()
sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
sub_p.paragraph_format.space_after = Pt(2)
sr = sub_p.add_run('MES Head · Technical Services · Odoo 18')
sr.font.size = Pt(11)
sr.font.color.rgb = C_MUTED

meta_p = doc.add_paragraph()
meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
meta_p.paragraph_format.space_after = Pt(12)
mr = meta_p.add_run('Last updated: July 25, 2026  ·  techservices database  ·  localhost:8069')
mr.font.size = Pt(9)
mr.font.color.rgb = C_MUTED
mr.font.italic = True

hr(doc)

# ── About ────────────────────────────────────────────────────────────────────
heading1(doc, 'About This Guide')
body(doc,
     'This document walks the MES Head (Supervisor role) through the complete '
     'end-to-end workflow for a new client service request.',
     bold_parts=['MES Head (Supervisor role)'])
body(doc, 'Login: your chem email', bold_parts=['Login:'])

# ── Workflow at a Glance ─────────────────────────────────────────────────────
heading1(doc, 'Workflow at a Glance')

glance_headers = ['#', 'Action', 'Location', 'Key Field / Button']
glance_rows = [
    ['1',  'Login as MES Head',                    '/odoo/login',                    'Email: your email'],
    ['2',  'Open CRM Pipeline',                    'CRM → Pipeline',                 'Main menu grid'],
    ['3',  'Create Opportunity',                   'CRM → New (list view)',           'Opportunity title'],
    ['4',  'Add Contact & Internal Notes',         'Opportunity form',               'Contact → Create and edit… / Internal Notes tab'],
    ['5',  'Create Quotation',                     'Opportunity → New Quotation',    'New Quotation button'],
    ['6',  'Set Service Type',                     'Quotation form',                 'Service Type dropdown (required)'],
    ['7',  'Select Worktag',                       'Quotation form',                 'Worktag field (auto-fills Speedchart)'],
    ['8',  'Add Labor Product',                    'Order Lines tab',                'Add a product → one of 4 labor products'],
    ['9',  'Confirm → Sales Order',                'Quotation form',                 'Confirm button'],
    ['10', 'Open Repair Order',                    'Sales Order → Repairs button',   'Repairs N smart button'],
    ['11', 'Assign to Technician',                 'Repair Order form',              'Responsible field'],
    ['12', 'Create Invoice Draft',                 'Sales Order → Create Invoice',   'Create Invoice → Create Draft'],
]
add_table(doc, glance_headers, glance_rows, col_widths=[0.3, 1.7, 1.8, 2.6])

# ── Step 1 ───────────────────────────────────────────────────────────────────
heading1(doc, 'Step 1 — Log In as MES Head')
body(doc, 'Navigate to Odoo and authenticate with the Supervisor account.')
heading3(doc, 'How To')
numbered(doc, 'Go to http://137.82.146.143:8069 and select the techservices database.')
numbered(doc, 'Enter your email and the assigned password, then click Log In.', bold_parts=['Log In'])
numbered(doc, 'The app opens at Discuss → Inbox. The top-right corner shows MES confirming the correct account.', bold_parts=['MES'])
callout(doc,
    'The Supervisor role grants access to CRM, Sales, Repairs, Timesheets, and Invoicing. '
    'Settings and inventory product creation are restricted to the Manager role.\n'
    'The Supervisor cannot see the Cost, Purchase Taxes, Sales, Inventory, or Billing tabs on '
    'product forms — these are restricted to the Manager role.',
    kind='info')
screenshot_placeholder(doc, 'Step 1: Logged in as MES Head. Discuss inbox confirms correct session.')

# ── Step 2 ───────────────────────────────────────────────────────────────────
heading1(doc, 'Step 2 — Open the CRM Pipeline')
body(doc, 'Navigate to CRM to view and manage service opportunities.')
heading3(doc, 'How To')
numbered(doc, 'Click the main menu grid (top-left) and open CRM, or navigate to /odoo/crm.', bold_parts=['CRM'])
numbered(doc, 'The Kanban pipeline shows stages: New, Needs information or actions, and Won.', bold_parts=['New', 'Needs information or actions', 'Won'])
numbered(doc, 'The default filter is My Pipeline — showing only your assigned opportunities.', bold_parts=['My Pipeline'])
callout(doc, 'Switch to List view (icon top-right) for a faster overview when managing many opportunities at once.', kind='tip')
screenshot_placeholder(doc, 'Step 2: CRM Pipeline in Kanban view showing current opportunities.')

# ── Step 3 ───────────────────────────────────────────────────────────────────
heading1(doc, 'Step 3 — Create a New Opportunity, Add Contact & Internal Notes')
body(doc, 'Open the full form, create a new client contact, and record intake details.')

heading3(doc, 'New Opportunity')
numbered(doc, 'Switch to List view and click New (top-left) to open the full opportunity form.', bold_parts=['New'])
numbered(doc, 'Enter a descriptive title (e.g. "Instrument Calibration & Repair Request").')
numbered(doc, 'The Salesperson is auto-set to MES Head. The dropdown only shows users belonging to the same company.', bold_parts=['Salesperson'])

heading3(doc, 'Add a New Contact')
numbered(doc, 'Click the Contact field and type the new client\'s name.', bold_parts=['Contact'])
numbered(doc, 'Select Create and edit… from the dropdown to open the contact dialog.', bold_parts=['Create and edit…'])
numbered(doc, 'Select Individual, fill in Name, Phone, and Email, then click Save & Close.', bold_parts=['Individual', 'Save & Close'])
numbered(doc, 'The contact\'s email and phone populate back on the opportunity form.')
screenshot_placeholder(doc, 'Step 3a: Creating a new Individual contact with phone and email from within the opportunity.')

heading3(doc, 'Add Internal Notes')
numbered(doc, 'Click the Internal Notes tab on the opportunity form.', bold_parts=['Internal Notes'])
numbered(doc, 'Type your intake notes — instrument details, priority, timeline, pre-authorised spend.')
numbered(doc, 'Click the cloud save icon in the breadcrumb to save.')
callout(doc,
    'Internal Notes are private — visible only to Odoo users, not to the client. '
    'Use the Send message button for client-facing communication.',
    kind='warning')
screenshot_placeholder(doc, 'Step 3b: Opportunity form with new contact and internal intake notes.')

# ── Step 4 ───────────────────────────────────────────────────────────────────
heading1(doc, 'Step 4 — Create a Quotation')
body(doc, 'Generate a quotation directly from the opportunity.')
heading3(doc, 'How To')
numbered(doc, 'From the saved opportunity, click New Quotation in the action bar.', bold_parts=['New Quotation'])
numbered(doc, 'The quotation opens pre-filled with the customer and opportunity name.')
numbered(doc, 'The Expiration date defaults to 30 days out.', bold_parts=['Expiration'])
screenshot_placeholder(doc, 'Step 4: New Quotation form. Service Type is required (highlighted in red if missing).')

# ── Step 5 ───────────────────────────────────────────────────────────────────
heading1(doc, 'Step 5 — Add Service Type, Worktag & Labor Product')
body(doc, 'Classify the service, select the billing worktag, and add the labor line.')

heading3(doc, 'Service Type (required)')
body(doc, 'Click the Service Type dropdown and choose the appropriate category:', bold_parts=['Service Type'])
add_table(doc,
    ['Option', 'When to use'],
    [
        ['Repair',        'Fixing or restoring a faulty instrument'],
        ['Manufacturing', 'Building or fabricating a component'],
        ['Move',          'Relocating equipment between labs'],
        ['Installation',  'Setting up new equipment on-site'],
        ['Maintenance',   'Scheduled preventive maintenance'],
    ],
    col_widths=[1.6, 4.9])

heading3(doc, 'Worktag')
numbered(doc, 'Click the Worktag field and type the code (e.g. CALREP-2026-001).', bold_parts=['Worktag'])
numbered(doc, 'Worktags are filtered to those linked to the customer\'s commercial partner.')
numbered(doc, 'When selected, the Speedchart field auto-populates from the worktag record.', bold_parts=['Speedchart'])
numbered(doc, 'Worktags must be validated by a Manager before an invoice can be posted.', bold_parts=['validated'])
callout(doc,
    'No worktags showing?  A worktag must be linked to the client\'s company via its Companies '
    'field (a worktag can belong to multiple companies). Ask the Manager to create the worktag '
    'or link it to the correct company if none appear. See "Managing Worktags on a Company '
    'Contact" later in this guide.',
    kind='info')

heading3(doc, 'Labor Product (Order Lines)')
body(doc, 'Click Add a product and select the labor product matching the client\'s category:', bold_parts=['Add a product'])
add_table(doc,
    ['Product', 'Client Category'],
    [
        ['Work order / repair order for Chemistry client – Labor',           'UBC Chemistry department'],
        ['Work order / repair order for UBC (external) client – Labor',      'Other UBC departments'],
        ['Work order / repair order for External to UBC or private client – Labor', 'Non-UBC / private clients'],
        ['Work order / repair order for Departmental service client – Labor','Internal MES department service'],
    ],
    col_widths=[4.2, 2.3])
screenshot_placeholder(doc, 'Step 5: Quotation complete — Service Type, Worktag, Speedchart auto-filled, labor product added.')

# ── Step 6 ───────────────────────────────────────────────────────────────────
heading1(doc, 'Step 6 — Confirm Quotation → Sales Order')
body(doc, 'Lock in pricing and generate the sale order and linked repair order.')
heading3(doc, 'How To')
numbered(doc, 'Review all fields, then click Confirm in the action bar.', bold_parts=['Confirm'])
numbered(doc, 'The status bar moves to Sales Order and the record gets a number (e.g. S00081).', bold_parts=['Sales Order'])
numbered(doc, 'A Repairs smart button appears — the system auto-creates a linked repair order.', bold_parts=['Repairs'])
callout(doc,
    'Once confirmed, pricing is locked. To make changes, cancel and recreate, or use Lock/Unlock '
    'controls (visible to managers).',
    kind='tip')
screenshot_placeholder(doc, 'Step 6: Sales Order confirmed. The Repairs smart button shows 1 linked repair order.')

# ── Step 7 ───────────────────────────────────────────────────────────────────
heading1(doc, 'Step 7 — Open the Repair / Work Order')
body(doc, 'Access the auto-created repair order and review its details.')
heading3(doc, 'How To')
numbered(doc, 'From the confirmed sales order, click the Repairs smart button (top bar).', bold_parts=['Repairs'])
numbered(doc, 'The repair order opens pre-filled with customer, opportunity, service type, and scheduled date.')
numbered(doc, 'Stage bar: New → Confirmed → Under Repair → Repaired. New repair orders land in Confirmed.', bold_parts=['New', 'Confirmed', 'Under Repair', 'Repaired'])
numbered(doc, 'The Parts tab is where technicians add physical components used during the repair.', bold_parts=['Parts'])
numbered(doc, 'The Timesheets tab records labour hours against this order.', bold_parts=['Timesheets'])
callout(doc,
    'Blocked repairs: If a technician sets a repair to Blocked (e.g. waiting for parts or client '
    'information), a yellow warning banner appears at the top of the form. The technician is '
    'required to log a note explaining the reason for the block. A blocked repair cannot progress '
    'until the issue is resolved.',
    kind='warning')
screenshot_placeholder(doc, 'Step 7: Repair Order in Confirmed state, linked to the Sale Order.')
screenshot_placeholder(doc, 'Step 7b: Repair Order in Blocked state showing the yellow warning banner.')

# ── Step 8 ───────────────────────────────────────────────────────────────────
heading1(doc, 'Step 8 — Assign the Repair Order to a Technician')
body(doc, 'Change the Responsible field to the staff member who will carry out the work.', bold_parts=['Responsible'])
heading3(doc, 'How To')
numbered(doc, 'Click the Responsible field (right column of the repair order header).', bold_parts=['Responsible'])
numbered(doc, 'Clear the current value and type the technician\'s name. The dropdown only shows users belonging to the same company.')
numbered(doc, 'Select the correct user from the dropdown and save using the cloud save icon.')
callout(doc,
    'The assigned technician will see this repair order in their own queue. They can log '
    'timesheet entries directly from the repair order\'s Timesheets tab.',
    kind='tip')
screenshot_placeholder(doc, 'Step 8: Repair order assigned to a technician.')

# ── Step 9 ───────────────────────────────────────────────────────────────────
heading1(doc, 'Step 9 — Create Invoice Draft')
body(doc, 'Return to the sales order and generate a draft invoice for Manager review.')

heading3(doc, 'Pre-requisite: Worktag Validation')
callout(doc,
    'Manager action required: A Manager must check the Validated field on the worktag before '
    'this step succeeds. Otherwise Odoo blocks invoice creation: "worktag has not been validated '
    '— a manager must check the Validated field on the worktag first."',
    kind='warning')

heading3(doc, 'How To')
numbered(doc, 'Click the breadcrumb or use the Sale Orders smart button to return to the sales order.')
numbered(doc, 'Click Create Invoice (top-left action bar).', bold_parts=['Create Invoice'])
numbered(doc, 'The dialog defaults to Regular invoice — leave this selected.', bold_parts=['Regular invoice'])
numbered(doc, 'Click Create Draft.', bold_parts=['Create Draft'])
numbered(doc, 'The draft invoice opens with all lines, taxes, worktag, and customer details pre-populated.')
screenshot_placeholder(doc, 'Step 9a: Create Invoice(s) dialog — select Regular invoice and click Create Draft.')
screenshot_placeholder(doc, 'Step 9b: Draft Customer Invoice with labor line, taxes, and worktag. Ready for Manager review.')

heading3(doc, 'What Happens Next')
bullet(doc, 'The Supervisor\'s job ends here — the draft sits in Accounting → Customer Invoices with status Draft.', bold_parts=['Draft'])
bullet(doc, 'A Manager reviews and clicks Confirm to post the invoice and generate journal entries.', bold_parts=['Confirm'])
bullet(doc, 'Once posted, the invoice can be emailed to the client directly from Odoo.')

# ── Managing Worktags ────────────────────────────────────────────────────────
heading1(doc, 'Managing Worktags on a Company Contact')
body(doc,
     'Worktags are master records shared across companies. A single worktag (e.g. a cost centre '
     'code) can be linked to multiple client companies.')

heading3(doc, 'Viewing a Company\'s Worktags')
numbered(doc, 'Go to Contacts and open a company record.', bold_parts=['Contacts'])
numbered(doc, 'Click the Worktags tab.', bold_parts=['Worktags'])
numbered(doc, 'All worktags currently linked to this company are listed with their code, name, cost centre, speedchart, category, status, and validation state.')
screenshot_placeholder(doc, 'Contacts: Worktags tab on a company record showing linked worktags.')

heading3(doc, 'Adding an Existing Worktag to a Company')
numbered(doc, 'On the Worktags tab, click Add.', bold_parts=['Worktags', 'Add'])
numbered(doc, 'A search dialog opens — type the worktag code.')
numbered(doc, 'Select the matching worktag. All its fields (name, cost centre, speedchart, category, status) auto-populate in the row.')
numbered(doc, 'Save the record.')
callout(doc,
    'Worktag details (code, cost centre, etc.) are managed centrally from '
    'Accounting → Configuration → Worktags. Editing them from the contact form affects all '
    'companies they are linked to.',
    kind='info')
screenshot_placeholder(doc, 'Contacts: Adding an existing worktag by code — details auto-populate on selection.')

heading3(doc, 'Creating a New Worktag')
body(doc,
     'New worktags should be created by a Manager from Accounting → Configuration → Worktags '
     'to ensure all required fields (including Validated) are properly set before the worktag '
     'is used on a sale order.',
     bold_parts=['Accounting → Configuration → Worktags', 'Validated'])

# ── Product Catalogue ────────────────────────────────────────────────────────
heading1(doc, 'Product Catalogue — What the Supervisor Can See')
body(doc,
     'When browsing inventory products (Inventory → Products), the Supervisor view is '
     'intentionally restricted.')

heading3(doc, 'Product List View')
body(doc, 'The table shows these columns by default (additional optional columns can be toggled via the column chooser):')
add_table(doc,
    ['Column', 'Notes'],
    [
        ['Product Name',          'Always visible'],
        ["Product's description", 'Optional — visible by default'],
        ['Make',                  'Optional — visible by default'],
        ['Make Part Number',      'Optional — visible by default'],
        ['Supplier',              'Optional — visible by default'],
        ['Supplier Part Number',  'Optional — visible by default'],
        ['Sales Price',           'Always visible'],
        ['Unit of Measure',       'Always visible'],
        ['Date Added',            'Optional — visible by default'],
    ],
    col_widths=[2.2, 4.3])

heading3(doc, 'Product Form View')
body(doc, 'Fields visible to the Supervisor on the General Information tab:')
bullet(doc, "Product's description")
bullet(doc, 'Make / Make Part Number')
bullet(doc, 'Supplier / Supplier Part Number')
bullet(doc, 'Alternative Supplier / Alternative Supplier Part Number')
bullet(doc, 'Room Location / Drawer Location')
callout(doc,
    'Restricted fields: The Supervisor cannot see Cost (standard price), Purchase Taxes, '
    'Product Type radio button, or the Sales, Inventory, and Billing tabs. '
    'These are visible only to Managers.',
    kind='warning')
screenshot_placeholder(doc, 'Product form as seen by the Supervisor role, showing available fields and hidden tabs.')

# ── Save ─────────────────────────────────────────────────────────────────────
out = '/Users/smedrano/Documents/Odoo_technical_services/docs/supervisor_workflow.docx'
doc.save(out)
print(f'Saved: {out}')
