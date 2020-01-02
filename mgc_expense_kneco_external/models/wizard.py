from odoo import api, models, fields
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError, UserError
import logging
_logger = logging.getLogger(__name__) 

class SaleConfirmLimit(models.TransientModel):
  _name='sale.control.limit.wizard'

  company_id = fields.Many2one(comodel_name="res.company", string="Company/B.U.")
  tax_month_start = fields.Date(string="Tax Month From Date")
  tax_month_end = fields.Date(string="Tax Month To Date")
  include_pending = fields.Boolean(string="Include Pending")
  include_untax = fields.Boolean(string="Include Untaxed")
  
  #my_credit_limit = fields.Float('Partner Credit Limit',readonly=1)
  
  @api.multi
  def agent_exceed_limit(self):
    _logger.debug(' \n\n\t We can do some actions here \n\n\n')

  @api.multi
  def print_transaction(self):

        payables_condition = [('id','!=', 0),('create_date','>=', self.tax_month_start),('create_date','<=', self.tax_month_end)]

        if self.include_untax == False:
          payables_condition.append(('compute_tax','=', '1'))
        
        payables = self.env['mgc.expense.base'].search(payables_condition)

        transaction_line = []
        total_net_of_vat = 0
        total_input_tax = 0
        total_gross = 0
        total_withh_tax = 0
        total_net_amount = 0

        for value in payables:
            vendor_info = self.env['res.partner'].search([('id','=',value.vendor_id.id)], limit=1)

            vated_payable = 'NVAT'
            tax_rate = ''
            
            total_net_of_vat = total_net_of_vat + value.net_of_vat_value
            total_input_tax = total_input_tax + value.input_tax_value
            total_gross = total_gross + value.amount
            total_withh_tax = total_withh_tax + value.tax_amount_value
            total_net_amount = total_net_amount + value.final_amount

            if value.vated_payable == True:
              vated_payable = 'VAT'

            if len(value.tax_ids) != 0:
              tax_rate = str(int(value.tax_ids[0].amount)) + "%"
              
            status_value = 'Pending'
            if value.vated_payable == False:
              status_value = 'No Tax'
            

            else:
              if value.tax_cater_status == True:
                  status_value = 'Deducted'




            transaction_line = transaction_line + [{
                                                      'tin': vendor_info.tin_number,
                                                      'vat': vated_payable,
                                                      'name':vendor_info.name,
                                                      'address':'',
                                                      'net_value': value.net_of_vat_value, #"{:,.2f}".format(float(value.net_of_vat_value)),
                                                      'input_tax':"{:,.2f}".format(float(value.input_tax_value)),
                                                      'gross_value':"{:,.2f}".format(float(value.amount)),
                                                      'tax_rate':tax_rate,
                                                      'withh_tax':"{:,.2f}".format(float(value.tax_amount_value)),
                                                      'net_amomunt':"{:,.2f}".format(float(value.final_amount)),
                                                      'status': status_value,
                                                  }]

        
        fromdateData = str(self.tax_month_start).split('-')
        todateData = str(self.tax_month_end).split('-')

        fromdate = date(day=int(fromdateData[2]), month=int(fromdateData[1]), year=int(fromdateData[0])).strftime('%B %d, %Y')
        todate = date(day=int(todateData[2]), month=int(todateData[1]), year=int(todateData[0])).strftime('%B %d, %Y')

        month = fromdate + " - " + todate

        data = { 'data' : {   
                  'company' : self.company_id.name,
                  'month' : month,
                  'transaction_line' : transaction_line,
                  'total_net_value' : "{:,.2f}".format(float(total_net_of_vat)),
                  'total_input_tax' : "{:,.2f}".format(float(total_input_tax)),
                  'total_gross_value' : "{:,.2f}".format(float(total_gross)),
                  'total_withh_tax' : "{:,.2f}".format(float(total_withh_tax)),
                  'total_net_amomunt' : "{:,.2f}".format(float(total_net_amount)),
                  }
                }
    
        out = self.env['report'].get_action(self, 'mgc_expense_kneco_external.expense_purchase_transaction', data=data)

        return out

class MGCExpenseVendorLedgerWizard(models.TransientModel):
  _name='mgc.vendor.ledger.wizard'

  company_id = fields.Many2one(comodel_name="res.partner", string="Vendor")
  month_start = fields.Date(string="From Date")
  month_end = fields.Date(string="To Date")
  # include_pending = fields.Boolean(string="Include Pending")
  # include_untax = fields.Boolean(string="Include Untaxed")
  
  #my_credit_limit = fields.Float('Partner Credit Limit',readonly=1)
  
  @api.multi
  def agent_exceed_limit(self):
    _logger.debug(' \n\n\t We can do some actions here \n\n\n')

  @api.multi
  def print_ledger(self):
    print("Printing the fucker")
    data = {'data':{'data1': '1','data2':'2',}}
    out = self.env['report'].get_action(self, 'mgc_expense_kneco_external.expense_vendor_ledger', data=data)

    return out

class MGCExpenseAgedPayableWizard(models.TransientModel):
  _name='mgc.aged.payable.wizard'

  sort_by_type = fields.Selection(string="Display By", selection=[('all','All'),('vendor','Vendors'),('due','Payment Due')])
  sort_by_payable_type = fields.Selection(string="By Payable Type", selection=[('all','All'),('cash','Payable w/o PO'),('purchase','Payable w/ PO')])

  @api.multi
  def agent_exceed_limit(self):
    _logger.debug(' \n\n\t We can do some actions here \n\n\n')

  @api.multi
  def print_aging(self):
    for aging in self:

      print_file = ''
      data = {}

      if aging.sort_by_type == 'all':
        print_file = 'mgc_expense_kneco_external.expense_aged_payable'
        data_result = self.get_aging_from_payable()
        
        data = {'data':{
                          'date_prepared': self.crop_date(date.today()),
                          'data_line': data_result['output_list'],
                          'total_invoice':data_result['total_invoice'],
                          'total_paid':data_result['total_paid'],
                          'total_balance':data_result['total_balance'],
                          'total_30':data_result['total_30'],
                          'total_60':data_result['total_60'],
                          'total_90':data_result['total_90'],
                          'total_91':data_result['total_91'],
                          

                        },}

      if aging.sort_by_type == 'vendor':
        print_file = 'mgc_expense_kneco_external.expense_aged_payable_vendor'
        vendor_list = self.get_aging_from_payable_vendor()
        
        data = { 'data':{
                            'date_prepared':self.crop_date(date.today()),
                            'data_line': vendor_list,

        },}
      
      if aging.sort_by_type == 'due':
        print_file = 'mgc_expense_kneco_external.expense_aged_payable_due'
        data_result = self.get_aging_from_payable_by_due()

        data = {'data':{
                          'date_prepared':self.crop_date(date.today()),
                          'data_line':data_result,
                },}

      out = self.env['report'].get_action(self, print_file, data=data)

      return out

  @api.multi
  def get_aging_from_payable(self):
    for aging in self:
      payable_list = self.env['mgc.expense.base'].search([('state','not in',['paid', 'draft', 'check'])])

      output_data = {}
      output_list = []
      total_invoice = 0
      total_paid = 0
      total_balance = 0
      total_30 = 0
      total_60 = 0
      total_90 = 0
      total_91 = 0 
      
      # total__plays0gt,n= 


      for payable in payable_list:

          date_start = payable.create_date
          date_due = payable.date_due_no_vendor_bill

          if payable.vendor_bill_ext != False:
            date_start = payable.vendor_bill_ext.date_invoice
            date_due = payable.vendor_bill_due_date

          date_due_string = str(date_due).split("-")
          date_interval = datetime(int(date_due_string[0]),int(date_due_string[1]),int(date_due_string[2])) - datetime.now()

          day30 = ''
          day60 = ''
          day90 = ''
          day91 = ''
          day0 = ''
          due_status = ''

          if date_interval.days < 31 and date_interval.days > 0:
            day30 = str(payable.balance_amount)
            total_30 = total_30 + payable.balance_amount

          if date_interval.days < 61 and date_interval.days > 30:
            day60 = str(payable.balance_amount)
            total_60 = total_60 + payable.balance_amount
          
          if date_interval.days < 91 and date_interval.days > 60:
            day90 = str(payable.balance_amount)
            total_90 = total_90 + payable.balance_amount
          
          if date_interval.days > 90:
            day91 = str(payable.balance_amount)
            total_91 = total_91 + payable.balance_amount
          
          if date_interval.days <= 0:
            day0 = str(payable.balance_amount)
            total_0 = total_0 + payable.balance_amount
            due_status = 'DUE'

          total_invoice = total_invoice + payable.amount
          total_balance = total_balance + payable.balance_amount
          total_paid = total_paid + payable.tax_amount_value

          output_list.append({
                                  'vendor':payable.vendor_id.name,
                                  'invoice':payable.receipt_number,
                                  'request_ref':payable.request_reference,
                                  'purpose':payable.purpose,
                                  'date_start': self.crop_date(date_start),
                                  'due_date':self.crop_date(date_due),
                                  'invoice_amt':payable.amount,
                                  'paid_amt':payable.catered_amount,
                                  'withhold_amt':payable.tax_amount_value,
                                  'disburse_amt':payable.final_amount,
                                  'amt_balance':payable.balance_amount,
                                  'date_to_go': date_interval.days,
                                  'type':payable.request_type_id_type,
                                  '30':day30,
                                  '60':day60,
                                  '90':day90,
                                  '91':day91,
                                  '0':day0,
                                  'due_status':due_status,
                            })


      output_data['output_list'] = output_list
      output_data['total_invoice'] = total_invoice
      output_data['total_balance'] = total_balance
      output_data['total_paid'] = total_paid

      output_data['total_30'] = total_30
      output_data['total_60'] = total_60
      output_data['total_90'] = total_90
      output_data['total_91'] = total_91

      return output_data
  

  @api.multi
  def get_aging_from_payable_by_due(self):
    for aging in self:
      payable_list = self.env['mgc.expense.base'].search([('state','not in',['paid', 'draft', 'check'])])

      output_data = []
      
      list_30 = []
      list_60 = []
      list_90 = []
      list_91 = []

      invoice_30 = 0
      paid_30 = 0
      balance_30 = 0

      invoice_60 = 0
      paid_60 = 0
      balance_60 = 0

      invoice_90 = 0
      paid_90 = 0
      balance_90 = 0
      
      invoice_91 = 0
      paid_91 = 0
      balance_91 = 0


      for payable in payable_list:

          date_start = payable.create_date
          date_due = payable.date_due_no_vendor_bill

          if payable.vendor_bill_ext != False:
            date_start = payable.vendor_bill_ext.date_invoice
            date_due = payable.vendor_bill_due_date

          date_due_string = str(date_due).split("-")
          date_interval = datetime(int(date_due_string[0]),int(date_due_string[1]),int(date_due_string[2])) - datetime.now()



          if date_interval.days < 31 and date_interval.days > 0:
              list_30.append({
                                  'vendor':payable.vendor_id.name,
                                  'invoice':payable.receipt_number,
                                  'request_ref':payable.request_reference,
                                  'purpose':payable.purpose,
                                  'date_start': self.crop_date(date_start),
                                  'due_date':self.crop_date(date_due),
                                  'invoice_amt':payable.amount,
                                  'paid_amt':payable.catered_amount,
                                  'withhold_amt':payable.tax_amount_value,
                                  'disburse_amt':payable.final_amount,
                                  'amt_balance':payable.balance_amount,
                                  'date_to_go': date_interval.days,
                                  'type':payable.request_type_id_type,
                            })
              
              invoice_30 = invoice_30 + payable.amount
              paid_30 = paid_30 + payable.catered_amount
              balance_30 = balance_30 + payable.balance_amount
          
          if date_interval.days < 61 and date_interval.days > 30:
              list_60.append({
                                  'vendor':payable.vendor_id.name,
                                  'invoice':payable.receipt_number,
                                  'request_ref':payable.request_reference,
                                  'purpose':payable.purpose,
                                  'date_start': self.crop_date(date_start),
                                  'due_date':self.crop_date(date_due),
                                  'invoice_amt':payable.amount,
                                  'paid_amt':payable.catered_amount,
                                  'withhold_amt':payable.tax_amount_value,
                                  'disburse_amt':payable.final_amount,
                                  'amt_balance':payable.balance_amount,
                                  'date_to_go': date_interval.days,
                                  'type':payable.request_type_id_type,
                            })
              invoice_60 = invoice_60 + payable.amount
              paid_60 = paid_60 + payable.catered_amount
              balance_60 = balance_60 + payable.balance_amount

          if date_interval.days < 91 and date_interval.days > 60:
              list_90.append({
                                  'vendor':payable.vendor_id.name,
                                  'invoice':payable.receipt_number,
                                  'request_ref':payable.request_reference,
                                  'purpose':payable.purpose,
                                  'date_start': self.crop_date(date_start),
                                  'due_date':self.crop_date(date_due),
                                  'invoice_amt':payable.amount,
                                  'paid_amt':payable.catered_amount,
                                  'withhold_amt':payable.tax_amount_value,
                                  'disburse_amt':payable.final_amount,
                                  'amt_balance':payable.balance_amount,
                                  'date_to_go': date_interval.days,
                                  'type':payable.request_type_id_type,
                            })
              invoice_90 = invoice_90 + payable.amount
              paid_90 = paid_90 + payable.catered_amount
              balance_90 = balance_90 + payable.balance_amount
          
          if date_interval.days > 90:
              list_91.append({
                                  'vendor':payable.vendor_id.name,
                                  'invoice':payable.receipt_number,
                                  'request_ref':payable.request_reference,
                                  'purpose':payable.purpose,
                                  'date_start': self.crop_date(date_start),
                                  'due_date':self.crop_date(date_due),
                                  'invoice_amt':payable.amount,
                                  'paid_amt':payable.catered_amount,
                                  'withhold_amt':payable.tax_amount_value,
                                  'disburse_amt':payable.final_amount,
                                  'amt_balance':payable.balance_amount,
                                  'date_to_go': date_interval.days,
                                  'type':payable.request_type_id_type,
                            })
              
              invoice_91 = invoice_91 + payable.amount
              paid_91 = paid_91 + payable.catered_amount
              balance_91 = balance_91 + payable.balance_amount
          
      output_data.append({
                                'name':'0-30 days',
                                'total_invoice':invoice_30,
                                'total_paid':paid_30,
                                'total_balance':balance_30,
                                'payable_list':list_30,
                            })

      output_data.append({
                                'name': '31-60 days',
                                'total_invoice':invoice_60,
                                'total_paid':paid_60,
                                'total_balance':balance_60,
                                'payable_list':list_60,
                            })

      output_data.append({
                                'name':'61-90 days',
                                'total_invoice':invoice_90,
                                'total_paid':paid_90,
                                'total_balance':balance_90,
                                'payable_list':list_90,
                            })

      output_data.append({
                                'name': '91 days and beyond',
                                'total_invoice':invoice_91,
                                'total_paid':paid_91,
                                'total_balance':balance_91,
                                'payable_list':list_91,
                            })


      return output_data

  @api.multi
  def get_aging_from_payable_vendor(self):
    for aging in self:

      vendor_list = self.env['mgc.expense.vendors'].search([('id','!=', 0)])

      output_data_vendor = []

      for vendor in vendor_list:

        payable_list = self.env['mgc.expense.base'].search([('vendor_id','=',vendor.vendor_id.id), ('state','not in',['paid', 'draft', 'check']) ])

        if len(payable_list) != 0:
        
          output_data = {}
          output_list = []
          total_invoice = 0
          total_paid = 0
          total_balance = 0
          total_30 = 0
          total_60 = 0
          total_90 = 0
          total_91 = 0 
          
          # total__plays0gt,n= 

          for payable in payable_list:

              date_start = payable.create_date
              date_due = payable.date_due_no_vendor_bill

              if payable.vendor_bill_ext != False:
                date_start = payable.vendor_bill_ext.date_invoice
                date_due = payable.vendor_bill_due_date

              date_due_string = str(date_due).split("-")
              date_interval = datetime(int(date_due_string[0]),int(date_due_string[1]),int(date_due_string[2])) - datetime.now()

              day30 = ''
              day60 = ''
              day90 = ''
              day91 = ''
              day0 = ''
              due_status = ''

              if date_interval.days < 31 and date_interval.days > 0:
                day30 = str(payable.balance_amount)
                total_30 = total_30 + payable.balance_amount

              if date_interval.days < 61 and date_interval.days > 30:
                day60 = str(payable.balance_amount)
                total_60 = total_60 + payable.balance_amount
              
              if date_interval.days < 91 and date_interval.days > 60:
                day90 = str(payable.balance_amount)
                total_90 = total_90 + payable.balance_amount
              
              if date_interval.days > 90:
                day91 = str(payable.balance_amount)
                total_91 = total_91 + payable.balance_amount
              
              if date_interval.days <= 0:
                day0 = str(payable.balance_amount)
                total_0 = total_0 + payable.balance_amount
                due_status = 'DUE'

              total_invoice = total_invoice + payable.amount
              total_balance = total_balance + payable.balance_amount
              total_paid = total_paid + payable.tax_amount_value

              output_list.append({
                                      'invoice':payable.receipt_number,
                                      'request_ref':payable.request_reference,
                                      'purpose':payable.purpose,
                                      'date_start': self.crop_date(date_start),
                                      'due_date':self.crop_date(date_due),
                                      'invoice_amt':payable.amount,
                                      'paid_amt':payable.catered_amount,
                                      'withhold_amt':payable.tax_amount_value,
                                      'disburse_amt':payable.final_amount,
                                      'amt_balance':payable.balance_amount,
                                      'date_to_go': date_interval.days,
                                      'type':payable.request_type_id_type,
                                      '30':day30,
                                      '60':day60,
                                      '90':day90,
                                      '91':day91,
                                      '0':day0,
                                      'due_status':due_status,
                                })


          output_data['output_list'] = output_list
          output_data['total_invoice'] = total_invoice
          output_data['total_balance'] = total_balance
          output_data['total_paid'] = total_paid

          output_data['total_30'] = total_30
          output_data['total_60'] = total_60
          output_data['total_90'] = total_90
          output_data['total_91'] = total_91
          output_data['name'] = vendor.name


          output_data_vendor.append(output_data)


      print(":::::::::::::::::::::::::::::::::::::::::::::::::::")
      print(output_data_vendor)

      return output_data_vendor
  
  @api.multi
  def crop_date(self, dateInput):
        
        str_date = str(dateInput).split(' ')
        date_of_request = datetime.strptime(str_date[0], '%Y-%m-%d')#%I:%M%
        
        return date_of_request.strftime('%b %d, %Y')
