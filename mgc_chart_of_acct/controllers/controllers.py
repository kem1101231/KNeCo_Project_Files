# -*- coding: utf-8 -*-
from odoo import http

# class MgcChartOfAcct(http.Controller):
#     @http.route('/mgc_chart_of_acct/mgc_chart_of_acct/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mgc_chart_of_acct/mgc_chart_of_acct/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mgc_chart_of_acct.listing', {
#             'root': '/mgc_chart_of_acct/mgc_chart_of_acct',
#             'objects': http.request.env['mgc_chart_of_acct.mgc_chart_of_acct'].search([]),
#         })

#     @http.route('/mgc_chart_of_acct/mgc_chart_of_acct/objects/<model("mgc_chart_of_acct.mgc_chart_of_acct"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mgc_chart_of_acct.object', {
#             'object': obj
#         })