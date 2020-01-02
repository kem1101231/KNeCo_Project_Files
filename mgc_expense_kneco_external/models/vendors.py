from odoo import api, models, fields
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError, UserError

class Vendors(models.Model):
	_name = 'mgc.expense.vendors'
	#_inherit = "res.partner"


	#@api.depends('payables')
	@api.model
	def _get_number_of_payables(self):
		for data in self:
			payable_list = self.env['mgc.expense.base'].search([('vendor_id','=',data.vendor_id.id),('state','in',['confirm','check','open', 'tag'])])

			total_cost_of_payables = 0
			total_balance_of_payables = 0

			for payable in payable_list:
				total_cost_of_payables = total_cost_of_payables + payable.final_amount
				total_balance_of_payables = total_balance_of_payables + (round(payable.final_amount, 2) - round(payable.catered_amount, 2))


			print("------------------------------------")
			print(total_balance_of_payables)
			print(total_cost_of_payables)
			data.payable_quantity = len(payable_list)
			
			data.payable_balance = total_balance_of_payables
	
	@api.depends('payables')
	def _get_cost_of_payables(self):
		for data in self:
			payable_list = self.env['mgc.expense.base'].search([('vendor_id','=',data.vendor_id.id),('state','in',['confirm','check','open', 'tag'])])

			total_cost_of_payables = 0
			total_balance_of_payables = 0

			for payable in payable_list:
				total_cost_of_payables = total_cost_of_payables + payable.final_amount
				total_balance_of_payables = total_balance_of_payables + (round(payable.final_amount, 2) - round(payable.catered_amount, 2))


			data.payable_cost = total_cost_of_payables
	
	vendor_id = fields.Many2one(string="Vendor", comodel_name="res.partner")
	name = fields.Char(string="Vendor Name")
	payables = fields.One2many(string="Payables", comodel_name="mgc.expense.base", inverse_name="payable_vendor")
	currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)
	payable_quantity = fields.Integer(string="Uncatered Payables", compute="_get_number_of_payables")
	payable_cost = fields.Monetary(string="Cost of Payables", compute="_get_cost_of_payables")
	payable_balance = fields.Monetary(string="Unpaid Balance", compute="_get_number_of_payables")


	
	@api.one
	def check_credit_limit(self):
	    partner=self.partner_id
	    new_balance=self.amount_total+partner.credit
	    if new_balance>partner.my_credit_limit:
	      params = {'invoice_amount':self.amount_total,'new_balance': new_balance,'my_credit_limit': partner.my_credit_limit}
	      return params    
	    else:
	      return True
	
	@api.multi
	def action_confirm(self):    
	    for order in self:
	      #params=order.check_credit_limit()
	      view_id=self.env['sale.control.limit.wizard']
	      new = view_id.create(params[0])    
	      return {
	        'type': 'ir.actions.act_window',
	        'name': 'Warning : Customer is about or exceeded their credit limit',
	        'res_model': 'sale.control.limit.wizard',
	        'view_type': 'form',
	        'view_mode': 'form',
	        'res_id'    : new.id,
	        'view_id': self.env.ref('control_credit_limit.my_credit_limit_wizard',False).id,
	        'target': 'new',
	      }
	   #res = super(MySale, self).action_confirm()
	    #return res


class CustomSalesDashboard(models.Model):
    _name = "custom.sales.dashboard"
 
    color = fields.Integer(string='Color Index')
    name = fields.Char(string="Name")

