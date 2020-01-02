from odoo import api, models, fields
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError, UserError


class PayableTtransaction(models.Model):
	_name = 'mgc.payables.transactions'