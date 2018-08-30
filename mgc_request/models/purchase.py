from odoo import models, fields, api


class InheritPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    request_id = fields.Many2one(comodel_name="account.request", string="Request Reference", required=False)
    request_origin = fields.Char(string="Request Origin", required=False)

    @api.onchange('state', 'order_line')
    def _onchange_allowed_request_ids(self):
        '''
        The purpose of the method is to define a domain for the available
        requests.
        '''
        result = {}

        # A request can be selected only if at least one request line is not already in the invoice
        request_line_ids = self.order_line.mapped('request_line_id')
        request_ids = self.order_line.mapped('request_id').filtered(lambda r: r.request_line <= request_line_ids)

        result['domain'] = {'request_id': [
            ('state', '=', 'done'),
            ('order_status', '=', 'to_order'),
            ('request_type_id.type', '=', 'purchase'),
            ('id', 'not in', request_ids.ids),
        ]}
        return result

    @api.onchange('request_id')
    def _preparing_request_line_ids(self):
        if not self.request_id:
            return {}
        else:
            self.company_id = self.request_id.request_company_id.company_id.id
            self.department_id = self.request_id.request_department_id.department_id.id

        order_lines = self.env['purchase.order.line']
        for record in self.request_id.request_line - self.order_line.mapped('request_line_id'):
            order_line = self.env['purchase.order.line']
            taxes = record.taxes_id
            order_line_tax_ids = record.request_id.fiscal_position_id.map_tax(taxes)
            count = 0

            data = {
                'request_line_id': record.id,
                'company_id': record.request_id.request_company_id.company_id.id,
                'product_id': record.product_id.id,
                'name': record.description,
                'product_qty': record.quantity,
                'price_unit': record.price_unit,
                'order_id': self.id,
                'product_uom': record.product_id.uom_po_id.id,
                'date_planned': record.date_scheduled,
                'currency_id': record.currency_id.id,
                'invoice_line_tax_ids': order_line_tax_ids.ids,
            }
            count += 1
            new_line = order_line.new(data)
            new_line._set_additional_fields(self)
            order_line += new_line

        self.order_line += order_lines
        self.request_id = False

        return {}

    @api.onchange('order_line')
    def _onchange_request_origin(self):
        request_ids = self.order_line.mapped('request_id')
        if request_ids:
            self.request_origin = ', '.join(request_ids.mapped('request_number'))

    @api.multi
    def button_confirm(self):
        order = super(InheritPurchaseOrder, self).button_confirm()
        request_line = self.env['account.request.line']
        request = self.env['account.request']
        for req in self.order_line:
            res_request_line = request_line.search([('id', '=', req.request_line_id.id)])
            res_request_line.update({'purchase_id': req.order_id.id})
            result = request.search([('id', '=', req.request_line_id.request_id.id)])
            result.update({'order_status': 'order'})

        return order


class InheritPurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    request_line_id = fields.Many2one('account.request.line', 'Request Line', ondelete='set null', index=True,
                                       readonly=True)
    request_id = fields.Many2one('account.request', related='request_line_id.request_id', string='Request Number',
                                  store=False, readonly=True, related_sudo=False,
                                  help='Associated Request. Filled in automatically when a Request is chosen on the purchase order.')

    def _set_additional_fields(self, order):
        """ :param order : purchase.order corresponding record
            :rtype line : purchase.order.line record
        """
        pass

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_po_id.id