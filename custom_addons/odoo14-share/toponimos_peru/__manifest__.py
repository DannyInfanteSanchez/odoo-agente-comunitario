# -*- coding: utf-8 -*-
{
    'name': "Toponimos de Peru",
    'summary': """
        Ubigeo Departamentos, Provincias y distritos del Peru según INEI.""",

    'description': """
Localizacion Peruana.
====================================

Clientes y Proveedores:
--------------------------------------------
    * Tabla de Ubigeos - Según INEI 2016
    * Departamentos, provincias y distritos de todo el Perú

    """,
    'author': "",
    'website': "",
    'category': 'Uncategorized',
    'version': '14.0.0.0.0',
    'depends': ['base'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'views/res_country_view.xml',
        'data/res_country_data.xml',
        'data/res.country.state.csv',
        'data/patch1/res.country.state.csv',
        'data/patch2/res.country.state.csv',
    ],
    'demo': [],
}
