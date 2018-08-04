from odoo import models, fields, api

class Request_Form(models.Model):
    _name = 'mgc_request.base'

    name = fields.Char(string='Name')
    request_code = None # request code or the reference number of the request of the document
    requestor_id = None # requesting personnel
    purpose = None # purpose of the request
    request_type = None # type of purpose of the request
    request_status = None # status of the request

    l1_approve_status = None # level 1 or the basic approval status of the request
    l1_approve_date = None  # date of level 1 or the basic approval status of the request

    l2_approve_status = None # level 2 approval status of the request (if there's any)
    l2_approve_date = None  #  date of level 2 approval status of the request (if there's any)

    l3_approve_status = None # level 3 approval status of the request (if there's any)
    l3_approve_date = None  # date of level  3 approval status of the request (if there's any)

    l4_approve_status = None # level 4 approval status of the request (if there's any)
    l4_approve_date = None  # date of level 4 approval status of the request (if there's any)

class Request_Types(models.Model):
    _name = 'mgc_request.types'

    name = None
    out_request = None
    transaction_type = None
    l1_approval_reference = None
    l1_approval_reference_data = None
    l2_approval_reference  = None
    l2_approval_reference_data = None
    l3_approval_reference  = None
    l3_approval_reference_data = None
    l4_approval_reference  = None
    l4_approval_reference_data = None


class Request_Conduct_Types(models.Model):
    _name = 'mgc.request.conduct_types'

    name = None
    l1_position_approval = None
    l2_position_approval = None
    l3_position_approval = None
    l4_position_approval = None


