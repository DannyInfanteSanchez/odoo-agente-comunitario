{
    'name': 'Módulo Seguridad - MINSA Odoo',
    'version': '1.0.0',
    'category': 'Others',
    'summary': 'Seguridad MINSA Odoo',
    'author': '',
    'description': 'Módulo de Seguridad MINSA Odoo',
    'data': [

        # data
        'data/seguridad_data.xml',
        'data/seguridad_cron.xml',

        # views
        'views/seguridad_user_inactive_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license':'LGPL-3',
}
