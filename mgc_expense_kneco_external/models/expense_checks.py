from odoo import api, models, fields
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError, UserError
from num2words import num2words

class MGC_ExpenseChecks(models.Model):
    _name = 'mgc.expense.checks'


    name = fields.Char(string="Check Number", required=True)
    account_number = fields.Many2one('mgc.expense.bank_accounts', string="Bank Account", ondelete="cascade", required=True)
    bank_account = fields.Char(related="account_number.account_number", store=False)
    bank_source = fields.Many2one(comodel_name="mgc.expense.banks", string="Bank", store=False, related="account_number.bank_id")
    bu_source = fields.Many2one(comodel_name ="mgc.expense.bu",string="Business Unit", store=False, related="account_number.bu_id")
    bu_code = fields.Char(string="Business Unit Code", related="bu_source.bu_code")
    check_date = fields.Date(string="Check Date", required=True)
    state = fields.Selection(string="State", selection=[('unreconcile','Draft'),('check','Checking'),('print','Print Check'),('validate','Released'),('cancel','Canceled'),('reconcile','Reconciled')], default="unreconcile", track_visibility='onchange')
    recon_status = fields.Boolean(string="Reconcilation")
    recon_date = fields.Date(string="Reconcilation Date")
    amount = fields.Float(string="Amount", required=True)
    expense_trans_id = fields.Many2one('mgc.expense.transactions', string="For Expense", ondelete="cascade", required=True)
    #disbursement_id = fields.Many2one(comodel_name="mgc.expense.base", string="Disbursement  Number")
    #expense_id = fields.Many2one('mgc.expense.base',string="For Expense", ondelete="cascade", required=True)
    #expense_bu = fields.Many2one(related='expense_id.bu_id', string="")
    purpose = fields.Text(string="Purpose")
    check_accounted_personel = fields.Many2one(string="Check Receiver", comodel_name="res.partner")
    check_printed = fields.Boolean(string="Check Printed")
    printed_by = fields.Many2one(string="Printed By", comodel_name="res.users")
    check_type = fields.Selection(selection=[('type1','Type 1'),('type2','Type 2'),], string="Type")


    amountLimit = 0

    # @api.onchange('expense_id')
    # def _onchane_expense_id(self):
    #     if self.expense_id:
    #         exp_cost = self.expense_id.amount
    #         check_cost = self.expense_id.check_list_amount

    #         amountLimit = exp_cost - check_cost
    #         if(amountLimit <= 0):
                
    #             self.expense_id = None
    #             self.amount = 0

    #             warning = {'title': 'Invalid Expense as Reference', 'message' : 'Expense has been reffered to checks with the total amount equal to the expense cost. Expense is no longer available for reference.'}                
    #             return {'warning': warning}

    #         else:
    #             self.amount = amountLimit 

        #  = fields.Many2one(comodel_name="mgc.expense.bank_accounts", string="Bank Account")
        #  = fields.Selection(selection=[('in','Cash to Bank'),('out','Outgoing Funds')], string="Type", default="in")
        #  = fields.Many2one(comodel_name="mgc.expense.checks", string="Check Number (System Generated) ")
        # check_reference = fields.Char(string="Check Number (External Source)")
        # description = fields.Text(string="Description")
        #  = fields.Date(string="Transaction Date")
        #  = fields.Float(string="Transaction Amount")


    @api.model
    def create(self, values):
        result = super(MGC_ExpenseChecks, self).create(values)

        trans_data = self.env['mgc.expense.bank_accounts.transactions'].create({
            
                                                                    'back_account_id':result.account_number.id,
                                                                    'transaction_type': 'out',
                                                                    'check_id_reference': result.id,
                                                                    'description':"Payment for " + result.expense_trans_id.vendor.name +" through " + str(result.expense_trans_id.name),
                                                                    'trans_date':date.today(),
                                                                    'amount':result.amount,
                                                                })

        return result


    @api.onchange('check_date')
    def _onchange_check_date(self):
    	if self.check_date:
    		dateList = str(self.check_date).split('-')
    		selDate = datetime(int(dateList[0]),int(dateList[1]),int(dateList[2]))

    		if(selDate <= datetime.now() - timedelta(days=1)):
    			self.check_date = None
    			warning = {  'title': 'Invalid Date', 'message' : 'Date after the current date is not allowed for selection'}
    			
    			return {'warning': warning}

    @api.multi
    def print_check(self):
        
        amount_string_list = str(round(self.amount, 2)).split('.')
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
                            'date':self.check_date,
                            'purpose': self.purpose,
                            'amount_in_words': amount_whole + amount_cent + ' only',
                            'amount':"{:,.2f}".format(float(self.amount)),
                        }
                }
        
        out = self.env['report'].get_action(self, 'mgc_expense_kneco_external.expense_check_template', data=data)
        
        print(":::::::::::::::::::::::::::::::::::::::::::::")

        self.state = 'validate'
        self.check_printed = True
        self.printed_by = self.env.user.id

        return out

    @api.multi
    def reconcile_check(self):

    	self.update({'recon_status': True,
                     'recon_date': str(date.today()),
                     'state':'reconcile',
                     })
        
        disbursement = self.env['mgc.expense.transactions'].search([('id','=', self.expense_trans_id.id)],limit=1)
        disbursement.update({'state':'valid',})
        accouont_line = self.env['mgc.expense.bank_accounts.transactions'].search([('check_id_reference','=',self.id)],limit=1)
        accouont_line.update({'state':'valid'})
    	
        #return True

    @api.depends('amount')
    def change_amount(self):
    	print(self.amount)
    	for request in self:
    		print(request)
    	
    	if self.amount:
    		if(self.amount > self.amountLimit):
    			warning = {  'title': 'Invalid Expense as Reference', 'message' : 'Expense has been reffered to checks with the total amount equal to the expense cost. Expense is no longer available for reference.'}
		

