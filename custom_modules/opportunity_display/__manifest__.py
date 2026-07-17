{
    'name': 'Opportunity Display',
    'version': '18.0.3.0.0',
    'summary': 'Shows opportunity, notes and service type on sale orders, invoices and repair orders',
    'author': 'Your Name',
    'license': 'LGPL-3',
    'category': 'Sales',
    'depends': [
        'sale_crm',
        'account',
        'repair',
    ],
    'data': [
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/repair_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
