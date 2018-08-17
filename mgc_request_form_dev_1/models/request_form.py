from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date
from odoo.addons import decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class Request_Form(models.Model):
    _name = 'mgc_request.base'

    name = fields.Char(string="Request Number")
    #request_code =  fields.Char(string="Request Number")# request code or the reference number of the request of the document
    requestor_id = None # requesting personnel
    purpose = fields.Text(string="Purpose") # purpose of the request
    request_type = None # type of purpose of the request
    request_status = None # status of the request
    request_line = fields.One2many(comodel_name="mgc_request.line", inverse_name="request_id",string="Request Board", required=False)

    l1_approve_status = None # level 1 or the basic approval status of the request
    l1_approve_date = None  # date of level 1 or the basic approval status of the request

    l2_approve_status = None # level 2 approval status of the request (if there's any)
    l2_approve_date = None  #  date of level 2 approval status of the request (if there's any)

    l3_approve_status = None # level 3 approval status of the request (if there's any)
    l3_approve_date = None  # date of level  3 approval status of the request (if there's any)

    l4_approve_status = None # level 4 approval status of the request (if there's any)
    l4_approve_date = None  # date of level 4 approval status of the request (if there's any)

class Request_Line(models.Model):
    _name = 'mgc_request.line'

    request_id = fields.Many2one(comodel_name="account.request", string="Request Number", required=False, )
    product_id = fields.Many2one(comodel_name="product.product", string="Product", required=False, )
    description = fields.Char(string="Description", required=True, )
    quantity = fields.Float(string="Quantity",  required=True, )
    date_scheduled = fields.Datetime(string="Scheduled Date", required=True, index=True)
    account_id = fields.Many2one(comodel_name="account.account", string="Account", required=False, )
    unit_uom = fields.Many2one('product.uom', string='Unit of Measure', required=False)
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Product Price'))
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Monetary(compute='_compute_amount', string='Tax', store=True)
    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=False,
                                 related='request_id.company_id')
    currency_id = fields.Many2one(related='request_id.currency_id', store=True, string='Currency', readonly=True)
    purchase_id = fields.Many2one(comodel_name="purchase.order", string="Purchase", required=False, )
    order_lines = fields.One2many('purchase.order.line', 'request_line_id', string="Order Lines", readonly=True,
                                    copy=False)
    state = fields.Selection(string="Status", selection=[('draft', 'Draft'),
                                                         ('cancelled', 'Cancelled'),
                                                         ('void', 'Void'),
                                                         ('print_rf', 'Print RF'),
                                                         ('confirmed', 'Confirmed'),
                                                         ('done', 'Done')], required=False, related='request_id.state')



class Request_Types(models.Model):
    _name = 'mgc_request.types'

    name = None
    out_request = None
    transaction_type = None
    l1_approval_reference = None
    l1_approval_reference_data = None
    l2_approval_reference  = None
    l2_approval_reference_data = None
    l3_approval_reference  = None
    l3_approval_reference_data = None
    l4_approval_reference  = None
    l4_approval_reference_data = None


class Request_Conduct_Types(models.Model):
    _name = 'mgc.request.conduct_types'

    name = None
    l1_position_approval = None
    l2_position_approval = None
    l3_position_approval = None
    l4_position_approval = None


