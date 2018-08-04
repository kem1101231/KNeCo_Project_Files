# -*- coding: utf-8 -*-
{
    'name': "MGC-Request KNeCo-Draft",

    'summary': """
        MGC Requests - KNeCo Test""",

    'description': """
        A Request for the needs of the company
    """,

    'author': "MSG-MIS KNeCo",
    'website': "http://www.mutigroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'account', 'stock', 'purchase'],

    # always loaded
    'data': [
        'security/request_security.xml',
        'security/ir.model.access.csv',

        'data/ir_sequence.xml',

        'views/request_views.xml',
        'views/purchase_views.xml',
        'views/request_config_views.xml',

        'report/report_request_views.xml',

        'report/template/report_request.xml',
        'report/template/request_footer.xml',
        'report/template/all_request_report.xml',
        'report/template/report_request_template.xml',

        'views/menuitem_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'images': [
        'static/description/icon.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}