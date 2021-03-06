from odoo import api, models, fields
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError, UserError
import xmlrpclib

class XMLRPC_Connection:
    url = 'http://192.168.93.3:8069'
    db = 'HONDA_SP'
    uname = 'admin'
    password = 'hondaadminsp'

    uid = None
    model = None
    #, url, db, uname, password
    def __init__(self):
        
        '''
        self.url = url
        self.db = db
        self.uname = uname
        self.password = password
        '''
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))

        self.uid = common.authenticate(self.db, self.uname, self.password, {})
        self.model = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))

    def getData(self, model, action, condition, result):
        #print(str(self.url)+ " - " + str(self.db)+ " - " + str(self.uid)+ " - " + str(self.password))
        return self.model.execute_kw(self.db, self.uid, self.password, model, action, condition, result)


class MGC_Expense(models.Model):
    _name = 'mgc.expense.base'

    def _amount_all(self):
        for expense in self:
           
            amount_untaxed = 0.0
            for line in expense.check_list:
                amount_untaxed += line.amount
            expense.update({
                'check_list_amount': amount_untaxed,
            })

    name = fields.Char(string="Expense ID")
    amount = fields.Float(string="Expense Cost", required=True)
    expense_type = fields.Many2one('mgc.acct_chart.acct_finance', string="Expense Type",ondelete='cascade', required=True)
    
    check_list = fields.One2many('mgc.expense.checks', 'expense_id', string="Prepared Checks")
    check_list_amount = fields.Float(string='Prepared Checks Amount', compute='_amount_all')
    approve_status = fields.Boolean(string="Approval Status")

    request_reference = fields.Many2one('account.request', store=True,string="Request Reference", required=True)
    #request_ref_type_name = fields.Char(related="request_reference.request_type_line_id.fs_class_id.name",string="Request Reference Type Name")
    request_ref_type = fields.Many2one('mgc.coa_legend.fs_class_chart', string="Reference Type",store=True, required=True)
    request_bu_id = fields.Char(related="request_reference.company_id.name", string="Business Unit")
    department = fields.Char(related="request_reference.department_id.name", string="Department")
    request_type = fields.Char(related="request_reference.request_type_id.name", string="Request Type")
    request_name = fields.Char(related="request_reference.request_type_line_id.name", string="Request Name")
    request_purpose = fields.Text(related="request_reference.purpose", string="Request Purpose")
    request_type_id_type = fields.Char(store=False) 

    purchase_id_source_type = fields.Selection([('MUTI_MC', 'MUTI MC'),('MUTI_SP', 'MUTI SP'),('HONDA_MC', 'Honda Soc. MC'),('HONDA_SP', 'Honda Soc. SP'),('internal', 'PPE')],string='Po Source Type', default='internal', store=True)

    purchase_id_ext = fields.Integer(string="Purchase ID")
    purchase_id_number_ext = fields.Char(string="Purchase Order")
    vendor_bill_id_ext = fields.Integer(string="Vendor Bill ID")
    vendor_bill_ext = fields.Char(string="Vendor Bill")

    purchase_id = fields.Many2one('purchase.order', string="Purchase Order")
    vendor_bill = fields.Many2one('account.invoice', string="Vendor Bill")


    bu_id = fields.Many2one('res.company', string="Expense B.U.", required=True)
    purpose = fields.Text(string="Expense Purpose", required=True)
    is_efo = fields.Boolean(string="Expense for Operation")
    is_shared = fields.Boolean(string="Shared Expense")
    prep_id = None #fields.Many2one('res.partner', string="Prepared by",ondelete='cascade')
    date_prep = None #fields.Date(string="Preparation Date")

    ext_Access_Data = {
                        'MUTI_MC':('MUTI_MC','admin',''),
                        'MUTI_SP':('MUTI_SP','admin',''),
                        'HONDA_MC':('HONDA_MC','admin',''),
                        'HONDA_SP':('HONDA_SP','admin','hondaadminsp'),
                    }

    @api.onchange('request_reference')
    def _onchange_request_reference(self):
        
        if self.request_reference:
            purString = ''
            purString = purString + self.request_reference.purpose

            self.purpose = purString

            #self.request_ref_type = self.request_reference.request_type_line_id.fs_class_id.id
            self.request_type_id_type = str(self.request_reference.request_type_id.type)

            if self.request_reference.request_type_id.type == 'cash':
                self.amount = self.request_reference.amount_total
            else:
                self.amount = 0
            
            sequence = self.search_count([('id', '!=', '0')])
            years = date.strftime(date.today(), '%y')
            name = 'E-' + str(years) + '-' + '{:06}'.format(sequence + 1)
            self.name = name
            self.bu_id = self.request_reference.company_id

    @api.onchange('purchase_id_source_type')
    def _onchange_purchase_id_source_type(self):
        if self.purchase_id_source_type:
            pass

    @api.onchange('purchase_id_number_ext')
    def _onchange_purchase_id_number_ext(self):
        if self.purchase_id_number_ext:
            xmlrpc_accessData = self.ext_Access_Data[self.purchase_id_source_type]
            #print(xmlrpc_accessData)
            #'http://192.168.93.3:8069', xmlrpc_accessData[0], xmlrpc_accessData[1], xmlrpc_accessData[2]/// [[['mgc_request_id', '=', self.request_reference.id],['name','=', self.purchase_id_number_ext]]]
            #xmlrpcData = XMLRPC_Connection().getData('purchase.order','search', [[[]]], {'fields': ['name','amount_total'], 'limit': 0})
            #print(xmlrpcData)

    @api.constrains('amount')
    def _amount_check(self):
	    for record in self:
	        if record.amount <= 0:
	            raise ValidationError("Invalid expense cost. Please enter the cost of expense.")	
	            
class MGC_ExpenseBanks(models.Model):
    _name ='mgc.expense.banks'

    bank_id = fields.Many2one('res.bank', string="Bank", ondelete="cascade")
    name = fields.Char(related='bank_id.name')
    bank_accounts = fields.One2many('mgc.expense.bank_accounts','bank_id',string="Bank Accounts")
    check_list = fields.One2many(related="bank_accounts.check_ids")
    #sbu_list = fields.One2many(related="bank_accounts")
    #, domain="[('bank_accounts.bank_id','=','bank_id')]"

class MGC_ExpenseChecks(models.Model):
    _name = 'mgc.expense.checks'


    name = fields.Char(string="Check Number", required=True)
    account_number = fields.Many2one('mgc.expense.bank_accounts', string="Bank Account", ondelete="cascade", required=True)
    bank_account = fields.Char(related="account_number.account_number")
    bank_source = fields.Char(related="account_number.bank_id.name", string="Bank")
    bu_source = fields.Char(related="account_number.bu_id.name", string="Business Unit")
    check_date = fields.Date(string="Check Date", required=True)
    status = fields.Boolean(string="Status")
    recon_status = fields.Boolean(string="Reconcilation")
    recon_date = fields.Date(string="Reconcilation Date")
    amount = fields.Float(string="Amount", required=True)
    expense_id = fields.Many2one('mgc.expense.base',string="For Expense", ondelete="cascade", required=True)
    expense_bu = fields.Many2one(related='expense_id.bu_id', string="")
    purpose = fields.Text(related="expense_id.purpose", string="Purpose")

    amountLimit = 0

    @api.onchange('expense_id')
    def _onchane_expense_id(self):
        if self.expense_id:
            exp_cost = self.expense_id.amount
            check_cost = self.expense_id.check_list_amount

            amountLimit = exp_cost - check_cost
            if(amountLimit <= 0):
                
                self.expense_id = None
                self.amount = 0

                warning = {  'title': 'Invalid Expense as Reference', 'message' : 'Expense has been reffered to checks with the total amount equal to the expense cost. Expense is no longer available for reference.'}                
                return {'warning': warning}

            else:
                self.amount = amountLimit 
    
    @api.onchange('check_date')
    def _onchange_check_date(self):
    	if self.check_date:
    		dateList = str(self.check_date).split('-')
    		selDate = datetime(int(dateList[0]),int(dateList[1]),int(dateList[2]))

    		if(selDate <= datetime.now() - timedelta(days=1)):
    			self.check_date = None
    			warning = {  'title': 'Invalid Date', 'message' : 'Date later than the current date is not allowed for selection'}
    			
    			return {'warning': warning}

    @api.multi
    def print_check(self):

        data = {'data':{'number':self.name,
                        'check_date':self.check_date,
                        'bank':self.bank_source,
                        'account':self.bank_account,
                        'amount':self.amount,
                        }
                }
        out = self.env['report'].get_action(self, 'mgc_expense_kneco.expense_check_form', data=data)
        return out

    @api.multi
    def reconcile_check(self):

    	self.write({'recon_status': True})
    	self.write({'recon_date': str(datetime.now())})

    	return True

    @api.depends('amount')
    def change_amount(self):
    	print(self.amount)
    	for request in self:
    		print(request)
    	'''
    	if self.amount:
    		    		if(self.amount > self.amountLimit):
    			warning = {  'title': 'Invalid Expense as Reference', 'message' : 'Expense has been reffered to checks with the total amount equal to the expense cost. Expense is no longer available for reference.'}
		'''


class MGC_ExpenseAccounts(models.Model):
    _name = 'mgc.expense.accounts'

    account_code = fields.Char(string="Account Code")
    name = fields.Char(string="Acount Name")
    #acct_type = fields.Selection([ ('type1', 'Type 1'),('type2', 'Type 2'),],string='Type', default='type1', store=True)

class MGC_ExpenseBusinessUnit(models.Model):
    _name = 'mgc.expense.bu'

    bu_id = fields.Many2one('res.company', string="Business Unit", ondelete="cascade")
    name = fields.Char(related='bu_id.name')
    bank_accounts = fields.One2many('mgc.expense.bank_accounts','bu_id',string="Bank Accounts")
    check_list = fields.One2many(related="bank_accounts.check_ids")

class MGC_ExpenseBankAccounts(models.Model):
    _name = 'mgc.expense.bank_accounts'

    account_number = fields.Char(string="Account Number", required=True)
    name = fields.Char(string="Account Name")
    #bu_id = fields.Many2one('mgc.expense.bu', string="Business Unit", ondelete="cascade", required=True)
    bu_id = fields.Many2one('res.company',string="Business Unit", ondelete="cascade", required=True)
    #bu_source = fields.Char(related="bu_id.name", string="Business Unit")
    bank_id = fields.Many2one('mgc.expense.banks', string="Bank", ondelete="cascade", required=True)
    cash_on_bank = fields.Float(string="Cash in Bank", required=True)
    check_ids = fields.One2many('mgc.expense.checks','account_number',string="Prepared Checks")

    '''
    @api.constrains('cash_on_bank')
    def _amount_cash_on_bank(self):
        for record in self:
            if record.cash_on_bank <= 0:
                raise ValidationError("Invalid value to cash on bank. Please provide an amount greater than zero.")    
    '''           
    nameList = "*/-/*/-/*".split('/')
    @api.onchange('bu_id')
    def _onchange_bu_id(self):
        if self.bu_id:
            self.nameList[0] = self.bu_id.partner_id.abbreviation
            self.name = "".join(self.nameList)

    @api.onchange('bank_id')
    def _onchange_bank_id(self):
        if self.bank_id:
            self.nameList[2] = self.bank_id.name
            self.name = "".join(self.nameList)
    
    @api.onchange('account_number')
    def _onchange_account_number(self):
        if self.account_number:
            self.nameList[4] = self.account_number
            self.name = "".join(self.nameList)
    


