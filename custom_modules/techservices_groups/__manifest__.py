{
    'name': 'Technical Services Groups',
    'version': '18.0.1.0.0',
    'summary': 'Defines Technician, Supervisor and Manager roles for Technical Services',
    'author': 'Your Name',
    'category': 'Technical Services',
    'depends': [
        'base',
        'stock',
        'hr_timesheet',
        'sales_team',
        'account',
    ],
    'data': [
        'security/techservices_groups.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
