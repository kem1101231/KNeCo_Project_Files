from odoo import api, models, fields
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError, UserError
from num2words import num2words

class MGCExpenseCreditMemo(models.Model):
	_name = 'mgc.expense.credit_memo'
	_description = 'Credit Memo'
	_inherit = ['mail.thread', 'ir.needaction_mixin']
	_order = 'id desc'

	name = fields.Char(string="Memo ID")
	vendor = fields.Many2one(comodel_name="res.partner", string="Vendor/Biller")
	account_entry = fields.Many2one(comodel_name="account.account", string="Account Entry")
	payable_line = fields.One2many(comodel_name='mgc.expense.credit_memo.line', inverse_name='memo_id', string="Payable List")
	state = fields.Selection(selection=[('draft','Draft'),('check','Checking'),('valid','Validated')], string="State", default="draft", track_visibility='onchange')

	@api.model
	def create(self, values):
            
            if 'vendor' in values:
               if values['vendor']:
            
                    monthData = monthrange(now.year, now.month)                    
                    sequence = sequence = self.search_count([('id', '!=', '0'),('create_date','>=', str(now.year)+'-'+str(now.month)+'-1'),('create_date','<=',str(now.year)+'-'+str(now.month)+'-'+str(monthData[1]))])
                    years = date.strftime(date.today(), '%y')
                    month = date.strftime(date.today(), '%m')
                    name = 'CM-' + str(years) +'-'+str(month)+'-'+'{:05}'.format(sequence + 1)                        
                    
                    values['name'] = name

            result =  super(MGCExpenseCreditMemo, self).create(values)

class MGCExpenseCreditMemoPayableLine(models.Model):
	_name= 'mgc.expense.credit_memo.line'

	memo_id = fields.Many2one(comodel_name='mgc.expense.credit_memo', string="Memo ID")
	payable_id = fields.Many2one(comodel_name="mgc.expense.base", string="Payable")
	reason = fields.Text(string="Reason/Description")
	currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)
	amount = fields.Monetary(string="Amount")
