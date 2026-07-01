# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2017 darkknightapps@gmail.com
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################
{
    'name': "Website Footer",
    'summary': """
        Website Footer Customization """,
    'description': """
=======================================================================================
        * Aligns copyright and company details to the center of the screen
        * Modified background color for website footer

""",

    'author': 'Dark Knight',
    'website': '',
    'category': 'Website',
    'version': '1.0',
    'depends': ['website'],
    'data': [
        'views/website_templates.xml',
    ],
    'demo': [
    ],
    'images': ['images/Footer2.png'],
    'installable': True,
    'application': False,
}
