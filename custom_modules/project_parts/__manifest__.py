{
    'name': 'Project Parts',
    'version': '18.0.1.0.0',
    'summary': 'Adds parts consumption tracking to project tasks with automatic SO sync',
    'author': 'Your Name',
    'category': 'Project',
    'depends': [
        'project',          # project.task model
        'sale_project',     # project → sale order link
        'sale',             # sale.order.line model
        'product',          # product.product model
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/project_task_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
