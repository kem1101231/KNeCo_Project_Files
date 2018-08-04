# -*- coding: utf-8 -*-
from odoo import http

# class MgcRequestFormDev1(http.Controller):
#     @http.route('/mgc_request_form_dev_1/mgc_request_form_dev_1/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mgc_request_form_dev_1/mgc_request_form_dev_1/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mgc_request_form_dev_1.listing', {
#             'root': '/mgc_request_form_dev_1/mgc_request_form_dev_1',
#             'objects': http.request.env['mgc_request_form_dev_1.mgc_request_form_dev_1'].search([]),
#         })

#     @http.route('/mgc_request_form_dev_1/mgc_request_form_dev_1/objects/<model("mgc_request_form_dev_1.mgc_request_form_dev_1"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mgc_request_form_dev_1.object', {
#             'object': obj
#         })