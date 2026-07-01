# -*- coding: utf-8 -*-
{
    'name': "MINSA - RENIPRESS - Establecimientos de Salud",
    'summary': """
        Establecimientos de Salud, Diresa, Red, Microredes""",

    'description': """
    Información de los Establecientos de Salud
    """,
    'author': "",
    'website': "http://www.minsa.gob.pe",
    'category': 'Others',
    'version': '14.0.0.0.0',
    'depends': ['toponimos_peru'],
    'data': [
        'security/ir.model.access.csv',
        #'data/querys.sql',
        'data/renipress_diresa_data.xml',
        'data/renipress_red_data.xml',
        'data/renipress_microred_data.xml',
        'data/renipress_eess_data.xml',
        'views/renipress_views.xml',
    ],
}
