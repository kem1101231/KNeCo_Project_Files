from odoo import models, api, fields

class MGC_RequestBase(models.Model):
    _name = 'mgc.request_form.base'

    name = fields.Char(string="Request Number")
    #request_code =  fields.Char(string="Request Number")# request code or the reference number of the request of the document
    requestor_id = None # requesting personnel 1
    purpose = fields.Text(string="Purpose") # purpose of the request
    request_type = None # type of purpose of the request
    request_status = None # status of the request
    request_line = fields.One2many(comodel_name="mgc.request_form.line", inverse_name="request_id",string="Request Board", required=False)

    l1_approve_status = None # level 1 or the basic approval status of the request
    l1_approve_date = None  # date of level 1 or the basic approval status of the request

    l2_approve_status = None # level 2 approval status of the request (if there's any)
    l2_approve_date = None  #  date of level 2 approval status of the request (if there's any)

    l3_approve_status = None # level 3 approval status of the request (if there's any)
    l3_approve_date = None  # date of level  3 approval status of the request (if there's any)

    l4_approve_status = None # level 4 approval status of the request (if there's any)
    l4_approve_date = None  # date of level 4 approval status of the request (if there's any)


class MGC_RequestLine(models.Model):
	_name = 'mgc.request_form.line'

	request_id = fields.Many2one('mgc.request_form.base', string='Request Number')
	product_id = fields.Many2one('product.product', string='Product')
	quantity = fields.Float(string='Quantity')
	unit = fields.Char(string='Unit')
	unit_price = fields.Float(string='Unit Price')


class MGC_RequestType(models.Model):
    _name = 'mgc.request_form.type'
    
    name = None
    out_request = None
    transaction_type = fields.Many2one('mgc.request_form.conduct_types', string='Request Approval Type')
    l1_approving_officer = fields.Char(related='transaction_type.l1_position_approval.name')
    l1_approval_reference = None
    l1_approval_reference_data = None
    l2_approving_officer = fields.Char(related='transaction_type.l2_position_approval.name')
    l2_approval_reference  = None
    l2_approval_reference_data = None
    l3_approving_officer = fields.Char(related='transaction_type.l3_position_approval.name')
    l3_approval_reference  = None
    l3_approval_reference_data = None
    l4_approving_officer = fields.Char(related='transaction_type.l4_position_approval.name')
    l4_approval_reference  = None
    l4_approval_reference_data = None


class MGC_RequestConductTypes(models.Model):
    _name = 'mgc.request_form.conduct_types'

    name = fields.Char(string='Request Approval Type')
    l1_position_approval = fields.Many2one('hr.job', string='Level 1 Approval')
    l2_position_approval = fields.Many2one('hr.job', string='Level 2 Approval')
    l3_position_approval = fields.Many2one('hr.job', string='Level 3 Approval')
    l4_position_approval = fields.Many2one('hr.job', string='Level 4 Approval')	