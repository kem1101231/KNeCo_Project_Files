from odoo import api, models, fields
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError, UserError
from odoo_rpc_connection import OdooRPC_Connection

class MGCExpenseLiquidation(models.Model):
	
	_name = 'mgc.expense.liquidation'
	_description = 'Liquidation'
	_order = 'id desc'
	_inherit = ['mail.thread', 'ir.needaction_mixin']

	
	@api.depends('liquidation_id_ref')
	def _get_liquidation_line(self):
		for liquidation in self:
			request_search = self.env['mgc.expense.access.configuration'].search([('access_type', '=', 'request'),])

			odoorpcConnection = OdooRPC_Connection()
			odoorpcConnection.set_connection(
													request_search.server_ip, 
													request_search.port_number, 
													request_search.dbname, 
													request_search.username, 
													request_search.password
											)
			
			odoo_class = odoorpcConnection.odoo_class()
			liquidation_data = odoo_class.env['account.request.liquidation'].search([('id','=', liquidation.liquidation_id_ref)],limit=1)
			liquidation_data_full = odoo_class.env['account.request.liquidation'].browse(liquidation_data[0])
			
			for line in liquidation_data_full.liquidation_line:

				liquid_line = self.env['mgc.expense.liquidation.line'].search([('liquidation_id_ref','=',line.id)],limit=1)
				print(liquid_line)
				print({
										'or_number':line.or_number,
										'or_date':line.or_date,
										'amount_budgeted':line.total_amount,
										'amount_spent':line.amount_spent,
										'amount_balance':line.amount_balance,
										'amount_status':line.status_of_balance,

								})

				liquid_line.sudo().write({
										'or_number':line.or_number,
										'or_date':line.or_date,
										'amount_budgeted':line.total_amount,
										'amount_spent':line.amount_spent,
										'amount_balance':line.amount_balance,
										'amount_status':line.status_of_balance,

								})

				liquidation.req_expended_amount =  liquidation_data_full.total_expended	
				liquidation.req_unexpended_amount =  liquidation_data_full.total_unexpended	
				liquidation.req_reimburse_amount =  liquidation_data_full.total_reimburse	
				liquidation.state = liquidation_data_full.state
				
				liquidation.write({
										'req_expended_amount':liquidation_data_full.total_expended,
										'req_unexpended_amount':liquidation_data_full.total_unexpended,
										'req_reimburse_amount':liquidation_data_full.total_reimburse,
										'state': liquidation_data_full.state,
					})


	name = fields.Char(string="Liquidation Number")
	liquidation_id_ref = fields.Integer(string="Liquidation Reference")
	request_number = fields.Char(string="Request Number")
	request_date = fields.Date(string="Request Date")
	requester = fields.Char(string="Requester")
	request_purpose = fields.Char(string="Purpose")
	req_advance_amount = fields.Monetary(string="Advance Amount")
	req_expended_amount = fields.Monetary(string="Expended", compute="_get_liquidation_line")
	req_unexpended_amount = fields.Monetary(string="Unexpended") 	
	return_status = fields.Boolean(string="To Returned")
	req_reimburse_amount = fields.Monetary(string="To Reimburse")
	reimburse_status = fields.Boolean(string="Amount to Reimburse")
	
	expense_id = fields.Many2one(comodel_name="mgc.expense.transactions", string="Disbursement")
	
	currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)    
	expense_amount = fields.Monetary(string="Expense Cost", related="expense_id.check_amount")
	expense_vendor = fields.Many2one(comodel_name="res.partner", string="Expense Vendor", related="expense_id.vendor")
	check_id = fields.Many2one(comodel_name="mgc.expense.checks", strig="Check", related="expense_id.expense_check")
	bank_source = fields.Many2one(comodel_name='mgc.expense.bank_accounts', string="Bank Account", related="expense_id.account_name")
	
	check_receiver = fields.Many2one(comodel_name="res.partner", string="Receive By")
	total_fund_used = fields.Monetary(string="Used Funds")

	state = fields.Selection(selection=[('draft','Draft'),('check','Checking'),('confirm','Confirmed'),('valid','Validated')], string="State", default="draft", track_visibity="onchange")

	liquidation_line = fields.One2many(string="Liquidation Line", comodel_name="mgc.expense.liquidation.line", inverse_name="liquidation_id")

	@api.multi
	def test_con(self):
		for liquidation in self:
			request_search = self.env['mgc.expense.access.configuration'].search([('access_type', '=', 'request'),])

			odoorpcConnection = OdooRPC_Connection()
			odoorpcConnection.set_connection(
													request_search.server_ip, 
													request_search.port_number, 
													request_search.dbname, 
													request_search.username, 
													request_search.password
											)
			
			odoo_class = odoorpcConnection.odoo_class()
			print("==============================================")
			print(odoo_class)

	@api.multi
	def validate_liquidation(self):
		for liquidation in self:
			request_search = self.env['mgc.expense.access.configuration'].search([('access_type', '=', 'request'),])

			odoorpcConnection = OdooRPC_Connection()
			odoorpcConnection.set_connection(
													request_search.server_ip, 
													request_search.port_number, 
													request_search.dbname, 
													request_search.username, 
													request_search.password
											)
			
			odoo_class = odoorpcConnection.odoo_class()
			#odoo_class.validate_liquidation
			
			liquidation_ref = odoo_class.env['account.request.liquidation']
			#iquidation_ref.validate_liquidation()
			
			liquidation_ref.write([liquidation.liquidation_id_ref],{'state':'valid',})
			liquidation.update({'state':'valid',})


    
    # @api.onchange('debitList')
    # def _onchange_debitList(self):
    # 	if self.debitList:
    # 		self.final_amount = self.amountd


class MGCExpenseLiquidationLine(models.Model):
	_name = 'mgc.expense.liquidation.line'

	name = fields.Char(string="")
	liquidation_id = fields.Many2one(comodel_name="mgc.expense.liquidation", string="Liquidation ID")
	liquidation_id_ref = fields.Integer(string="Reference from Beyond")
	description = fields.Char(string="Description")
	or_number = fields.Char(string="OR Number")
	or_date = fields.Char(string="OR Date")
	currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)    
	amount_budgeted = fields.Monetary(string="Budgeted Amount")
	amount_spent = fields.Monetary(string="Amount Spent")
	amount_balance = fields.Monetary(string="Balance")
	amount_status = fields.Selection(selection=[('in','Unexpended'),('out','Reimbursable'),('even','Expended')],string="Status")

    
  
	

