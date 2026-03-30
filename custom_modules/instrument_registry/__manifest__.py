{
    'name': 'Instrument Registry',
    'version': '18.0.2.0.0',
    'summary': 'Registry of instruments and equipment for repair tracking',
    'author': 'Your Name',
    'category': 'Repair',
    'depends': [
        'repair',
        'sale',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        # data/ must load before views/ so the sequence exists
        # before any instrument record tries to use it
        'data/ir_sequence_data.xml',
        'views/service_building_views.xml',
        'views/service_instrument_type_views.xml',
        'views/service_instrument_views.xml',
        'views/repair_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
