from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date
from odoo.addons import decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class RequestForm(models.Model):
    _name = 'account.request'
    _description = 'Request Form'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.depends('request_line.price_total')
    def _amount_all(self):
        for request in self:
            amount_untaxed = amount_tax = 0.0
            for line in request.request_line:
                amount_untaxed += line.price_subtotal
                if request.company_id.tax_calculation_rounding_method == 'round_globally':
                    taxes = line.taxes_id.compute_all(line.price_unit, line.request_line.currency_id, line.quantity)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax
            request.update({
                'amount_untaxed': request.currency_id.round(amount_untaxed),
                'amount_tax': request.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.depends('request_line.order_lines.order_id.state')
    def _compute_orders(self):
        for request in self:
            orders = self.env['purchase.order']
            for line in request.request_line:
                orders |= line.order_lines.mapped('order_id')
            request.order_ids = orders
            request.order_count = len(orders)

    @api.depends('state')
    def _get_ordered(self):
        for request in self:
            if request.state != 'done':
                request.order_status = 'no'
                continue

            if request.request_type_id.type == 'purchase':
                for line in request.request_line:
                    for lines in line.order_lines:
                        if lines.order_id.state == 'to approve':
                            request.order_status = 'to_order'

                        elif lines.order_id.state == 'purchase':
                            request.order_status = 'order'

                        else:
                            request.order_status = 'no'
            else:
                request.order_status = 'no'

    name = fields.Char(string="Name", required=False)

    curre_user = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.user)
    request_number = fields.Char(string="Request Number", required=False, )
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Requestor", required=True,
                                  default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1))
    department_id = fields.Many2one(comodel_name="hr.department", string="Department", required=True)
    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=True)
    request_company_id = fields.Many2one(comodel_name="account.request.company", string="Request Through Company", required=False,)
    request_department_id = fields.Many2one(comodel_name="account.request.department", string="Request Through Department",
                                            required=False)
    request_selection = fields.Selection(string="Requesting To", selection=[('company', 'Company'), ('contacts', 'Contacts')], required=True, default='company')
    partner_id = fields.Many2one(comodel_name="res.partner", string="Contacts", required=False)
    request_type_id = fields.Many2one(comodel_name="account.request.type", string="Type", required=True)
    request_type_line_id = fields.Many2one(comodel_name="account.request.type.line", string="Request Name", required=False)
    source_id = fields.Many2one(comodel_name="account.request.source", string="Source", required=False, )
    internal_type = fields.Char(string="Internal Type", required=False)
    date_request = fields.Date(string="Request Date", required=False, default=fields.Date.today())
    purpose = fields.Text(string="Purpose", required=False, )
    notes = fields.Text(string="Special Instruction", required=False, )
    request_line = fields.One2many(comodel_name="account.request.line", inverse_name="request_id",
                                       string="Request Board", required=False)
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal", required=False, )
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    state = fields.Selection(string="Status",
                             selection=[('draft', 'Draft'),
                                        ('cancelled', 'Cancelled'),
                                        ('void', 'Void'),
                                        ('print_rf', 'Print RF'),
                                        ('confirmed', 'Confirmed'),
                                        ('done', 'Done')], default='draft', required=False, track_visibility='onchange')
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='always')
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position', oldname='fiscal_position')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    is_printed = fields.Boolean(string="Printed RF")
    abbreviation = fields.Char(string="Abbreviation", required=False, )
    type_code = fields.Char(string="Code", required=False, )
    order_status = fields.Selection(string="Order Status",
                                    selection=[('no', 'Nothing to Order'),
                                               ('to_order', 'To Order'),
                                               ('order', 'Order Confirmed')], compute="_get_ordered", store=True,
                                    readonly=True, copy=False, default='no',track_visibility='onchange')
    approver_ids = fields.One2many(comodel_name="account.request.line.approvers", inverse_name="request_id",
                                   string="Approvers", required=False, )
    order_count = fields.Integer(compute="_compute_orders", string='# of Orders', copy=False, default=0)
    order_ids = fields.Many2many(comodel_name='purchase.order', compute="_compute_orders", string='Orders', copy=False)

    def _get_signed_on(self):
        user = self.env.user.id
        res_resource = self.env['resource.resource'].sudo().search([('user_id', '=', user), ('active', '=', True)],
                                                            order="id desc", limit=1)
        if not res_resource and user != 1:
            raise ValidationError("No related employee assigned to current user. Please consult System Admin")
        else:
            resource_id = res_resource.id
            res_sign = self.env['hr.employee'].sudo().search([('resource_id', '=', resource_id), ('active', '=', True)])
            sign_id = res_sign.id
        return sign_id

    @api.model
    def create(self, values):
        if 'employee_id' in values:
            if values['employee_id']:
                # sequence = self.env['ir.sequence'].next_by_code('account.request')
                department = values.get('department_id')
                sequence = self.search_count([('department_id', '=', department)])
                years = date.strftime(date.today(), '%y')
                code = values.get('type_code')
                name = str(years) + '-' + str(code) + '-' + '{:06}'.format(sequence + 1)
                values['name'] = name
                values['request_number'] = name
        result = super(RequestForm, self).create(values)

        for record in result.request_type_line_id.approval_ids:
            result.approver_ids.create({
                'request_id': result.id,
                'position_id': record.position_id.id,
                'priority': record.priority
            })


        return result

    @api.multi
    def action_confirmed(self):
        sign = self._get_signed_on()
        emp_sign = self.env['account.request.line.approvers']
        emp1_sign = emp_sign.search([('request_id', '=', self.id), ('priority', '=', 1)])
        emp1_sign.write({'employee_id': self.employee_id.id, 'is_approved': True})
        emp2_sign = emp_sign.search([('request_id', '=', self.id), ('priority', '=', 2)])
        emp = self.env['hr.employee'].browse(sign)
        emp2_sign.write({'employee_id': emp.id, 'is_approved': True})
        self.write({'state': 'confirmed'})

    @api.multi
    def action_done(self):
        sign = self._get_signed_on()
        emp_sign = self.env['account.request.line.approvers']
        emp2_sign = emp_sign.search([('request_id', '=', self.id), ('priority', '=', 3)])
        emp = self.env['hr.employee'].browse(sign)
        emp2_sign.write({'employee_id': emp.id, 'is_approved': True})
        self.write({'state': 'done'})

    @api.multi
    def action_cancelled(self):
        self.write({'state': 'cancelled'})

    @api.multi
    def print_request(self):
        emp_sign = self.env['account.request.line.approvers']
        emp1_sign = emp_sign.search([('request_id', '=', self.id), ('priority', '=', 1)])
        emp1_sign.write({'employee_id': self.employee_id.id, 'is_approved': True})
        if self.state == 'draft':
            self.write({'state': 'print_rf',
                        'is_printed': True})
        else:
            self.write({'is_printed': True})
        return self.env['report'].get_action(self, 'mgc_request.report_request')

    @api.multi
    def action_retrieve(self):
        self.write({'state': 'draft', 'is_printed': False})
        emp_sign = self.env['account.request.line.approvers']
        emp1_sign = emp_sign.search([('request_id', '=', self.id), ('priority', 'in', [2, 3])])
        emp1_sign.write({'employee_id': None, 'is_approved': False})

    @api.multi
    def action_void(self):
        self.write({'state': 'void'})

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.company_id = self.employee_id.company_id.id
            self.department_id = self.employee_id.department_id.id

    @api.onchange('request_type_line_id')
    def _onchange_request_type_line_id(self):
        if self.request_type_line_id:
            self.abbreviation = self.company_id.partner_id.abbreviation
            self.type_code = self.request_type_line_id.sub_code
            self.source_id = self.request_type_line_id.source_id.id

    @api.onchange('request_selection')
    def _onchange_request_selection(self):
        if self.request_selection == 'company':
            self.request_company_id = ''
            self.request_department_id = ''
        elif self.request_selection == 'contacts':
            self.partner_id = ''

    @api.multi
    @api.depends('request_number', 'company_id')
    def name_get(self):
        result = []
        for request in self:
            names = ''
            if request.request_number:
                names = '%s' % (request.request_number)

            result.append((request.id, names))
        return result

    @api.multi
    def unlink(self):
        for record in self:
            if record.state not in ('cancelled'):
                raise UserError(
                    _('You cannot delete the request/s. You should return to cancelled instead.'))
        return super(RequestForm, self).unlink()

    @api.multi
    def action_view_order(self):
        action = self.env.ref('purchase.purchase_form_action')
        result = action.read()[0]

        # override the context to get rid of the default filtering
        result['context'] = {'default_request_id': self.id}

        if self.order_ids:
            result['context']['default_line_id'] = self.order_ids[0].id

        # choose the view_mode accordingly
        if len(self.order_ids) != 1:
            result['domain'] = "[('id', 'in', " + str(self.order_ids.ids) + ")]"
        elif len(self.order_ids) == 1:
            res = self.env.ref('purchase.purchase_order_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.order_ids.id
        return result


class RequestFormLine(models.Model):
    _name = 'account.request.line'

    @api.depends('quantity', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            taxes = line.taxes_id.compute_all(line.price_unit, line.request_id.currency_id, line.quantity)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

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

    @api.onchange('product_id', 'description')
    def _onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.name
        if self.description:
            self.date_scheduled = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)


class AccountRequestLineApprovers(models.Model):
    _name = 'account.request.line.approvers'

    request_id = fields.Many2one(comodel_name="account.request", string="Request ID", required=False, )
    position_id = fields.Many2one(comodel_name="account.request.position", string="Authority", required=True, )
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Name of Authority", required=False, )
    is_approved = fields.Boolean(string="Approved")
    priority = fields.Integer(string="Priority", required=False, )
    request_line_approvers = fields.Many2one('account.request.approval', 'Request Line Approval', ondelete='set null', index=True,
                                      readonly=True)

    def _set_additional_fields(self, approvers):
        """ :param approvers : account.request corresponding record
            :rtype line : account.request.line.approvers record
        """
        pass
