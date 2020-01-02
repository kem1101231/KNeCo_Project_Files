from odoo import api, models, fields
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError, UserError

class MGC_ExpenseBanks(models.Model):
    _name ='mgc.expense.banks'

    #bank_id = fields.Many2one('res.bank', string="Bank", ondelete="cascade")
    name = fields.Char(string="Bank Code")
    bank_id = fields.Many2one(comodel_name="res.bank", string="Bank")
    bank_code = fields.Char(string="Bank Name")
    bank_complete_name = fields.Char(string="Bank Address")

    bank_accounts = fields.One2many('mgc.expense.bank_accounts','bank_id',string="Bank Accounts")
    check_list = fields.One2many(comodel_name="mgc.expense.checks", inverse_name="bank_source", string="Check List" )


    nameList = "*/ - /*".split('/')

    @api.onchange('bank_code')
    def _onchange_bank_code(self):
        if self.bank_code:
            self.nameList[0] = self.bank_code
            self.name = "".join(self.nameList)
    
    @api.onchange('bank_complete_name')
    def _onchange_bank_complete_name(self):
        if self.bank_complete_name:
            self.nameList[2] = self.bank_complete_name
            self.name = "".join(self.nameList)
    
    ##bu_list = fields.One2many(related="bank_accounts")
    #, domain="[('bank_accounts.bank_id','=','bank_id')]"


class MGC_ExpenseAccounts(models.Model):
    _name = 'mgc.expense.accounts'

    account_code = fields.Char(string="Account Code")
    name = fields.Char(string="Acount Name")
    #acct_type = fields.Selection([ ('type1', 'Type 1'),('type2', 'Type 2'),],string='Type', default='type1', store=True)

class MGC_ExpenseAccounts_Extension(models.Model):
    _name="mgc.expense.accounts.ext"
    _inherit="mgc.expense.accounts"

    type_data = fields.Char("Test Data")


class MGC_ExpenseBusinessUnit(models.Model):
    _name = 'mgc.expense.bu'

    #bu_id = fields.Many2one('res.company', string="Business Unit", ondelete="cascade")
    name = fields.Char(string="Business Unit")
    bu_code = fields.Char(string="Code")
    sub_bu_of = fields.Many2one(string="Sub B.U. of", comodel_name="res.company")
    bu_complete_name = fields.Char(string="Registered Name")
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id, store=False)
    bu_total_asset = fields.Monetary(string="Total Asset")
    bu_accounts_count = fields.Integer(string="No. of Accounts")


    bank_accounts = fields.One2many(comodel_name='mgc.expense.bank_accounts', inverse_name='bu_id',string="Bank Accounts")
    #check_list = fields.One2many(related="bank_accounts.check_ids")
    
    nameList = "*/ - /*".split('/')
    
    @api.onchange('bu_code')
    def _onchange_bu_code(self):
        if self.bu_code:
            self.nameList[0] = self.bu_code
            self.name = "".join(self.nameList)
    
    @api.onchange('sub_bu_of')
    def _onchange_sub_bu_of(self):
        if self.sub_bu_of:
            self.bu_complete_name = self.sub_bu_of.name

    @api.onchange('bu_complete_name')
    def _onchange_bu_compplete_name(self):
        if self.bu_complete_name:
            self.nameList[2] = self.bu_complete_name
            self.name = "".join(self.nameList)


class MGC_ExpenseBankAccounts(models.Model):
    _name = 'mgc.expense.bank_accounts'

    @api.depends('transactions')
    def _get_cash_on_hand(self):
        for bank_account in self:
            bank_account.cash_on_bank = bank_account.total_in_fund - bank_account.total_out_fund
            bank_account.update({'cash_on_bank':bank_account.total_in_fund - bank_account.total_out_fund,})

    account_number = fields.Char(string="Account Number", required=True)
    name = fields.Char(string="Account Name")
    #bu_id = fields.Many2one('res.company', string="Business Unit", ondelete="cascade", required=True)
    bu_id = fields.Many2one(comodel_name='mgc.expense.bu', string="Business Unit", ondelete="cascade", required=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id, store=False)
    bank_id = fields.Many2one(comodel_name='mgc.expense.banks', string="Bank", ondelete="cascade", required=True)
    cash_on_bank = fields.Monetary(string="Cash in Bank", required=True, default=0, compute="_get_cash_on_hand")
    check_ids = fields.One2many(comodel_name='mgc.expense.checks',inverse_name='account_number',string="Prepared Checks")
    
    credit_account = fields.Many2one(comodel_name="account.account", string="Default Credit Entry")
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal")
    check_number_start = fields.Integer(strng="Start of Check Number")
    check_number_end = fields.Integer(strng="End of Check Number")

    total_in_fund = fields.Monetary(string="All In Funds")
    total_out_fund = fields.Monetary(string="Total Out Funds")
    
    transactions = fields.One2many(comodel_name="mgc.expense.bank_accounts.transactions", inverse_name="back_account_id", string="Fund Movements")
    
    nameList = "*/ - /*/ - /*".split('/')
    @api.onchange('bu_id')
    def _onchange_bu_id(self):
        if self.bu_id:
            self.nameList[0] = self.bu_id.bu_code
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
    
class MGC_ExpenseBankAccounts_Transactions(models.Model):
        
        _name="mgc.expense.bank_accounts.transactions"
        _order = 'id desc'

        back_account_id = fields.Many2one(comodel_name="mgc.expense.bank_accounts", string="Bank Account")
        transaction_type = fields.Selection(selection=[('in','Cash to Bank'),('out','Outgoing Funds')], string="Type", default="in")
        check_id_reference = fields.Many2one(comodel_name="mgc.expense.checks", string="Check Number\n(Outgoing Fund) ")
        check_reference = fields.Char(string="Check Number\n(Incoming Fund)")
        description = fields.Text(string="Description")
        trans_date = fields.Date(string="Transaction Date", default = date.today())
        amount = fields.Float(string="Transaction Amount")
        state = fields.Selection(string="State", selection=[('draft','Draft'),('valid','Validated')], default="draft")

        @api.model
        def create(self, values):

            result = super(MGC_ExpenseBankAccounts_Transactions, self).create(values)
            
            bank_account = self.env['mgc.expense.bank_accounts'].search([('id','=',result.back_account_id.id)], limit=1)
            
            if result.transaction_type == 'in':
                bank_account.update({'total_in_fund': bank_account.total_in_fund + result.amount,})
            
            if result.transaction_type == 'out':
                bank_account.update({'total_out_fund': bank_account.total_out_fund + result.amount,})
                

            return result




