from odoo import models, fields, api

class Request_Form(models.Model):
    _name = 'mgc_request_form'

    name = fields.Char(string='Name')
    curre_user = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.user)



