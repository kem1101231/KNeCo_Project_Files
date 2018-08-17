# -*- coding: utf-8 -*-
from odoo import http

# class MgcExpenseKneco(http.Controller):
#     @http.route('/mgc_expense_kneco/mgc_expense_kneco/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mgc_expense_kneco/mgc_expense_kneco/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mgc_expense_kneco.listing', {
#             'root': '/mgc_expense_kneco/mgc_expense_kneco',
#             'objects': http.request.env['mgc_expense_kneco.mgc_expense_kneco'].search([]),
#         })

#     @http.route('/mgc_expense_kneco/mgc_expense_kneco/objects/<model("mgc_expense_kneco.mgc_expense_kneco"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mgc_expense_kneco.object', {
#             'object': obj
#         })