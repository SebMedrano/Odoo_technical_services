{
    'name': 'Repair Timesheet',
    'version': '18.0.5.0.0',
    'summary': 'Adds timesheet tracking to repair orders using native analytic lines',
    'author': 'Your Name',
    'category': 'Repair',
    'depends': [
        'repair',
        'hr_timesheet',
        'sale',
        'crm',
        'instrument_registry',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/repair_timesheet_security.xml',
        'views/hr_timesheet_views.xml',
        'views/account_analytic_line_views.xml',
        'views/repair_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
