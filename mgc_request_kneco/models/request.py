from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date
from odoo.addons import decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class MGC_Request(models.Model):
	_name = "mgc.request.form.base"
	desciption = "MGC Request Forms"



	name = fields.Char(string="Request Number")
	requestor_id = fields.Many2one(comodel_name="hr.employee", string="Requesting Employee", required=True,  default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1))
	request_department = fields.Many2one(comodel_name="hr.department", string="Department", required=True)
	request_company = fields.Many2one(comodel_name="res.company", string="Company", required=True)
	request_type = fields.Char(string="Request Type")
	request_name = fields.Char(string="Request Name")
	#request_company_through = fields.Many2one(comodel_name="res.company", string="Request Through", required=True)
	request_source = None
	request_purpose = fields.Text(string="Purpose", required=True)
	#request_special_instruction = fields.Text(string="Special Instruction")

	request_line_ids = fields.One2many("mgc.request.form.line", 'request_id', string="Request Name", required=False)
	request_total = fields.Float(string="Amount Total", readonly=True)
	state = fields.Selection(string="Status",
                             selection=[('draft', 'Draft'),
                                        ('cancelled', 'Cancelled'),
                                        ('void', 'Void'),
                                        ('print_rf', 'Print RF'),
                                        ('confirmed', 'Confirmed'),
                                        ('done', 'Done')], default='draft', required=False, track_visibility='onchange')
	
	
	@api.onchange('requestor_id')
	def _onchange_requestor_id(self):
		if self.requestor_id:
			self.request_company = self.requestor_id.company_id.id
			self.request_department = self.requestor_id.department_id.id
			sequence = self.search_count([('id', '!=', 0)])
			years = date.strftime(date.today(), '%y')
			name = str(years) + '-' + '{:06}'.format(sequence + 1)
			self.name = name
  

class MGC_Request_Line(models.Model):
	_name = 'mgc.request.form.line'
	_rec_name = 'request_id'
	desciption = "MGC Request Forms Line"
	_sql_constraints = [('mgc.request.form.line', 'unique (product_id)',     
                 'Duplicate products in order line not allowed !')]

	@api.depends('unit_cost', 'quantity')
	def _get_subtotal(self):
		for line in self:
			self.subtotal = line.unit_cost * line.quantity 
			
			'''
			line.update({
                'subtotal': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            '''

	request_id = fields.Many2one(comodel_name="mgc.request.form.base", string="Request ID")
	product_id = fields.Many2one(comodel_name="product.template", string="Product ID")
	description = fields.Text(related="product_id.description",string="Description")
	unit = fields.Many2one('product.uom',string="Unit")
	unit_cost = fields.Float(related="product_id.standard_price",string="Unit Cost")
	quantity = fields.Float(string="Quantity")
	tax_rate = fields.Char(string="Tax")
	subtotal = fields.Float(string="Sub Total", compute="_get_subtotal")

class MGC_Request_Types(models.Model):
	_name = "mgc.requeust.form.types"


class MGC_Request_Names(models.Model):
	_name = "mgc.requeust.form.names"	

class MGC_Request_Types(models.Model):
	_name = "mgc.requeust.form.types"

class MGC_Request_Types(models.Model):
	_name = "mgc.requeust.form.types"
