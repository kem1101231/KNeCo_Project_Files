from odoo import api, models, fields
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError, UserError
import xmlrpclib

class XMLRPC_Connection:
	url = 'http://localhost:8069'
	db = 'Odoo_1_1'
	uname = 'odoo'
	password = 'odoo'

	uid = None
	model = None

	def __init__(self):
		common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
		self.uid = common.authenticate(self.db, self.uname, self.password, {})
		self.model = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(self.url))

	def getData(self, inputNumber):
		return self.model.execute_kw(self.db, self.uid, self.password, 'account.request', 'search_read', [[['name', '=', inputNumber],]],{'fields': ['name',], 'limit': 0})



class MGC_Purchase_Extend(models.Model):
	_inherit = 'purchase.order'

	mgc_request_id = fields.Integer(string="Request Reference")
	mgc_request_number = fields.Char(string="Request Number")	

	@api.onchange('mgc_request_number')
	def _onchange_mgc_request_number(self):
		if self.mgc_request_number:
			xmlrpcdata = XMLRPC_Connection().getData(self.mgc_request_number)

			if xmlrpcdata == []:
				raise ValidationError("Invalid RF Reference. RF does not exists")
			else:
				xmlrpcdataFetch = xmlrpcdata[0]
				self.mgc_request_id = xmlrpcdataFetch['id']
	            	
	 



