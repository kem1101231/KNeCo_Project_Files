from odoo import api, models, fields
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError, UserError
#import xmlrpclib
#import odoorpc

class MGC_Accounting_Ledger(models.Model):
	_name = "mgc.specialized.accounting.ledger"

	def _get_credit_value(self):
		for ledger in self:
			dataValue = ''

			print("=====================================================")
			print(ledger.entry_type)

			if ledger.entry_type == 'credit': #or ledger.entry_type == 'neg-credit'
				dataValue = str(ledger.amount)

			ledger.update({
	            'credit_value': dataValue,
	        })
			
			''''
			if ledger.entry_type == 'neg-credit':
					self.env.create({ 'reference_code': ledger.reference_code,
												                                  'reference_pay': ledger.reference_pay,
												                                  'reference_type': 'payable', 
												                                  'location_id': ledger.location_id,
												                                  'description': ledger.description,
												                                  'account_name': ledger.account_name,
												                                  'entry_type': 'debit',
												                                  'amount': ledger.amount,
												                                })
			'''
	
	def _get_debit_value(self):
		for ledger in self:
			dataValue = ''
			if ledger.entry_type == 'debit':
				dataValue = str(ledger.amount)

			ledger.update({
                'debit_value': dataValue,
            })            

	#name = fields.Char()
	reference_code = fields.Char(string="Reference Number")
	#reference_id = fields.Integer(string="Reference ID")
	reference_pay = fields.Integer(string="Reference Payable")
	reference_exp = fields.Integer(string="Reference Expense")
	reference_type = fields.Char(string="Reference Type")
	location_id = fields.Many2one(comodel_name="mgc.acct_chart.acct_location", string="Location")
	description = fields.Char(string="Description")
	account_name = fields.Many2one(comodel_name ="mgc.acct_chart.acct_finance", string="Account Name")
	entry_type = fields.Selection(selection=[('debit','Debit'),('credit','Credit'),('neg-credit','Credit')], string="Entry Type")
	amount = fields.Float(string="Amount")
	debit_value = fields.Char(string="Debit",compute="_get_debit_value", store=False)
	credit_value = fields.Char(string="Credit",compute="_get_credit_value", store=False)

	'''
    @api.onchange('reference_id')
    def _onchange_request_id(self):
        result = {}
        if self.reference_id:
            result['domain'] = {'ref': [('department', '=', self.request_id.department_id.id)]}
        return result
	'''