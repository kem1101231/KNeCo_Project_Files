# -*- coding: utf-8 -*-
from odoo import http

# class MgcRequestKneco(http.Controller):
#     @http.route('/mgc_request_kneco/mgc_request_kneco/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mgc_request_kneco/mgc_request_kneco/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mgc_request_kneco.listing', {
#             'root': '/mgc_request_kneco/mgc_request_kneco',
#             'objects': http.request.env['mgc_request_kneco.mgc_request_kneco'].search([]),
#         })

#     @http.route('/mgc_request_kneco/mgc_request_kneco/objects/<model("mgc_request_kneco.mgc_request_kneco"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mgc_request_kneco.object', {
#             'object': obj
#         })