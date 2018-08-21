from odoo import api, models, fields

class MGC_Expense(models.Model):
    _name = 'mgc.expense.base'

    name = fields.Char(string="Expense ID")
    amount = fields.Float(string="Expense Cost")
    expense_type = fields.Many2one('mgc.expense.accounts', string="Expense Type",ondelete='cascade')
    purpose = fields.Text(string="Purpose")
    bu_id = fields.Many2one('mgc.expense.bu', string="Business Unit")
    check_list = fields.One2many('mgc.expense.checks', 'expense_id', string="Prepared Checks")
    approve_status = fields.Boolean(string="Approval Status")
    #fund_source = fields.Many2one('mgc.expense.bank_accounts', string="Source of Fund",ondelete='cascade')
    #bu_source = fields.Char(related="fund_source.bu_id.name", string="Business Unit")
    #bank_source = fields.Char(related="fund_source.bank_id.name", string="Bank")
    #acct_number = fields.Char(related="fund_source.account_number")
    #check_id = fields.Many2one('mgc.expense.checks', string="Prepared Check",ondelete='cascade')
    #recon_status = fields.Boolean(related="check_id.recon_status", string="Reconcilation Status")
    #recon_date = fields.Date(related="check_id.recon_date", string="Reconcilation Date")
    is_efo = fields.Boolean(string="Expense for Operation")
    is_shared = fields.Boolean(string="Shared Expense")
    prep_id = None #fields.Many2one('res.partner', string="Prepared by",ondelete='cascade')
    date_prep = None #fields.Date(string="Preparation Date")

class MGC_ExpenseBanks(models.Model):
    _name ='mgc.expense.banks'

    bank_id = fields.Many2one('res.partner', string="Bank", ondelete="cascade")
    name = fields.Char(related='bank_id.name')
    bank_accounts = fields.One2many('mgc.expense.bank_accounts','bank_id',string="Bank Accounts")
    check_list = fields.One2many(related="bank_accounts.check_ids")
    #sbu_list = fields.One2many(related="bank_accounts")
    #, domain="[('bank_accounts.bank_id','=','bank_id')]"

class MGC_ExpenseChecks(models.Model):
    _name = 'mgc.expense.checks'

    name = fields.Char(string="Check Number")
    account_number = fields.Many2one('mgc.expense.bank_accounts', string="Bank Account", ondelete="cascade")
    bank_account = fields.Char(related="account_number.account_number")
    bank_source = fields.Char(related="account_number.bank_id.name", string="Bank")
    bu_source = fields.Char(related="account_number.bu_id.name", string="Business Unit")
    check_date = fields.Date(string="Check Date")
    status = fields.Boolean(string="Status")
    recon_status = fields.Boolean(string="Reconcilation")
    recon_date = fields.Date(string="Reconcilation Date")
    amount = fields.Float(string="Amount")
    expense_id = fields.Many2one('mgc.expense.base',string="For Expense", ondelete="cascade")
    purpose = fields.Text(related="expense_id.purpose", string="Purpose")

class MGC_ExpenseAccounts(models.Model):
    _name = 'mgc.expense.accounts'

    account_code = fields.Char(string="Account Code")
    name = fields.Char(string="Acount Name")
    #acct_type = fields.Selection([ ('type1', 'Type 1'),('type2', 'Type 2'),],string='Type', default='type1', store=True)

class MGC_ExpenseBusinessUnit(models.Model):
    _name = 'mgc.expense.bu'

    bu_id = fields.Many2one('res.partner', string="Business Unit", ondelete="cascade")
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