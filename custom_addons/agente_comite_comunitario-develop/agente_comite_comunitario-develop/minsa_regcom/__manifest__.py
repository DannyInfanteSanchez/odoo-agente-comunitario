# -*- coding: utf-8 -*-

{
    'name': 'Registro Agente Comunirario de Salud',
    'description': u'Módulo para el registro de agentes comunitario por establecimientos',
    'author': 'MINSA',
    'category': 'Others',
    'version': '0.1',
    'depends': [
        "base",
        "base_setup",
        "mail",
        "web",
        "auth_signup",
        'oi_attachment_error',
        "renipress",
        "toponimos_peru",
    ],
    'data': [
        "data/parametros.xml",
        "data/minsa.etnia.xml",
        "data/minsa.genero.xml",
        "data/minsa.grado.instruccion.xml",
        "data/minsa.seguro.xml",
        "data/minsa.tipo.voluntariado.xml",
        "data/minsa.operador.mobil.xml",
        'security/security.xml',
        'security/ir.model.access.csv',
        "views/renipress_views.xml",
        "views/res_user.xml",
        "views/forms.xml",
        "views/view_agente_comunitario.xml",
        "views/menus.xml",
    ],
    'application': True,
    'installable': True
}
