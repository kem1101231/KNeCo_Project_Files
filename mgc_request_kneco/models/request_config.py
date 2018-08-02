from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date
from odoo.addons import decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class AccountRequestType(models.Model):
    _name = 'account.request.type'

    name = fields.Char(string="Name", required=True, )
    type_line = fields.One2many(comodel_name="account.request.type.line", inverse_name="request_type_id", string="Type Line", required=True, )
    request_company_id = fields.Many2one(comodel_name="account.request.company", string="Company", required=True)
    type = fields.Selection(string="Type", selection=[('cash', 'Cash'), ('purchase', 'Purchase'), ('payment', 'Payment'),
                                                      ('work', 'Work Order'), ('travel', 'Travel'), ('others', 'Others')],
                            required=False, default='cash')
    request_department_id = fields.Many2one(comodel_name="account.request.department", string="Branch / Department", required=True)
    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=False, )
    department_id = fields.Many2one(comodel_name="hr.department", string="Branch / Department", required=False)
    code = fields.Char(string="Code", required=False, )
    active = fields.Boolean(string="Active", required=True, default=True)

    @api.model
    def create(self, values):
        if 'name' in values:
            if values['name']:
                values['name'] = values.get('name').upper().strip()

        result = super(AccountRequestType, self).create(values)

        result.company_id = result.request_company_id.company_id.id
        result.department_id = result.request_department_id.department_id.id

        return result

    @api.multi
    def write(self, values):
        if 'name' in values:
            if values['name']:
                values['name'] = values.get('name').upper().strip()
        result = super(AccountRequestType, self).write(values)

        return result

    @api.onchange('request_company_id', 'request_department_id')
    def _get_code(self):
        code = ''
        if self.request_company_id:
            company_code = self.request_company_id.code
        else:
            company_code = ''
        if company_code:
            code = '%s' % (company_code)

        if self.request_department_id:
            department = self.request_department_id.code
        else:
            department = ''
        if department:
            res_code = self.search_count([('active', '=', True), ('request_department_id', '=', self.request_department_id.id),
                                          ('request_company_id', '=', self.request_company_id.id)])
            codes = '{:02}'.format(res_code + 1)
            code = '%s-%s' % (department, codes)
        self.code = code


class AccountRequestTypeLine(models.Model):
    _name = 'account.request.type.line'

    name = fields.Char(string="Description", required=False)
    request_type_id = fields.Many2one(comodel_name="account.request.type", string="Request Type", required=False, )
    source_id = fields.Many2one(comodel_name="account.request.source", string="Source", required=False, )
    request_company_id = fields.Many2one(comodel_name="account.request.company", string="Company", required=False,
                                 related="request_type_id.request_company_id")
    request_department_id = fields.Many2one(comodel_name="account.request.department", string="Branch / Department", required=False,
                                    related="request_type_id.request_department_id")
    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=False, related="request_type_id.company_id")
    department_id = fields.Many2one(comodel_name="hr.department", string="Branch / Department", required=False, related="request_type_id.department_id")
    active = fields.Boolean(string="Active", default=True)
    sub_code = fields.Char(string="Sub Code", required=False, )
    date_effectivity = fields.Datetime(string="Date Effective", required=False, index=True)
    approval_ids = fields.One2many(comodel_name="account.request.approval", inverse_name="request_type_line_id",
                                   string="Approvals", required=False, )

    @api.model
    def create(self, values):
        if 'name' in values:
            if values['name']:
                values['name'] = values.get('name').upper().strip()
        result = super(AccountRequestTypeLine, self).create(values)

        return result

    @api.multi
    def write(self, values):
        if 'name' in values:
            if values['name']:
                values['name'] = values.get('name').upper().strip()
        result = super(AccountRequestTypeLine, self).write(values)

        return result

    @api.onchange('name')
    def _get_sub_code(self):
        if self.name:
            sub_code = self.search_count([('active', '=', True), ('request_type_id', '=', self.request_type_id.id)])
            code = '{:02}'.format(sub_code + 1)
            self.sub_code = str(self.request_type_id.code) + '' + code
            self.date_effectivity = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            self.company_id = self.request_type_id.company_id.id
            self.department_id = self.request_type_id.department_id.id


class AccountRequestApprovals(models.Model):
    _name = 'account.request.approval'

    position_id = fields.Many2one(comodel_name="account.request.position", string="Authority", required=True, )
    amount = fields.Float(string='Amount', required=True, digits=dp.get_precision('Product Price'))
    priority = fields.Selection(string="Priority", required=True, selection=[(1, '1'), (2, '2'), (3, '3')], default=1)
    request_type_line_id = fields.Many2one(comodel_name="account.request.type.line", string="Request line", required=False, )


class AccountRequestCompany(models.Model):
    _name = 'account.request.company'

    name = fields.Char(string="Business Unit", required=False, )
    abbreviation = fields.Char(string="Abbreviation", required=False, )
    code = fields.Char(string="Code", required=False, )
    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=True, )
    active = fields.Boolean(string="Active", default=True)
    department_line_ids = fields.One2many(comodel_name="account.request.department", inverse_name="request_company_id", string="Departments", required=False, )
    is_MSG = fields.Boolean(string="is MSG")

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            code = self.search_count([('active', '=', True)])
            codes = '{:02}'.format(code + 1)
            self.code = codes
            abbr = self.company_id.partner_id.abbreviation
            self.abbreviation = abbr
            self.active = True
            name = self.company_id.name
            self.name = name
            if self.abbreviation == 'EPFC':
                self.is_MSG = True

    @api.model
    def create(self, values):
        if 'name' in values:
            values['name'] = values.get('name').upper().strip()
        if 'abbreviation' in values:
            values['abbreviation'] = values.get('abbreviation').upper().strip()

        return super(AccountRequestCompany, self).create(values)

    @api.multi
    def write(self, values):
        if 'name' in values:
            values['name'] = values.get('name').upper().strip()
        if 'abbreviation' in values:
            values['abbreviation'] = values.get('abbreviation').upper().strip()

        return super(AccountRequestCompany, self).write(values)

    @api.multi
    def action_generate_department(self):
        dept = self.env['hr.department']
        request_departments = self.env['account.request.department']
        if self.is_MSG == True:
            msg_ids = dept.search([('company_id', '=', self.company_id.id), ('parent_id.name', '=', 'MSG')])
            code = 01
            for msg in msg_ids:
                if msg.parent_id:
                    exist = request_departments.search([('department_id', '=', msg.id)])
                    if exist.department_id.id == msg.id:
                        raise ValidationError("Department Already Exists!")
                    else:
                        codes = str(self.code) + '-' + '{:02}'.format(code)
                        name = msg.name
                        request_departments.create({
                            'department_id': msg.id,
                            'name': name.upper(),
                            'code': codes,
                            'active': True,
                            'request_company_id': self.id,
                        })
                        code += 1
        else:
            dept_ids = dept.search([('company_id', '=', self.company_id.id)])
            code = 01
            for depts in dept_ids:
                if not depts.parent_id:
                    exist = request_departments.search([('department_id', '=', depts.id)])
                    if exist.department_id.id == depts.id:
                        raise ValidationError("Department Already Exists!")
                    else:
                        codes = str(self.code) + '-' + '{:02}'.format(code)
                        name = depts.name
                        request_departments.create({
                            'department_id': depts.id,
                            'name': name.upper(),
                            'code': codes,
                            'active': True,
                            'request_company_id': self.id,
                        })
                    code += 1


class AccountRequestDepartment(models.Model):
    _name = 'account.request.department'

    name = fields.Char(string="Name", required=False)
    department_id = fields.Many2one(comodel_name="hr.department", string="Branch / Department", required=False, )
    code = fields.Char(string="Code", required=False)
    request_company_id = fields.Many2one(comodel_name="account.request.company", string="Business Unit", required=False, )
    active = fields.Boolean(string="Active", default=True)
    company_id = fields.Many2one(comodel_name="res.company", string="Company", related="request_company_id.company_id", required=False, )

    _sql_constraints = [
        ('department_unique', 'unique(name, department_id)', 'Branch / Department must be unique!'),
    ]

    def _set_additional_fields(self, department):
        """ :param department : account.request.company corresponding record
            :rtype line : account.request.department record
        """
        pass

    @api.model
    def create(self, values):
        if 'name' in values:
            values['name'] = values.get('name').upper().strip()
        return super(AccountRequestDepartment, self).create(values)

    @api.onchange('department_id')
    def _onchange_department_id(self):
        if self.department_id:
            department = self.search([('department_id', '=', self.department_id.id)])
            if department.id == self.department_id.id:
                raise ValidationError("Job Position already exists!")
            else:
                self.name = self.department_id.name
                code_count = self.search_count([('active', '=', True), ('request_company_id', '=', self.request_company_id.id)])
                code = str(self.request_company_id.code) + '-' + '{:02}'.format(code_count + 1)
                self.code = code


class AccountRequestSource(models.Model):
    _name = 'account.request.source'

    name = fields.Char(string="Name", required=False, )
    active = fields.Boolean(string="Active", default=True)

    @api.model
    def create(self, values):
        if 'name' in values:
            values['name'] = values.get('name').upper().strip()
        return super(AccountRequestSource, self).create(values)

    @api.multi
    def write(self, values):
        if 'name' in values:
            values['name'] = values.get('name').upper().strip()
        return super(AccountRequestSource, self).write(values)


class AccountRequestPosition(models.Model):
    _name = 'account.request.position'

    name = fields.Char(string="Name", required=True, )
    job_id = fields.Many2one(comodel_name="hr.job", string="Job Position", required=False)
    responsible_id = fields.Many2one(comodel_name="hr.employee", string="Responsible", required=False, )

    _sql_constraints = [
        ('name_unique', 'unique(name, job_id)', 'Name and Job Position must be unique!'),
    ]

    @api.model
    def create(self, values):
        if 'name' in values:
            values['name'] = values['name'].upper().strip()

        return super(AccountRequestPosition, self).create(values)

    @api.multi
    def write(self, values):
        if 'name' in values:
            values['name'] = values['name'].upper().strip()

        return super(AccountRequestPosition, self).write(values)

    @api.onchange('job_id')
    def _onchange_job_id(self):
        if self.job_id:
            name = self.job_id.name
            self.name = name.upper()






