{
    'name': 'Opportunity Display',
    'version': '18.0.2.0.0',
    'summary': 'Shows opportunity, notes and service category on sale orders, invoices and repair orders',
    'author': 'Your Name',
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
