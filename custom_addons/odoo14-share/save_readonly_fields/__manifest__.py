
{
    'name': 'Save ReadOnly Fields',
    'summary': 'To allow save the readonly fields...',
    'description': """
Save ReadOnly Fields
====================

Save fields whit property 'readonly' activated...
""",

    'author': "Alejandro Cora González",
    'website': "",

    'category': '',
    'version': "14.0.1.0.0",

    'depends': [
        'web',
    ],

    # Always loaded.
    'data': [
        # Templates...
        'static/src/xml/webclient_templates.xml',
    ],

    'demo': [
    ],

    'test': [
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
