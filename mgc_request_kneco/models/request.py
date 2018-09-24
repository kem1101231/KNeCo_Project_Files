from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date
from odoo.addons import decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class MGC_Request(models.Model):
	_name = "mgc.requeust.form.base"
	desciption = "MGC Request Forms"

	name = None
	requestor_id = None
	request_department = None
	request_company = None
	request_type = None
	request_name = None
	request_purpose = None

class MGC_Request_Types(models.Model):
	_name = "mgc.requeust.form.types"


class MGC_Request_Names(models.Model):
	_name = "mgc.requeust.form.names"	

class MGC_Request_Types(models.Model):
	_name = "mgc.requeust.form.types"

class MGC_Request_Types(models.Model):
	_name = "mgc.requeust.form.types"
