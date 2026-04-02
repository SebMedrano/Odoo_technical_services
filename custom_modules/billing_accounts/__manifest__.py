{
    'name': 'Billing Accounts (Worktags)',
    'version': '18.0.4.0.0',
    'summary': 'Adds worktags (billing account codes) to companies, sale orders and invoices',
    'author': 'Your Name',
    'category': 'Accounting',
    'depends': [
        'analytic',
        'account',
        'sale',
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/service_worktag_views.xml',
        'views/res_partner_views.xml',
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
