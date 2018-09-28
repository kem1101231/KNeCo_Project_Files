# -*- coding: utf-8 -*-
from odoo import http

# class PosMgcPurchaseConnector(http.Controller):
#     @http.route('/pos_mgc_purchase_connector/pos_mgc_purchase_connector/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_mgc_purchase_connector/pos_mgc_purchase_connector/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_mgc_purchase_connector.listing', {
#             'root': '/pos_mgc_purchase_connector/pos_mgc_purchase_connector',
#             'objects': http.request.env['pos_mgc_purchase_connector.pos_mgc_purchase_connector'].search([]),
#         })

#     @http.route('/pos_mgc_purchase_connector/pos_mgc_purchase_connector/objects/<model("pos_mgc_purchase_connector.pos_mgc_purchase_connector"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_mgc_purchase_connector.object', {
#             'object': obj
#         })