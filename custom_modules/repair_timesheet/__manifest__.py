{
    'name': 'Repair Timesheet',
    'version': '18.0.2.0.0',
    'summary': 'Adds timesheet tracking to repair orders using native analytic lines',
    'author': 'Your Name',
    'category': 'Repair',
    'depends': [
        'repair',           # Repair order model
        'hr_timesheet',     # account.analytic.line + timesheet views
        'sale',             # Sale order for billing sync
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_analytic_line_views.xml',
        'views/repair_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
