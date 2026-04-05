{
    'name': 'Opportunity Display',
    'version': '18.0.1.0.0',
    'summary': 'Shows the linked CRM opportunity on sale orders, invoices and repair orders',
    'author': 'Your Name',
    'category': 'Sales',
    'depends': [
        'sale_crm',     # opportunity_id on sale.order
        'account',      # account.move (invoices)
        'repair',       # repair.order
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
