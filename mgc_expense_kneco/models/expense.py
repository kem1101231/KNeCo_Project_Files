from odoo import api, models, fields
from datetime import datetime, date
from odoo.exceptions import ValidationError, UserError


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
    request_bu_id = fields.Char(related="request_reference.company_id.name", string="Business Unit")
    department = fields.Char(related="request_reference.department_id.name", string="Department")
    request_type = fields.Char(related="request_reference.request_type_id.name", string="Request Type")
    request_name = fields.Char(related="request_reference.request_type_line_id.name", string="Request Name")
    request_purpose = fields.Text(related="request_reference.purpose", string="Request Purpose")

    bu_id = fields.Many2one('res.company', string="Expense B.U.", required=True)
    purpose = fields.Text(string="Expense Purpose", required=True)
    is_efo = fields.Boolean(string="Expense for Operation")
    is_shared = fields.Boolean(string="Shared Expense")
    prep_id = None #fields.Many2one('res.partner', string="Prepared by",ondelete='cascade')
    date_prep = None #fields.Date(string="Preparation Date")

    
    @api.onchange('request_reference')
    def _onchange_request_reference(self):
        
        if self.request_reference:
            purString = ''
            purString = purString + self.request_reference.purpose

            self.purpose = purString
            
            sequence = self.search_count([('id', '!=', '0')])
            years = date.strftime(date.today(), '%y')
            name = 'E-' + str(years) + '-' + '{:06}'.format(sequence + 1)
            self.name = name
            self.bu_id = self.request_reference.company_id

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

                warning = {  'title': 'Invalid Expense as Reference', 'message' : 'Expense has been reffered to checks with the total amount equal to the expense cost. Expense is no longer available for reference.'}
                
                return {'warning': warning}

            else:
                self.amount = amountLimit 
    
    @api.multi
    def reconcile_check(self):

    	self.write({'recon_status': True})
    	self.write({'recon_date': str(datetime.now())})

    	return True
    	                 
    

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

    account_number = fields.Char(string="Account Number")
    name = fields.Char(string="Account Name")
    bu_id = fields.Many2one('mgc.expense.bu', string="Business Unit", ondelete="cascade")
    #bu_source = fields.Char(related="bu_id.name", string="Business Unit")
    bank_id = fields.Many2one('mgc.expense.banks', string="Bank", ondelete="cascade")
    #bank_source = fields.Char(related="bank_id.name", string="Business Unit")
    cash_on_bank = fields.Float(string="Cash in Bank")
    check_ids = fields.One2many('mgc.expense.checks','account_number',string="Prepared Checks")

class CustomReport(models.AbstractModel):
      _name = 'report.mgc_expense_kneco.report_fleet_job_card'

      @api.model
      def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('mgc_expense_kneco.report_fleet_job_card')
        fleet_args = {
            'doc_ids': docids,
            'doc_model': report.fleet_repair,
            'docs': self,
        }
        return report_obj.render('mgc_expense_kneco.report_fleet_job_card', fleet_args)
 