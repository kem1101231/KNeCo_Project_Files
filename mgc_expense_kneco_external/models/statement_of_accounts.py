from odoo import api, models, fields
from datetime import datetime, date, timedelta
from calendar import monthrange
from odoo.exceptions import ValidationError, UserError

class StatementOfAccounts(models.Model):
	_name = "mgc.expense.soa"
	_inherit = ['mail.thread', 'ir.needaction_mixin']
	_description = 'Statement of Accounts'
	_order = 'id desc, name desc'

	@api.depends('included_payables')
	def _get_total_amount(self):
		for payable in self:
			total_amount = 0
			for payable_line in payable.included_payables:
				if payable_line.payable_id.state != 'draft':
					amount = payable_line.payable_id.amount
					total_amount = total_amount + amount
			
			payable.total_amount = total_amount		
	
	@api.depends('included_payables')
	def _get_total_tax(self):
		for payable in self:
			
			total_tax = 0
			for payable_line in payable.included_payables:
				if payable_line.payable_id.state != 'draft':
					tax = payable_line.tax_amount
					total_tax = total_tax + tax

			payable.total_tax = total_tax	
	
	@api.depends('included_payables')
	def _get_total_vat_value(self):
		for payable in self:
			
			total_tax = 0
			for payable_line in payable.included_payables:
				if payable_line.payable_id.state != 'draft':
					tax = payable_line.payable_cost_of_vat
					total_tax = total_tax + tax

			payable.total_cost_of_vat = total_tax	
	
	@api.depends('included_payables')
	def _get_total_balance_amount(self):
		for payable in self:

			total_balance_amount = payable.total_amount - payable.total_tax
			
			payable.balance_total = total_balance_amount
	
	@api.depends('included_payables')
	def _get_total_amount_after_vat(self):
		for payable in self:
			total_amount = 0
			for payable_line in payable.included_payables:
				if payable_line.payable_id.state != 'draft':
					amount = payable_line.payable_cost_after_vat
					total_amount = total_amount + amount
			
			payable.total_amount_after_vat = total_amount

	@api.depends('included_payables')
	def _get_total_computed_tax_value(self):
		for payable in self:

			total_balance_amount = payable.total_tax
			
			payable.total_tax_amount = total_balance_amount

	# =======================================================================

	@api.depends('included_payables')
	def _get_total_to_cater_amount(self):
		for payable in self:
			total_amount = 0
			for payable_line in payable.included_payables:
				if payable_line.payable_id.state != 'draft':
					amount = 0
					#if payable_line.
					if  payable_line.to_be_catered == '1':
						amount = payable_line.non_taxed_catered_value
						total_amount = total_amount + amount
				
			payable.total_to_cater_amount = total_amount		
	
	@api.depends('included_payables')
	def _get_total_to_cater_tax(self):
		for payable in self:
			
			total_tax = 0
			for payable_line in payable.included_payables:
				if payable_line.payable_id.state != 'draft':
					if  payable_line.to_be_catered == '1':
						tax = payable_line.catered_tax_amount
						total_tax = total_tax + tax

			payable.total_to_cater_tax = total_tax	
	
	@api.depends('included_payables')
	def _get_total_to_cater_balance_amount(self):
		for payable in self:
	
			total_balance_amount = payable.total_to_cater_amount - payable.total_to_cater_tax
			
			payable.balance_to_cater_total = total_balance_amount
	
	@api.depends('included_payables')
	def _get_total_to_cater_amount_after_vat(self):
		for payable in self:
			total_amount = 0
			for payable_line in payable.included_payables:
				if payable_line.payable_id.state != 'draft':
					if payable_line.to_be_catered == '1':
						amount = payable_line.taxed_catered_value
						total_amount = total_amount + amount
				
			payable.total_to_cater_amount_after_vat = total_amount		
	
	@api.depends('included_payables')
	def _get_total_to_cater_vat_value(self):
		for payable in self:
			
			total_tax = 0
			for payable_line in payable.included_payables:
				if payable_line.payable_id.state != 'draft':
					if payable_line.to_be_catered == '1':
						tax = payable_line.catered_va_tax_value
						total_tax = total_tax + tax

			payable.total_to_cater_cost_of_vat = total_tax	
	
	@api.depends('included_payables')
	def _get_total_to_cater_computed_tax_value(self):
		for payable in self:

			total_balance_amount = payable.total_to_cater_tax
			
			payable.total_to_cater_tax_amount = total_balance_amount

	# =======================================================================

	@api.depends('included_payables')
	def _get_total_catered_taxed_amount(self):
		for payable in self:
			total_amount = 0
			total_untaxed_amount = 0
			total_tax = 0

			for payable_line in payable.included_payables:
				if payable_line.payable_id.state != 'draft':
					total_amount = total_amount + payable_line.payable_id.catered_amount
					total_untaxed_amount = total_untaxed_amount + payable_line.payable_id.catered_untaxed_amount
					total_tax = total_tax + payable_line.payable_id.catered_tax_amount

			
			payable.total_taxed_catered = total_amount
			payable.total_untaxed_catared = total_untaxed_amount
			payable.total_all_tax_amount = total_tax	
	
	# =========================================================
	
	@api.multi
	def confirm_soa(self):
		for soa in self:
			if soa.balance_to_cater_total != 0:
				soa.state = 'confirm'

				for line in self.included_payables:
					line.update({'state': 'confirm'})

			else:
				raise ValidationError("It seems that you want to confirm this SOA without the intention of paying any amount to it.\nThat not good you know.\nPlease select a payable on the list and fill proper amount to it.")

	@api.multi
	def validate_soa(self):
		for soa in self:
			soa.state = 'validate'

			for payable_line in soa.included_payables:
				
				journal_gen_id = self.env['account.move'].search([('id','=',payable_line.payable_id.journal_id.id)])

				if journal_gen_id.state != 'posted':

					payable_line.state = 'valid'
					
					payable_data = self.env['mgc.expense.base'].search([('id','=', payable_line.payable_id.id)],limit=1)
					payable_data.validate_payable()


	name = fields.Char(string="SOA Name")
	soa_code = fields.Char(string="Identification Number") 
	vendor = fields.Many2one(string="Vendor", comodel_name="res.partner")
	vendor_name = fields.Char(string="Vendor Name", related="vendor.name", store=False)
	adrress = fields.Char(string="Address")
	vendor_vat = fields.Boolean(string="VAT", related="vendor.vatable_vendor", store=False)
	vendor_tin = fields.Char(string="T.I.N.", related="vendor.tin_number", store=False)
	default_term = fields.Integer(string="Default Term (days)", related="vendor.default_term")
	vendor_reputation = fields.Selection(string="Vendor Reputation", selection=[('good','Good'),('nor','Inconsistent'),('bad','Bad')], related="vendor.vendor_reputation", store=False)
	included_payables = fields.One2many(string="Included Payables", comodel_name="mgc.expense.soa.line", inverse_name="soa_id")
	currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)
	
	total_amount = fields.Monetary(string="Total Cost of Invoices", compute="_get_total_amount")
	total_amount_after_vat = fields.Monetary(string="Total after VAT", compute="_get_total_amount_after_vat")
	total_cost_of_vat = fields.Monetary(string="Total VAT Value", compute="_get_total_vat_value")
	total_tax = fields.Monetary(string="Total Taxes", compute="_get_total_tax")
	balance_total = fields.Monetary(string="Total Taxed Amount", compute="_get_total_balance_amount")

	total_to_cater_amount = fields.Monetary(string="Total to be Paid", compute="_get_total_to_cater_amount")
	total_to_cater_amount_after_vat = fields.Monetary(string="Total after VAT", compute="_get_total_to_cater_amount_after_vat")
	total_to_cater_tax = fields.Monetary(string="Total Taxes", compute="_get_total_to_cater_tax")
	balance_to_cater_total = fields.Monetary(string="Amount for Disbursement", compute="_get_total_to_cater_balance_amount")
	total_to_cater_cost_of_vat = fields.Monetary(string="Total VAT Value", compute="_get_total_to_cater_vat_value")

	total_tax_amount = fields.Monetary(string="Total Withholding Tax", compute="_get_total_computed_tax_value")
	total_to_cater_tax_amount = fields.Monetary(string="Withholding Tax Total", compute="_get_total_to_cater_computed_tax_value")
	total_catered_tax_amount = fields.Monetary(string="To Cater Computed Tax", compute="_get_total_to_cater_computed_tax_value")

	total_taxed_catered = fields.Monetary(string="Catered Taxed Amount", compute="_get_total_catered_taxed_amount")
	total_untaxed_catared = fields.Monetary(string="Catered Untaxed Amount", compute="_get_total_catered_taxed_amount")
	total_all_tax_amount = fields.Monetary(string="Catered Tax Amount", compute="_get_total_catered_taxed_amount")
	total_tax_value_amount = fields.Monetary(string="Catered Tax Amount", compute="_get_total_catered_taxed_amount")

	disbursement_list = fields.One2many(string="Payment Transactions", comodel_name="mgc.expense.transactions", inverse_name="soa_id")

	state = fields.Selection(string="State", selection=[('draft','Draft'),('confirm','Confirmed'),('validate','Validated'),('tag','Tagged'), ('pay','On Payment'),('paid','Paid')], default="draft", track_visibility='onchange')

	# @api.onchange('vendor')
	# def _onchange_vendor(self):
	# 	if self.vendor:
	# 		info_data = self.env['res.partner.vendor.additional.information'].search([('vendor','=',self.vendor.id)],limit=1)
	# 		self.vendor_vat = info_data.vatable_vendor
	# 		self.vendor_tin = info_data.tin_number
	# 		self.vendor_reputation = info_data.vendor_reputation
	

	@api.model
	def create(self, values):
			now = date.today()
			if 'vendor' in values:
				if values['vendor']:
					monthData = monthrange(now.year, now.month)

					sequence = self.search_count([('id', '!=', '0'),('create_date','>=', str(now.year)+'-'+str(now.month)+'-1'),('create_date','<=',str(now.year)+'-'+str(now.month)+'-'+str(monthData[1]))])
					years = date.strftime(date.today(), '%y')
					month = date.strftime(date.today(), '%m')
					gen_name = 'SOA-' + str(years) + '-'+str(month)+'-' + '{:05}'.format(sequence + 1)
					values['soa_code'] = gen_name
					values['name'] = gen_name 
					# +' @ <'+values['vendor_name']+'>'

			result =  super(StatementOfAccounts, self).create(values)

			return result



class StatementOfAccountsLine(models.Model):
	_name="mgc.expense.soa.line"

	@api.depends('payable_id')
	def _get_total_after_vat(self):
		for payable in self:
			payable_cost = 0
			vat_value = 0

			if payable.payable_id.compute_tax == '1':
				payable_cost = payable.payable_cost / 1.12
				vat_value = payable.payable_cost - payable_cost
			else:
				payable_cost = payable.payable_cost

			payable.payable_cost_after_vat = payable_cost
	
	@api.depends('payable_id')
	def _get_total_vat_value(self):
		for payable in self:
			payable_cost = 0
			vat_value = 0

			if payable.payable_id.compute_tax == '1':
				payable_cost = payable.payable_cost / 1.12
				vat_value = payable.payable_cost - payable_cost
			else:
				payable_cost = payable.payable_cost

			payable.payable_cost_of_vat = vat_value
	
	@api.depends('payable_id')
	def _get_total_of_catered_vat_value(self):
		for payable in self:
			payable_cost = 0
			vat_value = 0

			if payable.payable_id.compute_tax == '1':
				payable_cost = payable.non_taxed_catered_value / 1.12
				vat_value = payable.non_taxed_catered_value - payable_cost
			else:
				payable_cost = payable.non_taxed_catered_value

			payable.catered_va_tax_value = vat_value
	

	@api.depends('payable_id')
	def _get_total_of_catered_after_vat(self):
		for payable in self:
			payable_cost = 0
			vat_value = 0

			if payable.payable_id.compute_tax == '1':
				payable_cost = payable.non_taxed_catered_value / 1.12
				vat_value = payable.non_taxed_catered_value - payable_cost
			else:
				payable_cost = payable.non_taxed_catered_value

			print("==========================")
			print(payable_cost)
			payable.taxed_catered_value = payable_cost
	
	@api.depends('tax_used')
	def _get_tax_used_value(self):
		for payable in self:
			if len(payable.tax_used) != 0:
				total_tax_value = 0
				baseAmount = 0

				if payable.payable_id.compute_tax == '1':
					if payable.soa_id.vendor_vat == True:
						baseAmount = payable.payable_cost_after_vat	
				
					else:
						
						baseAmount = payable.payable_cost

					for tax_line in payable.tax_used:
						total_tax_value = total_tax_value + baseAmount * (tax_line.amount * 0.01)

					payable.tax_amount = total_tax_value

			else:
				payable.tax_amount = 0
	
	@api.depends('tax_used','non_taxed_catered_value')
	def _get_tax_used_for_catered_value(self):
		for payable in self:
			if len(payable.tax_used) != 0:
				total_tax_value = 0
				baseAmount = 0
				
				if payable.payable_id.tax_cater_status == False:
					if payable.payable_id.compute_tax == '1':
						if payable.soa_id.vendor_vat == True:
							baseAmount = payable.taxed_catered_value
						
						else:
							
							baseAmount = payable.non_taxed_catered_value

						for tax_line in payable.tax_used:
							total_tax_value = total_tax_value + baseAmount * (tax_line.amount * 0.01)

						payable.catered_tax_amount_dummy = total_tax_value

			else:
				payable.catered_tax_amount_dummy = 0
	
	@api.depends('tax_used','non_taxed_catered_value')
	def _get_to_catered_value(self):
		for payable in self:
			cater_value = payable.non_taxed_catered_value - (payable.catered_va_tax_value + payable.catered_tax_amount)
			payable.cater_value = cater_value

	soa_id = fields.Many2one(string="S.O.A.", comodel_name="mgc.expense.soa")
	soa_vendor = fields.Many2one(comodel_name="res.partner", store=False, related="soa_id.vendor")

	currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)
	payable_id = fields.Many2one(string="Payable", comodel_name="mgc.expense.base")
	payable_receipt_number  = fields.Char(string="Receipt Reference", related="payable_id.receipt_number", store=False)
	payable_cost = fields.Float(string="Payable Invoice Amount", store=False, related="payable_id.amount")
	payable_cost_after_vat = fields.Monetary(string="Total after VAT", compute="_get_total_after_vat")
	payable_cost_of_vat = fields.Monetary(string="VAT Value", compute="_get_total_vat_value")
	payable_state = fields.Selection(selection=[('draft', 'Draft'),('check','Checking'),('cancel','Canceled'),('done','Done'),('confirm','Confirmed'),('open','Open'),('tag','Tagged'), ('paid','Paid')], related="payable_id.state")
	payable_type = fields.Selection(string="Payable Reference", selection=[('cash','Cash Request'),('purchase','Purchase Order')], store=False, related="payable_id.request_type_id_type")
	payable_usage = fields.Selection(selection=[('item','Payment for Purchased Items'),('service','Payment for Rendered Service/s'),('bill', 'Payment for Bills'), ('cash','Advance for Operation') ], string="Expense as", store=False, related="payable_id.expense_type")
	
	tax_used = fields.Selection(string="Taxes", selection=[(0.01,'1%'),(0.02,'2%')], related="payable_id.tax_ids")
	tax_amount = fields.Monetary(string="W/holding Tax Value") #compute="_get_tax_used_value"
	#
	catered_tax_amount_dummy = fields.Monetary(string="Withholding Tax Value", compute="_get_tax_used_for_catered_value", store=False)
	catered_tax_amount = fields.Monetary(string="W/holding Tax values (Catered)")

	to_be_catered = fields.Selection(string="Include for Payment", selection=[('1','Yes'),('0','No'),('9','Catered')], default="0")
	cater_value_limit = fields.Monetary(string="To be Catered Cost Limit")
	non_taxed_catered_value = fields.Monetary(string="To be Paid Amount")
	taxed_catered_value = fields.Monetary(string="Net of V.A.T.", compute="_get_total_of_catered_after_vat")
	catered_va_tax_value = fields.Monetary(string="Input Tax Value", compute="_get_total_of_catered_vat_value")
	
	cater_value = fields.Monetary(string="Cost to Cater", compute="_get_to_catered_value")
	catered_amount = fields.Monetary(string="Amount Paid", related="payable_id.catered_amount")
	catered_untaxed_amount = fields.Monetary(string="Amount Untaxed Paid", related="payable_id.catered_untaxed_amount")
	catered_on_total_tax_amount = fields.Monetary(string="Tax Amount Paid", related="payable_id.catered_tax_amount")

	tax_cater_status = fields.Boolean(string="Tax Deducted", related="payable_id.tax_cater_status")
	
	state = fields.Selection(string="State", selection=[('draft','Draft'),('confirm','Confirmed'),('valid','Validated'),('pay','For Payment'),('paid','Paid')], default="draft")

	@api.onchange('catered_tax_amount_dummy')
	def _onchange_catered_tax_amount_dummy(self):
		if self.catered_tax_amount_dummy:
			self.tax_amount = self.payable_id.tax_amount_value
		
			if self.payable_id.tax_cater_status == False:
				self.catered_tax_amount = self.tax_amount

	@api.onchange('to_be_catered')
	def _onchange_to_be_catered(self):
		if self.to_be_catered:

			amount_to_cater = 0
			amount_to_cater_non_taxed = 0
			if self.to_be_catered == '1':
				
				if self.soa_id.vendor_vat == True:
					amount_to_cater = self.payable_cost_after_vat - self.tax_amount - self.catered_amount
				else:
					amount_to_cater = self.payable_cost - self.tax_amount - self.catered_amount
				
				amount_to_cater_non_taxed = self.payable_cost - self.catered_untaxed_amount

			else:
				amount_to_cater = 0
				amount_to_cater_non_taxed = 0

			# self.cater_value_limit = amount_to_cater
			# self.cater_value = amount_to_cater
			self.non_taxed_catered_value = amount_to_cater_non_taxed

	@api.onchange('tax_used')
	def _onchange_tax_used(self):
		if self.tax_used:
				
			total_tax_value = 0
			if self.payable_id.compute_tax == '1':
				baseAmount = 0
				if self.soa_id.vendor_vat == True:
					baseAmount = self.taxed_catered_value
				else:
					baseAmount = self.non_taxed_catered_value

				for tax_line in self.tax_used:
					total_tax_value = total_tax_value + baseAmount * (tax_line.amount * 0.01)

			self.catered_tax_amount = total_tax_value

	@api.multi
	def write(self, vals):

		result = super(StatementOfAccountsLine, self).write(vals)
		for rec in self:
			if rec.state == 'valid':

				with_tax = False
				tax_value = 0

				if len(rec.tax_used) != 0:
					with_tax = True
					tax_value = tax_value + rec.tax_amount

				if rec.soa_id.vendor_vat == True:
					with_tax = True
					tax_value = tax_value + rec.payable_cost_of_vat


				payable = self.env['mgc.expense.base'].search([('id','=', rec.payable_id.id),],limit=1)
				
				if rec.payable_id.compute_tax == '1':
					payable.update({
									'tax_amount_value': rec.tax_amount,	
									'total_tax_amount_value': tax_value,
									'with_tax': with_tax,
									'vated_payable':rec.soa_id.vendor_vat,
									})

		return result

	# @api.onchange('cater_value')
	# def _onchange_cater_value(self):
	# 	if self.cater_value:
	# 		print("========================")
	# 		print(self.cater_value)
	# 		print(self.cater_value_limit)

	# 		if self.cater_value > self.cater_value_limit:
	# 			self.cater_value = self.cater_value_limit
	# 			raise ValidationError("Invalid Amount. \n * Your given amount exceeds to the actual amount to be paid.")


	# @ai.onchange('payable_id')		
	
# class ConductedPayments(models.Model):
# 	_name = ''
