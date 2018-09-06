# -*- coding: utf-8 -*-
{
    'name': "MGC Project Expense IS",

    'summary': """
        Application to track conducted expense of the company""",

    'description': """
        
    """,

    'author': "MGC-MIS (KNeCo)",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
       # any module necessary for this one to work correctly
    'depends': ['base', 'mgc_request'],


    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        #'views/views.xml',
        #'views/templates.xml',
        'views/index.xml',
        'views/expense_check_form.xml',
        'views/expense_check_base.xml',
    ],
    'images': [
        'static/description/icon.png',
    ],
    'installable': True,
    'application': True,
}