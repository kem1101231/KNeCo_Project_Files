from odoo import fields, api, _, models
from odoo.exceptions import ValidationError, UserError


class AccountRequestReportHandler(models.TransientModel):
    _name = 'account.request.report.handler'

    start_date = fields.Date(string="Start Date", required=False)
    end_date = fields.Date(string="End Date", required=False)
    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=False)
    department_id = fields.Many2one(comodel_name="hr.department", string="Branch / Department", required=False)
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency", required=False, default=lambda self: self.env.user.company_id.currency_id.id)
    request_type_id = fields.Many2one(comodel_name="account.request.type", string="Request Type", required=False)
    request_type_line_id = fields.Many2one(comodel_name="account.request.type.line", string="Request Sub Type", required=False, )
    state = fields.Selection(string="State", selection=[('draft', 'Draft'),
                                                        ('cancelled', 'Cancelled'),
                                                        ('confirmed', 'Confirmed'),
                                                        ('done', 'Done')], required=False)
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=False)
    responsible_id = fields.Many2one(comodel_name="hr.employee", string="Responsible", required=False,
                                     default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1))
    filters = fields.Selection(string="Filter By", selection=[('none', 'None'),
                                                              ('employee', 'By Employee'),
                                                              ('source', 'Source')], required=False, default='none')
    source_id = fields.Many2one(comodel_name="account.request.source", string="", required=False)
    request_company_id = fields.Many2one(comodel_name="account.request.company", string="Request Through Company",
                                         required=False)
    request_department_id = fields.Many2one(comodel_name="account.request.department",
                                            string="Request Through Branch / Department", required=False)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            self.department_id = ''

    @api.onchange('request_company_id')
    def _onchange_request_company_id(self):
        if self.request_company_id:
            self.request_department_id = ''

    @api.multi
    def print_request_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['company_id', 'department_id', 'request_type_id', 'request_type_line_id',
                                  'employee_id', 'responsible_id', 'request_company_id', 'request_department_id',
                                  'state', 'filters', 'start_date', 'end_date', 'source_id'])[0]

        return self._print_report(data)

    def _print_report(self, data):
        return self.env['report'].sudo().get_action(self, 'mgc_request_kneco.report_request_template', data=data)


class AccountRequestReport(models.AbstractModel):
    _name = 'report.mgc_request_kneco.report_request_template'

    @api.multi
    def render_html(self, docids, data):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        company = data['form']['company_id']
        department = data['form']['department_id']
        employee = data['form']['employee_id']
        request_company = data['form']['request_company_id']
        request_department = data['form']['request_department_id']
        request_type = data['form']['request_type_id']
        request_type_line = data['form']['request_type_line_id']
        source = data['form']['source_id']
        state = data['form']['state']
        start = data['form']['start_date']
        end = data['form']['end_date']

        if employee:
            employee = data['form']['employee_id'][0]
        if source:
            source = data['form']['source_id'][0]
        if company:
            company = data['form']['company_id'][0]
        if request_company:
            request_company = data['form']['request_company_id'][0]
        if department:
            department = data['form']['department_id'][0]
        if request_department:
            request_department = data['form']['request_department_id'][0]
        if request_type:
            request_type = data['form']['request_type_id'][0]
        if request_type_line:
            request_type_line = data['form']['request_type_line_id'][0]

        if company and state:
            records = self.env['account.request'].search([('company_id', '=', company)])
            if records:
                records
            else:
                raise ValidationError("No Records Found!")

        if company and department:
            records = self.env['account.request'].search([('company_id', '=', company),
                                                          ('department_id', '=', department)])
            if records:
                records
            else:
                raise ValidationError("No Records Found!")

        if company and department and request_type:
            records = self.env['account.request'].search([('company_id', '=', company),
                                                          ('department_id', '=', department),
                                                          ('request_type_id', '=', request_type)])
            if records:
                records
            else:
                raise ValidationError("No Records Found!")

        if company and department and employee and request_type and request_type_line:
            records = self.env['account.request'].search([('company_id', '=', company),
                                                          ('department_id', '=', department),
                                                          ('employee_id', '=', employee),
                                                          ('request_type_id', '=', request_type),
                                                          ('request_type_line_id', '=', request_type_line)])
            if records:
                records
            else:
                raise ValidationError("No Records Found!")

        if company and department and source and request_type and request_type_line:
            records = self.env['account.request'].search([('company_id', '=', company),
                                                          ('department_id', '=', department),
                                                          ('source', '=', source),
                                                          ('request_type_id', '=', request_type),
                                                          ('request_type_line_id', '=', request_type_line)])
            if records:
                records
            else:
                raise ValidationError("No Records Found!")

        if company and department and request_type and request_type_line:
            records = self.env['account.request'].search([('company_id', '=', company),
                                                          ('department_id', '=', department),
                                                          ('request_type_id', '=', request_type),
                                                          ('request_type_line_id', '=', request_type_line)])
            if records:
                records
            else:
                raise ValidationError("No Records Found!")

        if company and start and end:
            records = self.env['account.request'].search([('company_id', '=', company),
                                                          ('date_request', '>=', start),
                                                          ('date_request', '<=', end)])
            if records:
                records
            else:
                raise ValidationError("No Records Found!")

        if company and department and start and end:
            records = self.env['account.request'].search([('company_id', '=', company),
                                                          ('department_id', '=', department),
                                                          ('date_request', '>=', start),
                                                          ('date_request', '<=', end)])
            if records:
                records
            else:
                raise ValidationError("No Records Found!")

        if company and department and request_type and start and end:
            records = self.env['account.request'].search([('company_id', '=', company),
                                                          ('department_id', '=', department),
                                                          ('request_type_id', '=', request_type),
                                                          ('date_request', '>=', start),
                                                          ('date_request', '<=', end)])
            if records:
                records
            else:
                raise ValidationError("No Records Found!")

        if company and department and request_type and request_type_line and start and end:
            records = self.env['account.request'].search([('company_id', '=', company),
                                                          ('department_id', '=', department),
                                                          ('request_type_id', '=', request_type),
                                                          ('request_type_line_id', '=', request_type_line),
                                                          ('date_request', '>=', start),
                                                          ('date_request', '<=', end)])
            if records:
                records
            else:
                raise ValidationError("No Records Found!")

        if company and department and employee and request_type and request_type_line and start and end:
            records = self.env['account.request'].search([('company_id', '=', company),
                                                          ('department_id', '=', department),
                                                          ('employee_id', '=', employee),
                                                          ('request_type_id', '=', request_type),
                                                          ('request_type_line_id', '=', request_type_line),
                                                          ('date_request', '>=', start),
                                                          ('date_request', '<=', end)])
            if records:
                records
            else:
                raise ValidationError("No Records Found!")

        if company and department and source and request_type and request_type_line and start and end:
            records = self.env['account.request'].search([('company_id', '=', company),
                                                          ('department_id', '=', department),
                                                          ('source', '=', source),
                                                          ('request_type_id', '=', request_type),
                                                          ('request_type_line_id', '=', request_type_line),
                                                          ('date_request', '>=', start),
                                                          ('date_request', '<=', end)])
            if records:
                records
            else:
                raise ValidationError("No Records Found!")

        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'records': records,

        }

        return self.env['report'].render('mgc_request_kneco.report_request_template', docargs)

