from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date
from odoo.addons import decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class MGC_Request(models.Model):
	_name = "mgc.request.form.base"
	desciption = "MGC Request Forms"

	name = fields.Char(string="Request Number", required=True)
	requestor_id = fields.Many2one(comodel_name="hr.employee", string="Requesting Employee", required=True,  default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1))
	request_department = fields.Many2one(comodel_name="hr.department", string="Department", required=True)
	request_company = fields.Many2one(comodel_name="res.company", string="Company", required=True)
	request_type = None
	request_name = None
	request_purpose = fields.Text(string="Purpose", required=True)
	request_special_instruction = fields.Text(string="Special Instruction")

	request_line_ids = fields.One2many("mgc.request.form.line", 'request_id', string="Request Name", required=False)

	@api.onchange('requestor_id')
	def _onchange_requestor_id(self):
		if self.requestor_id:
			self.request_company = self.requestor_id.company_id.id
			self.request_department = self.requestor_id.department_id.id
  

class MGC_Request_Line(models.Model):
	_name = 'mgc.request.form.line'

	request_id = fields.Many2one(comodel_name="mgc.request.form.base", string="Request ID")
	product_id = fields.Many2one(comodel_name="product.product", string="Product ID")
	description = fields.Char(string="Description")
	unit = fields.Char(string="Unit")
	unit_cost = fields.Float(string="Unit Cost")
	quantity = fields.Float(string="Quantity")
	tax_rate = fields.Char(string="Tax")
	subtotal = fields.Float(string="Sub Total")

class MGC_Request_Types(models.Model):
	_name = "mgc.requeust.form.types"


class MGC_Request_Names(models.Model):
	_name = "mgc.requeust.form.names"	

class MGC_Request_Types(models.Model):
	_name = "mgc.requeust.form.types"

class MGC_Request_Types(models.Model):
	_name = "mgc.requeust.form.types"
