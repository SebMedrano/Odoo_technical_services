{
    'name': 'Project Parts',
    'version': '18.0.2.0.0',
    'summary': 'Parts consumption on project tasks with stock moves and SO sync',
    'author': 'Your Name',
    'license': 'LGPL-3',
    'category': 'Project',
    'depends': [
        'project',
        'sale_project',
        'sale',
        'product',
        'stock',         # Required for stock moves
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/project_task_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
