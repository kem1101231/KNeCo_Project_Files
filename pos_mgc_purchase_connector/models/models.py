# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class pos_mgc_purchase_connector(models.Model):
#     _name = 'pos_mgc_purchase_connector.pos_mgc_purchase_connector'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100