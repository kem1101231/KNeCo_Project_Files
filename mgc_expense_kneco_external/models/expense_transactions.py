from odoo import api, models, fields
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError, UserError
from calendar import monthrange
from num2words import num2words
from odoo_rpc_connection import OdooRPC_Connection




class ExpenseTransaction(models.Model):
	_name = 'mgc.expense.transactions'
	_inherit = ['mail.thread', 'ir.needaction_mixin']
	_description = 'Disbursement'
	_order = 'id desc'


	@api.depends('payable_list.amount_to_cater')
	def _amount_all(self):
		for expense in self:
			amount_cater_all = 0
			if expense.trans_budget != 0:
				for line in expense.payable_list:
					amount_cater_all = amount_cater_all + line.amount_to_cater

				expense.update({
				    'total_trans_amount': expense.trans_budget - amount_cater_all,
				})

	@api.depends('soa_payable_list')
	def _amount_all_for_check(self):
		for expense in self:
			amount_cater_all = 0

			total_amount = 0
			total_tax = 0
			total_payable_amount = 0
			total_catered_amount = 0
			total_catered_tax_amount = 0

			# for line in expense.soa_list:
			# 		if line.to_be_catered == '1':
			# 			total_amount = total_amount + line.cater_value
			# 			total_tax = total_tax + float(line.tax_amount) + float(line.payable_cost_of_vat)
			# 			total_payable_amount = total_payable_amount + float(line.payable_cost)
			# 			total_catered_amount = total_catered_amount + float(line.non_taxed_catered_value)
			# 			total_catered_tax_amount = total_catered_tax_amount + (float(line.catered_va_tax_value) + float(line.catered_tax_amount))
			# 		
			
			for line in expense.soa_payable_list:
					print(line.taxed_amount_to_cater)
					total_amount = total_amount + line.taxed_amount_to_cater
					total_tax = total_tax + float(line.tax_value)
					total_payable_amount = total_payable_amount + float(line.payable_cost)
					total_catered_amount = total_catered_amount + float(line.untaxed_amount_to_cater)
					total_catered_tax_amount = total_catered_tax_amount + float(line.tax_value)

			expense.update({
				    'check_amount': total_amount,
				    'amount_total': total_amount,
				    'amount_tax': total_tax,
				    'payable_base_total': total_payable_amount,
				    'catered_base_total': total_catered_amount,
				    'amount_of_catered_tax': total_catered_tax_amount,
				})

			print("Done Saving")


	@api.multi		
	def cancel_payment(self):
		for expense in self:
			
			print("++++++++++++++++++++++++++++++++++++++++++++++")
			print(expense.state)
			if expense.state == 'done':

				soa = self.env['mgc.expense.soa'].search([('id','=', expense.soa_id.id)], limit=1)

				soa.update({'state':'validate',})

				for line in expense.soa_payable_list:
					soa_line = self.env['mgc.expense.soa.line'].search([('payable_id','=', line.payable_id.id)], limit=1)

					payable = self.env['mgc.expense.base'].search([('id','=',line.payable_id.id)],limit=1)
					
					print("==========================================")
					print("Taxed: "+str(line.taxed_amount_to_cater))
					print("Untaxed: "+str(line.untaxed_amount_to_cater))
					print("Tax: "+str(line.tax_value))
					
					payable.update({'state':'open',
									'is_catered':True,
									})
					payable.update_catered_values(line.taxed_amount_to_cater, line.untaxed_amount_to_cater, line.tax_value, 'sub')

				check = self.env['mgc.expense.checks'].search([('id','=', expense.expense_check.id)], limit=1)
				check.update({'state': 'cancel',})
				self.journal_update('unpost', expense.journal_entry_id.id)
			
			expense.update({'state':'cancel'})

	
	def reset_as_draft(self):
		for expense in self:
			expense.update({'state':'check',})


	
 	def journal_update(self, update_type, id_entry):
	 	journal = self.env['account.move'].search([('id','=', id_entry)], limit=1)
	 	journal_state = ''
	 	journal_line_reconcile = False

	 	if update_type == 'post':
	 		journal.write({'state': 'posted'})

	 		for journal_item in journal.line_ids:
	 			item = self.env['account.move.line'].search([('id','=',journal_item.id),])
	 			item.write({'reconciled':True})

	 	else:
	 		self.env.cr.execute("update account_move set state = 'draft' where id = "+ str(id_entry))

	 		for journal_item in journal.line_ids:
	 			self.env.cr.execute("update account_move_line set reconciled = FALSE where id = "+str(journal_item.id))


	@api.depends('soa_payable_list')
	def _check_for_efo(self):
		for expense in self:

			check_data = False
			check_id = 0

			for line in expense.soa_payable_list:
				if line.payable_id.is_efo == True:
					check_data = True
					check_id = line.payable_id.request_reference_id


			expense.for_efo = check_data
			expense.efo_request_id = check_id
			expense.update({'for_efo':check_data,'efo_request_id':check_id})


	@api.multi
	def validate_expense(self):
		for expense in self:

			# Journal Update  =================================================

			journal = self.env['account.move'].search([('id', '=', expense.journal_entry_id.id),])

			if journal.state != 'posted':

				journal.write({'state':'posted'})

				for journal_item in journal.line_ids:
					item = self.env['account.move.line'].search([('id','=',journal_item.id),])
					item.write({'reconciled':True})
			
			# check update ======================================================

			check = self.env['mgc.expense.checks'].search([('id','=', expense.expense_check.id)],limit=1)
			check.update({'state':'print'})

			# SOA update ========================================================
			 
			soa = self.env['mgc.expense.soa'].search([('id','=', expense.soa_id.id)], limit=1)
			
			for soa_line in soa.included_payables:
				soa_line.update({'state':'draft',})
			
			for payable_line in expense.soa_payable_list:
					payable_invoice = self.env['account.invoice'].search([('id', '=', payable_line.payable_id.vendor_bill_ext.id),], )
					payable = self.env['mgc.expense.base'].search([('id', '=', payable_line.payable_id.id),],limit=1)
					soa_line = self.env['mgc.expense.soa.line'].search([('payable_id','=', payable_line.payable_id.id)], limit=1)
					

					#if payable_line.payable_id.request_type_id_type == 'purchase':
					#	
					
					is_catered = False
					balance_amount = 0
					balance_tax_amount = 0
					state = ''
					catered_tax_value = 0

					if round(payable_line.payable_id.balance_amount, 2)  == round(payable_line.taxed_amount_to_cater, 2) or round(payable_line.payable_id.final_amount, 2) == round(payable_line.taxed_amount_to_cater, 2):
						state = 'paid'
						is_catered = False
						balance_amount = 0
						balance_tax_amount = 0
						catered_tax_value = 0

						if payable_line.payable_id.request_type_id_type == 'purchase':
							self.env.cr.execute("update account_invoice set state = 'paid' where id = "+str(payable_line.payable_id.vendor_bill_ext.id)+"")

					else:
						state = 'tag'
						is_catered = True 
						balance_amount = payable_line.payable_id.balance_amount - payable_line.taxed_amount_to_cater
						catered_tax_value = payable_line.payable_id.catered_tax_amount + payable_line.tax_value
						balance_tax_amount = payable_line.payable_id.total_tax_amount_value + payable_line.tax_value


					payable.update({
									'state': state,
									'catered_amount': payable_line.payable_id.catered_amount + payable_line.taxed_amount_to_cater,
									'catered_untaxed_amount': payable_line.payable_id.catered_untaxed_amount + payable_line.untaxed_amount_to_cater,
									'is_catered': is_catered,
									'catered_tax_amount':catered_tax_value,
									'balance_amount':balance_amount,
									'balance_tax_amount':balance_tax_amount,
									#'balance_untaxed_amount':payable_line.payable_cost - payable_line.catered_untaxed_amount,
									'tax_cater_status':True,
								})

					soa_line_state =  'draft'
					to_be_catered = '0'
					
					if state == 'paid':
						soa_line_state = 'paid'
						to_be_catered = '9'

					print(soa_line_state)
					soa_line.update({
											'state':soa_line_state,
											'non_taxed_catered_value':0,
											'catered_tax_amount':0,
											'to_be_catered': to_be_catered,
											'cater_value':0,
											'taxed_catered_value':0,
											'catered_va_tax_value':0,

							})

			soa_state = soa.state
			if soa.balance_total == soa.total_taxed_catered:
				soa_state = 'paid'
			else:
				soa_state = 'pay'	

			print(soa_state)
			soa.update({'state':soa_state})

			expense.validated_by = int(self.env.user.id)

			if expense.for_efo == True:

				request_search = self.env['mgc.expense.access.configuration'].search([('access_type', '=', 'request'),])
				odoorpcConnection = OdooRPC_Connection()
				odoorpcConnection.set_connection(request_search.server_ip,request_search.port_number,request_search.dbname,request_search.username,request_search.password)
				rpcClass = odoorpcConnection.odoo_class()

				request = rpcClass.env['account.request'].search([('id','=', expense.efo_request_id)], limit=1)
				requestData = odoorpcConnection.odoo.env['account.request'].browse(int(request[0]))


				print("_____________________________ *****")
				
				print(requestData)
				print(requestData.employee_id.id)
				print("::::::::::::::::::::::::::")
				print(expense.efo_request_id) 

				liquidation = odoorpcConnection.odoo.env['account.request.liquidation'].create({
																									'name':"LT for RF: " + requestData.name +" @ " + expense.name,
																									'total_cost':float(expense.check_amount),
																									'state': 'check',
																									'request_reference': expense.efo_request_id,
																									'employee_id':requestData.employee_id.id,
																									'check_reference':expense.account_name.name + " / " + expense.expense_check.name,
																									'fund_source_type':'corpo',
																									'currency_id':requestData.currency_id.id,
																			})
				

				gen_liquidation = self.env['mgc.expense.liquidation'].create({																					
																					'name':"LT for RF: " + requestData.name +" @ " + expense.name,
																					'req_advance_amount':float(expense.check_amount),
																					'state': 'check',
																					'liquidation_id_ref':liquidation,
																					'request_number': requestData.name,
																					'request_date': requestData.create_date,
																					'requester':requestData.employee_id.name,
																					'request_purpose':requestData.purpose,
																					'check_reference':expense.expense_check.name,
																					'expense_id':expense.id,
																					'expense_vendor':expense.vendor.id,
																					'check_receiver':expense.check_accounted_personel.id,

																			})


				for line in requestData.request_line:
					liquid_line = odoorpcConnection.odoo.env['account.request.liquidation.line'].create({
										
										'liquidation_id': liquidation,
										'description':line.description.name,
										'total_amount':line.price_subtotal,
										'quantity':line.quantity,
										'per_unit_price': line.price_unit,
										'currency_id':requestData.currency_id.id,
						})

					self.env['mgc.expense.liquidation.line'].create({

										'liquidation_id': gen_liquidation.id,
										'liquidation_id_ref':liquid_line,
										'description':line.description.name,
										'amount_budgeted':line.price_subtotal,
						})

			expense.state = 'done'

	# @api.depends('soa_list')
	# def _get_total_tax_value(seslf):
	# 	tax_value = 0


	name = fields.Char(string="Expense Number") 
	reference_type = fields.Selection(selection=[('request','Request')	,('payable','Payable')], string="Expense Reference", default="payable")
	trans_budget = fields.Monetary(string="Transaction Budget", store=False)
	total_trans_amount = fields.Monetary(string="Budget Balance", store=False, compute="_amount_all")
	soa_id = fields.Many2one(string="Statement of Account", comodel_name="mgc.expense.soa")
	vendor = fields.Many2one(comodel_name="res.partner", string="Vendor/Biller")
	source_payable = fields.Selection(selection=[('payable','Payables'),('soa','Statement of Accounts')], string="Source Document", default="payable") 
	payable_list = fields.One2many(comodel_name="mgc.expense.transactions.payable.line", inverse_name="expense_id", string="Included Payables")
	soa_list = fields.One2many(related="soa_id.included_payables")
	soa_payable_list = fields.One2many(comodel_name="mgc.expense.transactions.soa.list", inverse_name="expense_id", string="SOA Payable List")

	#==========================================
	'''
	request_id = fields.Many2one(comodel_name="account.request", string="Request Number",  domain="[('request_type_id.type','!=','purchase')]")
	request_dept = fields.Char(related="request_id.department_id.name", string="Department",store=False)
	request_bu = fields.Char(related="request_id.company_id.name", string="Business Unit",store=False)
	request_purpose = fields.Text(related="request_id.purpose", string="Purpose",store=False)
	request_cost = fields.Monetary(related="request_id.amount_total", string="Request Amount", store=False)
	request_type = fields.Char(related="request_id.request_type_id.name", string="Type",store=False)
	request_name = fields.Char(related="request_id.request_type_line_id.name", string="Name",store=False)
	'''
	#request_type_id_type = fields.Char(string="Request Type", store=False)
	

	currency_id = fields.Many2one('res.currency', 'Currency', store=False, default=lambda self: self.env.user.company_id.currency_id.id)
	journal_entry_id = fields.Many2one(comodel_name="account.move", string="Journal Entry")
	journal_id = fields.Many2one(comodel_name="account.journal", string="Journal", required=True)
	credit_entry = fields.Many2one(comodel_name="account.account",string="Credit Entry", related="account_name.credit_account")
	journal_item = fields.One2many(related="journal_entry_id.line_ids")

	#==========================================
	payable_id = fields.Many2one(comodel_name="mgc.expense.base", string="Payable Number")
	payable_purpose = fields.Text(related="payable_id.purpose", string="Purpose",store=False)
	payable_cost = fields.Float(related="payable_id.amount", string="Amount",store=False)
	payable_request_reference = fields.Char(string="Request Reference")
	#payable_request_reference = fields.Many2one(related="payable_id.request_reference", comodel_name="account.request", string="Request References", store=False)
	#payable_location = fields.Char(related="payable_location.request_type_line_id.name", string="Name",store=False)

	expense_check = fields.Many2one(string="Check", comodel_name="mgc.expense.checks")
	check_state = fields.Selection(string="State", selection=[('unreconcile','Draft'),('check','Checking'),('print','Print Check'),('validate','Released'),('cancel','Canceled'),('reconcile','Reconciled')], related="expense_check.state")
	check_number = fields.Char(string="Check Number", required=True)
	check_amount = fields.Monetary(string="Amount", compute="_amount_all_for_check")
	check_date = fields.Date(string="Date", required=True)
	check_accounted_personel = fields.Many2one(string="Check Receiver", comodel_name="res.partner")
	account_name = fields.Many2one(comodel_name="mgc.expense.bank_accounts", string="Bank Account", required=True)
	account_number = fields.Char(string="Account Number", related="account_name.account_number",store=False)
	bank_id = fields.Many2one(store=False, string="Bank", comodel_name="mgc.expense.banks", related="account_name.bank_id")
	bu_id = fields.Many2one(store = False, string="Business Unit", comodel_name="mgc.expense.bu", related="account_name.bu_id")

	is_advances = fields.Boolean(string="Advance for Operation")
	amount_total = fields.Monetary(string="Total Amount")
	amount_tax = fields.Monetary(string="Total Tax", compute="_amount_all_for_check")
	payable_base_total = fields.Float(string="Payable Amount", compute="_amount_all_for_check")
	catered_base_total = fields.Float(string="Payable Catered Amount", compute="_amount_all_for_check")
	amount_of_catered_tax = fields.Monetary(string="Total Catered Tax", compute="_amount_all_for_check")

	purpose = fields.Text(string="Purpose")
	state = fields.Selection(selection=[('draft','Draft'),('check','Checking'),('done','Done'),('valid','Validated'),('cancel','Cancelled')], string="State", default="draft", track_visibility='onchange')
	validated_by = fields.Many2one(string="Validated By", comodel_name="res.users")

	expense_line_list = []
	expense_line = fields.One2many(comodel_name='mgc.expense.transactions.line', inverse_name='expense_id', string="Expense Line")
	for_efo = fields.Boolean(string="Advance/Expense for Operation", compute="_check_for_efo")
	efo_request_id = fields.Integer("Request ID")

	@api.model
	def create(self, values):
		now = date.today()
		if 'reference_type' in values:
			if values['reference_type']:
				monthData = monthrange(now.year, now.month)

				sequence =  self.search_count([('id', '!=', '0'),('create_date','>=', str(now.year)+'-'+str(now.month)+'-1'),('create_date','<=',str(now.year)+'-'+str(now.month)+'-'+str(monthData[1]))])
				years = date.strftime(date.today(), '%y')
				month = date.strftime(date.today(), '%m')
				values['name'] = 'D-' + str(years) + '-' + str(month) + '-' + '{:05}'.format(sequence + 1)
				values['state'] = 'check'


		
		result =  super(ExpenseTransaction, self).create(values)


		gen_check = self.env['mgc.expense.checks'].create({ 
												
												'account_number': result.account_name.id,
												'name':result.check_number,
												'check_date':result.check_date,
												'amount': result.check_amount,
												'expense_trans_id':result.id,
												'purpose': 'Payment for payables included on [ ' + str(result.name)+' ]',	
												'check_accounted_personel': result.check_accounted_personel.id,
												'state':'check',
												#'disbursement_id': result.id,
							
							})
		
		result.update({'expense_check':gen_check})
		bank_account = self.env['mgc.expense.bank_accounts'].search([('id','=', result.account_name.id)], limit=1)
		
		current_account_number = bank_account.check_number_start
		bank_account.update({'check_number_start':current_account_number + 1})
		
		soa_id = self.env['mgc.expense.soa'].search([('id','=',result.soa_id.id)],limit=1)
		soa_id.update({'state':'tag'})


		journal_gen_id = self.env['account.move'].create({
           													'name':result.journal_id.name,
		                                                    'journal_id':result.journal_id.id,
		                                                    'date': datetime.now(),
		                                                    'company_id':self.env.user.company_id.id,
		                                                    'state':'draft',
		                    				})
		itemList = []
		total_credit = 0
		total_tax_amount = 0

		print("Jack Sparrow")
		for item in result.soa_payable_list:

				itemList.append({	'move_id':journal_gen_id.id,
	           						'account_id':item.payable_id.expense_credit_account.id,
	           						'partner_id':result.vendor.id,
	           						'name': 'Payment for '+item.payable_id.name+' through '+result.name,
	           						'debit':item.taxed_amount_to_cater,
	           						'credit':0,
	           						'date_maturity':result.check_date,
	           						'reconciled':False,
	           						'company_id':self.env.user.company_id.id,
								})
				
				# tax_value = item.payable_cost_of_vat + item.tax_amount
				# if tax_value != 0:
				# 	itemList.append({	'move_id':journal_gen_id.id,
		  #          						'account_id':item.payable_id.expense_tax_credit_account.id,
		  #          						'partner_id':result.vendor.id,
		  #          						'name': "Withholding Tax for " + item.payable_id.name,
		  #          						'debit':0,
		  #          						'credit':tax_value,
		  #          						'date_maturity':result.check_date,
		  #          						'reconciled':False,
		  #          						'company_id':self.env.user.company_id.id,
				# 					})

				# total_credit = total_credit + item.payable_cost
				# total_tax_amount = total_tax_amount + tax_value

		itemList.append({
		                    		'move_id':journal_gen_id.id,
		                    		'account_id':result.credit_entry.id,
		                    		'partner_id':result.vendor.id,
		                    		'name':result.account_name.name + "/Chk:"+result.check_number,
		                    		'debit':0,
		                    		'credit':result.check_amount,
		                    		'date_maturity':result.check_date,
		                    		'reconciled':False,
		                    		'company_id':self.env.user.company_id.id,
		                    	})
		

		journal_gen_id.update({'line_ids':itemList})
		result.update({'journal_entry_id': journal_gen_id.id})

		for payable_line in result.soa_payable_list:
			payable_id = self.env['mgc.expense.base'].search([('id','=', payable_line.payable_id.id)], limit=1)
			payable_id.update({'state':'tag'})

		return result
        
 
        # self.env['mgc.specialized.accounting.ledger'].create({  'reference_code': result.name,
        #                                                         'reference_id': result.id,
        #                                                         'reference_type': 'expense', 
        #                                                         'location_id':  result.account_location.id,
        #                                                         'description': result.purpose,
        #                                                         'account_name': result.expense_type.id,
        #                                                         'entry_type':'credit',
        #                                                         'amount': result.final_amount,
                                                                
        #                                                         })


	@api.onchange('check_number')
	def _onchange_check_number(self):
		if self.check_number:
			check = self.env['mgc.expense.checks'].search([('name','=',self.check_number), ('account_number','=',self.account_name.id)])
			# print("+++++++++++++++++++++++++++++++++++++++")
			# print(len(check))
			# print(len(check) == 0)

			if len(check) != 0:
				self.check_number = None
				warning = { 'title': 'Check Number already used', 'message' : 'Check number has already been used on a different disbursement transaction.'}

				return {'warning': warning}


	@api.onchange('check_date')
	def _onchange_check_date(self):
		if self.check_date:
			dateList = str(self.check_date).split('-')
			selDate = datetime(int(dateList[0]),int(dateList[1]),int(dateList[2]))

			if(selDate <= datetime.now() - timedelta(days=1)):
				self.check_date = None
				warning = {  'title': 'Invalid Date', 'message' : 'Date after the current date is not allowed for selection'}

				return {'warning': warning}



	@api.onchange('trans_budget')
	def _onchange_trans_budget(self):

		if self.trans_budget:
				self.total_trans_amount = self.trans_budget


	@api.onchange('request_id')
	def _onchange_request_id(self):
		if self.request_id:
			#self.request_type_id_type = str(self.request_id.request_type_id.type)
			pass
	
	@api.onchange('payable_id')
	def _onchange_payable_id(self):
		if self.payable_id:
				self.amount_total = self.payable_id.final_amount

	@api.onchange('account_name')
	def _onhange_account_name(self):
		if self.account_name:
			self.journal_id = self.account_name.journal_id.id
			self.check_number = str(self.account_name.check_number_start).zfill(10)
			self.check_date = date.today()

	@api.onchange('soa_id')
	def _onchange_soa_id(self):
		if self.soa_id:
			payable_list = []
			for payable_line in self.soa_id.included_payables:

				tax_value = 0
				if payable_line.to_be_catered == '1':
					
					if payable_line.payable_id.compute_tax == '1':

						# if self.soa_id.vendor_vat == True:
						# 	tax_value = tax_value + payable_line.catered_va_tax_value

						if len(payable_line.tax_used) != 0:
							tax_value = tax_value + payable_line.catered_tax_amount

					payable_list.append({
											'payable_id':payable_line.payable_id.id,
											'receipt': payable_line.payable_receipt_number,
											'payable_cost':payable_line.payable_cost,
											'payable_uncatered_cost':payable_line.payable_cost - payable_line.catered_untaxed_amount,
											'payable_catered_cost':payable_line.catered_untaxed_amount,
											'payable_tax_used':payable_line.tax_used,
											'untaxed_amount_to_cater': payable_line.non_taxed_catered_value,
											'tax_value': tax_value,
											'taxed_amount_to_cater': payable_line.non_taxed_catered_value - tax_value,
						})
			
			self.update({'soa_payable_list':payable_list,})

	
	@api.multi
	def print_cvj(self):

		vendor_name = self.vendor.name
		journal_line_value = []
		total_credit = 0
		total_debit = 0

		for line in self.journal_item:
			
			debit_value = '' 
			if line.debit != 0:
				debit_value = "{:,.2f}".format(float(line.debit))
			
			credit_value = ''
			if line.credit != 0:
				credit_value = "{:,.2f}".format(float(line.credit))

			journal_line_value = journal_line_value + [{
															'account':line.account_id.name,
															'debit':debit_value,
															'credit':credit_value,

													}]
			
			total_credit = total_credit + line.credit
			total_debit = total_debit + line.debit


		amount_string_list = str(round(self.check_amount, 2)).split('.')
		amount_whole = str(num2words(int(amount_string_list[0]))).title() + ' Pesos'
		amount_cent = ''

		if int(amount_string_list[1]) != 0:
			cent_value = 0
			if len(amount_string_list[1]) == 1:
				cent_value = int(amount_string_list[1]+'0')
			else:
				cent_value = int(amount_string_list[1])

			amount_cent = ' and ' + str(num2words(cent_value)).title() + ' Centavos'


		data = {'data':{ 
						 'vendor':vendor_name,
                         'journal_line':journal_line_value,
                         'total_payable_cost':"{:,.2f}".format(float(self.payable_base_total)),
                         'total_tax_cost':"{:,.2f}".format(float(self.amount_tax)),
                         'total_balance_cost':"{:,.2f}".format(float(self.check_amount)),
                         'total_credit':"{:,.2f}".format(float(total_credit)),
                         'total_debit':"{:,.2f}".format(float(total_debit)),
                         'total_catered_base':"{:,.2f}".format(float(self.catered_base_total)),
                         'soa_id': self.soa_id.name,
                         'cv_no':self.name,
                         'cv_date':self.crop_date(self.create_date),
                         'check_number':self.check_number,
                         'check_date': self.crop_date(self.check_date),
                         'check_amount_in_words': amount_whole + amount_cent,
                         'create_by': self.create_uid.name,
                         'validate_by': self.validated_by.name,
                        }
                }

		out = self.env['report'].get_action(self, 'mgc_expense_kneco_external.expense_check_form', data=data)

		return out
		# data = {'data':{'1':'The Begining'}}
		#out = self.env['report'].get_action(self, 'mgc_expense_kneco_external.check_voucher_template', data=data)

	@api.model
	def crop_date(self, dateInput):
		str_date = str(dateInput).split(' ')
		date_of_request = datetime.strptime(str_date[0], '%Y-%m-%d')#%I:%M%

		return date_of_request.strftime('%b %d, %Y')


class ExpenseTransactionLine(models.Model):
	_name = 'mgc.expense.transactions.line'

	expense_id = fields.Many2one(comodel_name="mgc.expense.transactions",string="Expense")
	#account_type = fields.Many2one('mgc.coa_legend.fs_class_chart', string="Account Type", store=False)
	account = fields.Many2one('account.account', string="Account Name", ondelete='cascade')
	description = fields.Char(string="Description")
	amount = fields.Float(string="Amount")
	entry_type = fields.Selection(selection=[('debit', 'Debit'), ('credit', 'Credit')], string="Account Type", default="debit")

	# is_shared = fields.Boolean(string="Shared Expense")
	# shareList = fields.One2many(comodel_name='mgc.expense.base.shared.bu',inverse_name='expense_line_id',string="Sharing B.U.")

	# @api.onchange('amount')
	# def  _onchange_amount(self):
	# 	if self.amount:
	# 		if self.amount <= 0:
	# 			if self.amount < 0:
	# 				self.entry_type = 'credit'
	# 				self.amount = abs(self.amount)
	# 			else:
	# 				raise ValidationError("Zero value on amount is not allowed.")    


class SOAListToCater(models.Model):
	_name = "mgc.expense.transactions.soa.list"

	@api.depends('payable_id')
	def _get_payable_uncatered_amount(self):
		for payable in self:
			payable_amount = payable.payable_cost - payable.payable_catered_cost

			payable.payable_uncatered_cost = payable_amount

	@api.depends('untaxed_amount_to_cater')
	def _get_amount_to_cater(self):
		for payable in self:

			payable_tax_amount = 0
			tax_amount = 0

			print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
			print(payable.payable_id.request_type_id_type)

			if payable.payable_id.tax_cater_status == False:
				tax_amount = payable.payable_id.tax_amount_value
				payable_tax_amount = payable.untaxed_amount_to_cater - tax_amount
			else:
				payable_tax_amount = payable.untaxed_amount_to_cater

			# if payable.payable_id.request_type_id_type == 'purchase':

			# 	payable_amount = 0
			# 	if payable.payable_id.compute_tax == '1':
			# 		if payable.payable_id.vated_payable == True:
			# 			payable_amount = payable.untaxed_amount_to_cater / 1.12
			# 		else:
			# 			payable_amount = payable.untaxed_amount_to_cater

			# 	else:
			# 		payable_amount = payable.untaxed_amount_to_cater

			# 	vat_amount = payable.untaxed_amount_to_cater - payable_amount
			# 	tax_amount = 0

			# 	for tax in payable.payable_tax_used:
			# 		tax_amount = tax_amount + (payable_amount * (tax.amount * 0.01))

			# 	payable_tax_amount = payable.untaxed_amount_to_cater - tax_amount

			# if payable.payable_id.request_type_id_type == 'cash':
			# 	payable_tax_amount = payable.payable_id.final_amount
			# 	tax_amount = payable.payable_id.tax_amount_value

			payable.taxed_amount_to_cater = payable_tax_amount
			payable.tax_value = tax_amount

	# @api.depends('payable_id')
	# def _get_payable_uncatered_amount(self):
	# 	for payable in self:
	# 		payable_amount = payable.payable_cost - payable.payable_catered_cost

	# 		payable.payable_uncatered_cost = payable_amount

	name = fields.Char(string="SOA Line")
	expense_id = fields.Many2one(comodel_name="mgc.expense.transactions", string="Disbursement Number")
	payable_id = fields.Many2one(comodel_name="mgc.expense.base", string="Payable Number")
	receipt = fields.Char(string="Receipt Number", related="payable_id.receipt_number")
	currency_id = fields.Many2one('res.currency', 'Currency', store=False, default=lambda self: self.env.user.company_id.currency_id.id)	
	payable_cost = fields.Float(string="Payable Cost", store=False, related="payable_id.amount")
	payable_uncatered_cost = fields.Monetary(string="Payable Balance Amount", compute="_get_payable_uncatered_amount")
	payable_catered_cost = fields.Monetary(string="Payable Cost", store=False, related="payable_id.catered_untaxed_amount")
	payable_tax_used = fields.Selection(selection=[(0.01,'1%'),(0.02,'2%')], related="payable_id.tax_ids")
	#to_be_catered = fields.Selection(selection=[('0','No'),('1','Yes')], default="0", string="To be Catered")
	untaxed_amount_to_cater = fields.Monetary(string="Cost to Cater (Untaxed)")
	tax_value = fields.Monetary(string="Tax Value", compute="_get_amount_to_cater", store=True)
	taxed_amount_to_cater = fields.Monetary(string="Cost to Cater (Taxed)", compute="_get_amount_to_cater", store=True)


	@api.onchange('payable_id')
	def _onchange_payable_id(self):
		if self.payable_id:
			if self.payable_id.request_type_id_type == 'cash':
				self.untaxed_amount_to_cater = self.payable_id.amount
			# self.payable_uncatered_cost = payable_amount


	# @api.onchange('payable_tax_used')
	# def _onchange_payable_tax_used(self):
	# 	if self.tax_used:
	# 		total_tax = 0
			
	# 		for tax_line in self.tax_used:

	# 			amount_base = 0
	# 			if self.soa_id.vendor_vat == True:
	# 				amount_base = self.payable_cost_after_vat
	# 			else:
	# 				amount_base = self.payable_cost

	# 			amount = amount_base * (tax_line.amount * 0.01)
	# 			total_tax = total_tax + amount

	# 		self.tax_amount = total_tax

	# # @ai.onchange('payable_id')		



class PayablesList(models.Model):
	_name = "mgc.expense.transactions.payable.line"
	_sql_constraints = [('payable_list', 'unique (payable_id)',  'Duplicate descriptions in payable line not allowed !')]
	
	#name = None
	expense_id = fields.Many2one(comodel_name="mgc.expense.transactions", string="Disbursement ID")
	expense_reference_vendor = fields.Many2one(comodel_name="res.partner", string="Vendor", related="expense_id.vendor", store=False)
	expense_spec_inst = fields.Text(string="", related="payable_id.request_spec_instr")
	payable_id = fields.Many2one(comodel_name="mgc.expense.base", string="Payable", required=True)
	payable_amount = fields.Float(string="Payable's Amount", related="payable_id.amount")
	payable_final_amount = fields.Float(string="Payable's Final Amount", related="payable_id.final_amount")
	full_catering = fields.Boolean(string="Full Payment")
	amount_to_cater = fields.Float(string="Amount to Cater")
   
    # @api.onchange('expense_id')
    # def _onchange_request_id(self):
    #     result = {}
    #     if self.request_id:
    #         result['domain'] = {'description': [('department', '=', self.request_id.department_id.id)]}
    #     return result

	@api.onchange('payable_id')
	def _onchange_payable_id(self):
		if self.payable_id:
			
			if self.expense_id.trans_budget != 0:

				if self.expense_id.total_trans_amount > 0:

					if self.payable_amount < self.expense_id.total_trans_amount:
						self.amount_to_cater = self.payable_amount
					else:
						self.amount_to_cater = self.payable_amount - (self.payable_amount - self.expense_id.total_trans_amount)	
					
				else:
					raise ValidationError("Budget can no longer cater further more payable")
			else:
				self.amount_to_cater = self.payable_amount

					# self.env['mgc.expense.transactions.line'].create({  'expense_id':self.expense_id.id,
					# 													'account':x.account_id.id,
					# 													'description':x.name,
					# 													'amount':self.amount_to_cater,
					# 													'entry_type':'debit',
																		
					# 												})

	'''		
	@api.model
	def create(self, values):
		result =  super(PayablesList, self).create(values)
		
		for record in result.expense_line:
			self.env['mgc.specialized.accounting.ledger'].create({  'reference_code': result.name,
                                                                    'reference_exp': result.id,
                                                                    'reference_type': 'expense', 
                                                                    'location_id': result.location_spec_id.id,
                                                                    'description': record.description,
                                                                    'account_name': record.account.id,
                                                                    'entry_type': record.entry_type,
                                                                    'amount': record.amount,
                                                                })

		return result
	'''



		



