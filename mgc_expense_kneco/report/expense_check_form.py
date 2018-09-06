# -*- coding: utf-8 -*-

import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError


class MGCExpenseCheckForm(models.AbstractModel):
    _name = 'report.mgc_expense_kneco.expense_check_form'
    
    @api.model
    def render_html(self, docids, data):
        docargs = {
            'doc_ids': self.ids,
            'doc_model': None,
            'docs': {'1':'one','2':'two','3':'three','4':'four','5':'five'},
            'time': time,
            'dataInput': data['data'],
        }
        return self.env['report'].render('mgc_expense_kneco.expense_check_form', docargs)
