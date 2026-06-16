{
    'name': 'Website Lead Forms',
    'version': '18.0.1.0.0',
    'summary': 'Multiple website contact forms routing to different salespeople and companies',
    'category': 'Website',
    'depends': ['website', 'crm', 'website_crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/backend_views.xml',
        'views/frontend_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
