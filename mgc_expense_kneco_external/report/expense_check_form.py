# -*- coding: utf-8 -*-

import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError


class MGCExpenseCheckForm(models.AbstractModel):
    _name = 'report.mgc_expense_kneco_external.expense_check_form'
    
    @api.model
    def render_html(self, docids, data):
        docargs = {
            'doc_ids': self.ids,
            'doc_model': None,
            'docs': {'1':'one','2':'two','3':'three','4':'four','5':'five'},
            'time': time,
            'dataInput': data['data'],
        }
        return self.env['report'].render('mgc_expense_kneco_external.expense_check_form', docargs)

class MGCExpensePurchaseJournalTemplate(models.AbstractModel):
    _name = 'report.mgc_expense_kneco_external.expense_purchase_journal'
    
    @api.model
    def render_html(self, docids, data):
        docargs = {
            'doc_ids': self.ids,
            'doc_model': None,
            'docs': {'1':'one','2':'two','3':'three','4':'four','5':'five'},
            'time': time,
            'dataInput': data['data'],
        }
        return self.env['report'].render('mgc_expense_kneco_external.expense_purchase_journal_template', docargs)

class MGCExpensePurchaseJournalTemplate(models.AbstractModel):
    _name = 'report.mgc_expense_kneco_external.expense_purchase_transaction'
    
    @api.model
    def render_html(self, docids, data):
        docargs = {
            'doc_ids': self.ids,
            'doc_model': None,
            'docs': {'1':'one','2':'two','3':'three','4':'four','5':'five'},
            'time': time,
            'dataInput': data['data'],
        }

        return self.env['report'].render('mgc_expense_kneco_external.expense_purchase_transaction_template', docargs)

class MGCExpenseCheckTemplate(models.AbstractModel):
    _name = 'report.mgc_expense_kneco_external.expense_check_template'
    
    @api.model
    def render_html(self, docids, data):
        docargs = {
            'doc_ids': self.ids,
            'doc_model': None,
            'docs': {'1':'one','2':'two','3':'three','4':'four','5':'five'},
            'time': time,
            'dataInput': data['data'],
        }

        return self.env['report'].render('mgc_expense_kneco_external.expense_check_template', docargs)

class MGCExpenseAgedPayableTemplate(models.AbstractModel):
    _name = 'report.mgc_expense_kneco_external.expense_aged_payable'
    
    @api.model
    def render_html(self, docids, data):
        docargs = {
            'doc_ids': self.ids,
            'doc_model': None,
            'docs': {'1':'one','2':'two','3':'three','4':'four','5':'five'},
            'time': time,
            'dataInput': data['data'],
        }


        return self.env['report'].render('mgc_expense_kneco_external.expense_aged_payable', docargs)

class MGCExpenseAgedPayableDueTemplate(models.AbstractModel):
    _name = 'report.mgc_expense_kneco_external.expense_aged_payable_due'
    
    @api.model
    def render_html(self, docids, data):

        docargs = {
            'doc_ids': self.ids,
            'doc_model': None,
            'docs': {'1':'one','2':'two','3':'three','4':'four','5':'five'},
            'time': time,
            'dataInput': data['data'],
        }

        print("************************")
        print(docargs['dataInput'])

        return self.env['report'].render('mgc_expense_kneco_external.expense_aged_payable_due', docargs)

class MGCExpenseAgedPayableVendorTemplate(models.AbstractModel):
    _name = 'report.mgc_expense_kneco_external.expense_aged_payable_vendor'
    
    @api.model
    def render_html(self, docids, data):

        docargs = {
            'doc_ids': self.ids,
            'doc_model': None,
            'docs': {'1':'one','2':'two','3':'three','4':'four','5':'five'},
            'time': time,
            'dataInput': data['data'],
        }

        print("@@@@@@@@@@@@@@@@@@@@@@@@@")
        print(docargs['dataInput'])

        return self.env['report'].render('mgc_expense_kneco_external.expense_aged_payable_vendor', docargs)

class MGCExpenseVendorLedgerTemplate(models.AbstractModel):
    _name = 'report.mgc_expense_kneco_external.expense_vendor_ledger'
    
    @api.model
    def render_html(self, docids, data):
        docargs = {
            'doc_ids': self.ids,
            'doc_model': None,
            'docs': {'1':'one','2':'two','3':'three','4':'four','5':'five'},
            'time': time,
            'dataInput': data['data'],
        }

        return self.env['report'].render('mgc_expense_kneco_external.expense_vendor_ledger', docargs)
