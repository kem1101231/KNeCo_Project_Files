from odoo import api, models, fields
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError, UserError
import xmlrpclib
import odoorpc

class Access_Configuration(models.Model):
	_name = "mgc.expense.access.configuration"

	name = fields.Char(string="Connection Name")
	dbname = fields.Char(string="Database Name")
	server_ip = fields.Char(string="Server IP")
	port_number = fields.Integer(string="Port Number")
	username = fields.Char(string="Username")
	password = fields.Char(string="Password")
	access_type = fields.Selection(string="Access Type", selection=[('request','Access Request Forms'),('order','Access Purchase Orders')])

