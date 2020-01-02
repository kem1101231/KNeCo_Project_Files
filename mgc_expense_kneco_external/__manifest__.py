# -*- coding: utf-8 -*-
{
    'name': "MGC Project Expense IS External",

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
    'depends': ['base','account', 'purchase','mgc_rf_purchase_order_plugin'],


    # always loaded
    'data': [

        'security/expense_security.xml',
        'security/ir.model.access.csv',
        
        #'views/views.xml',
        #'views/templates.xml',
        'views/index.xml',
        'views/expense_check_base.xml',
        'views/expense_check_form.xml',
        'views/check_voucher_template.xml',
        'views/expense_purchase_journal_template.xml',
        'views/expense_purchase_transaction.xml',
        'views/expense_check_template.xml',
        'views/expense_aged_payable.xml',
        'views/expense_vendor_ledger.xml',
        'views/expense_aged_payable_vendor.xml',
        'views/expense_aged_payable_due.xml',
        
    ],
    'images': [
        'static/description/icon.png',
    ],
    'installable': True,
    'application': True,
}