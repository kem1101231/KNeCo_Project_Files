from odoo import api, models, fields

class MGC_Expense(models.Model):
	_name = 'mgc.expense.base'

    name = fields.Char(string="Expense ID")
    #check_code = fields.Char(string="Check Code", required=True)
    amount = None #fields.Float(string="Check Amount")
    expense_type = fields.Many2one('mgc.expense.accounts', string="Prepared Check",ondelete='cascade')
    purpose = fields.Text(string="Purpose of the Check")
    receiver = None #fields.Many2one('res.partner', string="Recipient",ondelete='cascade')
    fund_source = fields.Many2one('mgc.expense.bank_accounts', string="Source of Fund",ondelete='cascade')
    bu_source = fields.Char(related="fund_source.bu_id.name")
    bank_source = fields.Char(related="fund_source.bank_id.name")
    check_id = fields.Many2one('mgc.expense.checks', string="Prepared Check",ondelete='cascade')
    is_efo = fields.Boolean(string="Expense for Operation")
    is_shared = fields.Boolean(string="Shared Expense")
    prep_id = None #fields.Many2one('res.partner', string="Prepared by",ondelete='cascade')
    date_prep = None #fields.Date(string="Preparation Date")

class MGC_ExpenseBanks(models.Model):
    _name ='mgc.expense.banks'

    bank_id = fields.Many2one('res.partner', string="Bank", ondelete="cascade")
    name = fields.Char(related='bank_id.name')

class MGC_ExpenseChecks(models.Model):
    _name = 'mgc.expense.checks'

    name = fields.Char(string="Check Number")
    account_number = fields.Many2one('mgc.expense.bank_accounts', string="Bank Account", ondelete="cascade")
    check_date = fields.Date(string="Check Date")
    status = fields.Boolean(string="Status")
    recon_status = fields.Boolean(string="Reconcilation")
    recon_date = fields.Boolean(string="Reconcilation Date")
    amount = fields.Float(string="Amount")

class MGC_ExpenseAccounts(models.Model):
    _name = 'mgc.expense.accounts'

    account_code = fields.Char(string="Account Code")
    name = fields.Char(string="Acount Name")

class MGC_ExpenseBusinessUnit(models.Model):
    _name = 'mgc.expense.bu'

    bu_id = fields.Many2one('res.partner', string="Business Unit", ondelete="cascade")
    name = fields.Char(related='bu_id.name')

class MGC_ExpenseBankAccounts(models.Model):
    _name = 'mgc.expense.bank_accounts'

    account_number = fields.Char(string="Account Number")
    name = None
    bu_id = fields.Many2one('mgc.expense.bu', string="Business Unit", ondelete="cascade")
    bank_id = fields.Many2one('mgc.expense.banks', string="Bank", ondelete="cascade")
    cash_on_bank = fields.Float(string="Cash in Bank")