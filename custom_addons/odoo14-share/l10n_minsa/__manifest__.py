
{
    'name': "MINSA - Base",

    'summary': """
        Localización Base para Odoo - Minsa""",

    'description': """
    Modifica los parametros de la Compañia, moneda
    """,

    'author': "",
    'website': "http://www.minsa.gob.pe",

    'category': 'Others',
    'version': "14.0.1.0.0",

    'depends': ['base', 'web'],

    'data': [
        'data/base.xml',
        'views/views.xml',
    ],
    'demo': [
    ],
    'application': False,
}
