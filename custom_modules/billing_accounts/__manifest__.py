{
    'name': 'Billing Accounts (Worktags)',
    'version': '18.0.1.0.0',
    'summary': 'Adds worktags (billing account codes) to companies, sale orders and invoices',
    'author': 'Your Name',
    'category': 'Accounting',
    'depends': [
        'analytic',     # Analytic accounting base
        'account',      # Invoicing and accounting
        'sale',         # Sale orders
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/service_worktag_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
