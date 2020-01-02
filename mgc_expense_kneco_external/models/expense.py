from odoo import api, models, fields, _
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError, UserError
import xmlrpclib
import odoorpc
from odoo_rpc_connection import OdooRPC_Connection
from calendar import monthrange

class MGC_Expense(models.Model):
    _name = 'mgc.expense.base'
    _description = 'Payable/Expense'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'

    #odooRPCRequestConnection = OdooRPC_Connection()
    request_connection = {}
    
    ext_Access_Data = {}

    # def _amount_all(self):
    #     for expense in self:
    #         amount_untaxed = 0.0
    #         for line in expense.check_list:
    #             amount_untaxed += line.amount
    #         expense.update({
    #             'check_list_amount': amount_untaxed,
    #         })
    '''
    def _get_total_debit(self):
        for expense in self:
           
            amount_untaxed = 0.0
            for line in expense.transactionRecord:
                if line.entry_type == 'debit':
                    amount_untaxed += line.amount
            
            expense.update({
                'debit_total_amount': amount_untaxed,
            })
    
    def _get_total_credit(self):
        for expense in self:
           
            amount_untaxed = 0.0
            for line in expense.transactionRecord:
                if line.entry_type == 'credit' or line.entry_type == 'neg-credit':
                    amount_untaxed += line.amount
            
            expense.update({
                'credit_total_amount': amount_untaxed,
            })    
    '''
    def _check_if_balanced(self):
        for expense in self:
           
            is_balanced = False

            if expense.credit_total_amount == expense.debit_total_amount:
                is_balanced = True    

            expense.update({
                'is_balanced': is_balanced,
            }) 
    
    def _check_if_shared(self):
        for expense in self:
           
            is_shared = False

            for itemLine in expense.debitList:
                if itemLine.is_shared == True:
                    is_shared = True

            expense.update({
                'is_shared': is_shared,
            }) 
    
    # def _get_total_tax_value(self):
    #     for expense in self:
           
    #         total_tax_value = 0

    #         for tax_line in expense.tax_ids:
    #             tax_value = expense.amount * (tax_line.amount_ref * .01)
    #             total_tax_value = total_tax_value + tax_value
    #         expense.update({
    #             'tax_amount_value': total_tax_value,
    #         }) 
    
    
    @api.depends('tax_ids', 'debitList', 'compute_tax', 'vated_payable')
    def _get_tax_value(self):
        for expense in self:

            amount_data = self.get_base_and_tax()

            amount_base = amount_data['base']
            total_tax = amount_data['tax']
            input_tax = amount_data['input_tax']
            tax_to_display = 0

            if expense.tax_amount_value == 0:

                expense.tax_amount_value_ref = total_tax
                expense.tax_amount_value = total_tax
                expense.input_tax_value = input_tax
                expense.update({
                                    'tax_amount_value_ref': total_tax, 
                                    'input_tax_value': input_tax,  
                                    'tax_amount_value': total_tax,
                                })
   
    @api.depends('tax_ids', 'debitList', 'compute_tax', 'vated_payable')
    def _get_input_tax_value(self):
        for expense in self:

            amount_data = self.get_base_and_tax()
            input_tax = amount_data['input_tax']
            tax_to_display = 0

            if expense.tax_amount_value != 0:
                expense.input_tax_value = input_tax
                expense.update({ 
                                    'input_tax_value': input_tax,  
                                })
    
    @api.depends('tax_ids', 'debitList', 'compute_tax', 'vated_payable')
    def _get_net_of_vat_value(self):
        for expense in self:

            amount_data = self.get_base_and_tax()
            base_amount = amount_data['base']
            invoice_amount = amount_data['invoice_amount']
            tax_to_display = 0


            expense.net_of_vat_value = base_amount
            expense.amount = invoice_amount

            expense.update({ 
                            'net_of_vat_value': base_amount,
                            'amount': invoice_amount,
                        })
        
    @api.depends('tax_ids', 'debitList', 'compute_tax', 'vated_payable', 'tax_amount_value')
    def _get_total_tax_value(self):
        for expense in self:
            
            amount_data = self.get_base_and_tax()
            
            amount_base = amount_data['base']
            total_tax = amount_data['tax']

            expense.total_tax_amount_value = (expense.amount - amount_base) + expense.tax_amount_value
            
            expense.update({
                                'total_tax_amount_value':(expense.amount - amount_base) + expense.tax_amount_value, 
                            })


   
    # @api.depends('debitList', 'tax_ids', 'compute_tax')
    # def _get_final_amount_value(self):
    #     for expense in self:
    #         amount_to_display = 0
    #         if expense.compute_tax == '1':
    #             if expense.vated_payable == True:
    #                 pass



    @api.depends('debitList', 'tax_ids', 'compute_tax', 'tax_amount_value')
    def _get_final_amount_value(self):
        for expense in self:
            amount_to_display = 0

            expense.final_amount = expense.amount - expense.tax_amount_value
            expense.update({'final_amount':expense.amount - expense.tax_amount_value,})


    def get_base_and_tax(self):
        for expense in self:
            
            amount_base = 0
            total_tax = 0
            input_tax = 0
            invoice_amount = 0

            if expense.compute_tax == '1': 
                
                for line in expense.debitList:
                    line_amount = line.amount
                    
                    if line.entry_type == 'debit':

                        if expense.vated_payable == True:
                            taxed_line_amount = round(line.amount / 1.12, 2)
                            amount_base = amount_base + taxed_line_amount
                            input_tax = input_tax + line_amount - taxed_line_amount
                        
                        else:
                            amount_base = amount_base + line.amount

                        invoice_amount = line_amount
                
                total_tax = round((amount_base * expense.tax_ids), 2)   
            
            else:
                amount_base = expense.amount

            return {'base': amount_base, 'tax':total_tax, 'input_tax': input_tax, 'invoice_amount':invoice_amount}

    def confirm_payable(self):
        
        for expense in self:
            
            expense.validated_by = int(self.env.user.id)

            expense.state = 'confirm'

            soa_id_ref = 0

            if expense.add_to_soa == '1':

                soa_id = self.env['mgc.expense.soa'].search([('vendor', '=', expense.vendor_id.id), ('state','=','draft')], limit=1)
                #info_data = self.env['res.partner.vendor.additional.information'].search([('vendor','=',expense.vendor_id.id)],limit=1)

                
                if len(soa_id) == 0 :
                    print(soa_id)
                    soa_gen_id = self.env['mgc.expense.soa'].create({'vendor':expense.vendor_id.id,
                            
                            })

                    self.env['mgc.expense.soa.line'].create({
                                                                'soa_vendor':expense.vendor_id.id,
                                                                'soa_id': soa_gen_id.id,
                                                                'payable_id': expense.id,
                                                            })
                    soa_id_ref = soa_gen_id.id


                else:
                    self.env['mgc.expense.soa.line'].create({
                                                                'soa_vendor':expense.vendor_id.id,
                                                                'soa_id': soa_id.id,
                                                                'payable_id': expense.id,

                                                            })
                    soa_id_ref = soa_id.id
            
            expense.update({'soa_ref_id':soa_id_ref,})        
    
    def validate_payable(self):
        for payable in self:

            journal_entries = self.env['account.move'].search([('id','=', payable.journal_id.id)])

            min_value = 0
            max_value = 0
            min_value_id = 0
            max_value_id = 0


            for line in journal_entries.line_ids:
                if line.credit != 0:
                    credit_value = line.credit
                    credit_id = line.id

                    if min_value == 0:
                        min_value = credit_value
                        min_value_id = credit_id

                    else:
                        if min_value < credit_value:
                            max_value = credit_value
                            max_value_id = credit_id
                        else:
                            max_value = min_value
                            min_value = credit_value

                            max_value_id = min_value_id
                            min_value_id = credit_id
            
            debit_entry = self.env['mgc.expense.base.line'].search([('expense_id','=', payable.id), ('amount','=', min_value), ('entry_type','=','credit')])

            if min_value != payable.tax_amount_value and len(debit_entry) != 0:

                self.env.cr.execute("update mgc_expense_base_line set amount = "+str(payable.tax_amount_value)+" where id = "+str(debit_entry.id))
                self.env.cr.execute("update account_move_line set credit = "+str(payable.tax_amount_value)+" where id = "+str(min_value_id))
                self.env.cr.execute("update account_move_line set credit = "+str(payable.final_amount)+" where id = "+str(max_value_id))

                print("Do the Fricking update")

            # itemLine = []
            # if payable.vated_payable == True:
            #     itemLine.append({
            #                         'expense_id': payable.id,
            #                         'description': 'Withholding Tax for Payable - ' + payable.name,                           
            #                         'amount': payable.tax_amount_value,
            #                     })
            #     itemLine.append({
            #                         'expense_id': payable.id,
            #                         'description': 'Input Tax for Payable - ' + payable.name,                           
            #                         'amount': payable.total_tax_amount_value - payable.tax_amount_value,
            #                     })
            # else:
            #     itemLine.append({
            #                         'expense_id': payable.id,
            #                         'description': 'Withholding Tax for Payable - ' + payable.name,                       
            #                         'amount': payable.tax_amount_value,
            #                     })

            # for item in itemLine:
            #     self.env['mgc.expense.base.line'].create({
            #                                                'expense_id': item['expense_id'],
            #                                                'description': item['description'],
            #                                                'entry_type': 'credit',
            #                                                'amount': item['amount'],
            #                                             })

            # journal_result_to_remove = self.journal_line_update(payable.journal_id, payable)
            # self.clean_journal_lines(journal_result_to_remove)

            self.journal_update('post', payable.journal_id.id)
            
            payable.update({'state':'open',})


    def cancel_payable(self):
        for payable in self:
            payable.journal_update(update_type='draft',id_entry=payable.journal_id.id)
            payable.update({'state':'cancel'})

    def set_as_draft(self):
        for payable in self:
            payable.update({'state':'check',})
            
    def journal_update(self, update_type, id_entry):

        journal = self.env['account.move'].search([('id','=', id_entry)], limit=1)

        journal_state = ''
        journal_line_reconcile = False

        if update_type == 'post':
            journal.write({'state': 'posted'})

            for journal_item in journal.line_ids:
                item = self.env['account.move.line'].search([('id','=',journal_item.id),])
                item.write({'reconciled':True})

        else:
            self.env.cr.execute("update account_move set state = 'draft' where id = "+ str(id_entry))
            
            for journal_item in journal.line_ids:
                self.env.cr.execute("update account_move_line set reconciled = FALSE where id = "+str(journal_item.id))


    def print_journal(self):
        for expense in self:
            journal = self.env['account.move'].search([('id', '=', expense.journal_id.id),])
            info_data = self.env['res.partner.vendor.additional.information'].search([('vendor','=',expense.vendor_id.id)],limit=1)

            journal_line_value = []
            credit_total = 0
            debit_total = 0

            for journal_item in journal.line_ids:
                
                account_entry = str(journal_item.account_id.code)+" - "+str(journal_item.account_id.name)
                label = journal_item.name
                debit = journal_item.debit
                credit = journal_item.credit

                debit_total = debit_total + debit
                credit_total = credit_total + credit

                debit_value = ''
                credit_value = ''

                if debit != 0:
                    debit_value = "{:,.2f}".format(float(debit))

                if credit != 0:
                    credit_value = "{:,.2f}".format(float(credit))

                if label == '/':
                    label = "Payable to vendor: " + str(expense.vendor_id.name)

                journal_line_value = journal_line_value + [{'account':account_entry,
                                                            'label': label,
                                                            'debit':debit_value,
                                                            'credit': credit_value,
                                                            },]


            request_type = ''
            purchase_order = ''
            vendor_bill = ''

            if expense.request_type_id_type == 'cash':
                request_type = 'Request for Cash'

            else:
                request_type = 'Request to Purchase'
                purchase_order = expense.purchase_id_number_ext.name
                vendor_bill = expense.vendor_bill_ext.number
            
            vat_string = 'Not a VAT Vendor'

            if expense.vendor_id.vatable_vendor == True:
                vat_string = 'A VAT vendor'
                

            data = {'data':{    'vendor': expense.vendor_id.name,
                                'tin': expense.vendor_id.tin_number,
                                'vat':vat_string,
                                'address':expense.vendor_id.street,
                                'receipt': expense.receipt_number,
                                'request_type': request_type,
                                'request':expense.request_reference,
                                'purchase':purchase_order,
                                'bill':vendor_bill,
                                'journal': expense.name,
                                'date': self.crop_date(expense.create_date),        
                                'journal_line':journal_line_value,
                                'credit_total': "{:,.2f}".format(float(credit_total)),
                                'debit_total':"{:,.2f}".format(float(debit_total)),
                                'create_uid': expense.create_uid.name,
                                'validated_by': self.validated_by.name,
                            }
                    }
            

            out = self.env['report'].get_action(self, 'mgc_expense_kneco_external.expense_purchase_journal', data=data)
            
            return out
   
    @api.model
    def crop_date(self, dateInput):
        
        str_date = str(dateInput).split(' ')
        date_of_request = datetime.strptime(str_date[0], '%Y-%m-%d')#%I:%M%
        return date_of_request.strftime('%b %d, %Y')

    @api.model
    def _get_payable_balance(self):
        for payable in self:
            balance_value = 0
            if payable.catered_amount != 0:
                balance_value = payable.final_amount - payable.catered_amount

            payable.balance_amount = balance_value 

    @api.model
    def _get_untaxed_balance(self):
        for payable in self:
            balance_value = 0
            if payable.catered_amount != 0:
                balance_value = payable.amount - payable.catered_untaxed_amount

            payable.balance_untaxed_amount = balance_value 


    # @api.depends('vendor_id')
    # def _get_vendor_additional_info(self):
    #     for expense in self:
    #         #info_data = self.env['res.partner.vendor.additional.information'].search([('vendor','=',expense.vendor_id.id)],limit=1)
    #         expense.update({'dummy_field': str('hello world'),})

    '''    
    def getRequestList(self):
                    outList = []
                    self.odooRPCRequestConnection.set_connection(self.request_connection['server_ip'],self.request_connection['port_number'],self.request_connection['dbname'],self.request_connection['username'],self.request_connection['password'])
                    odoorpcData = self.odooRPCRequestConnection.findID('account.request', [('state', '=', 'done')])#('mgc_request_number_name', '=', self.request_reference.name)
        
                    odooData = self.odooRPCRequestConnection.odoo.env['account.request']
                    odooList = odooData.search([])
                    for i in odooLisst:
                        outList = outList + [(str(i), odooData.browse(int(i)).name),]
        
                    return outList
    '''  
    '''    
    @api.multi      
    def db_source_list(self):
        
        selection_list = []

        request_search = self.env['mgc.expense.access.configuration'].search([('access_type', '=', 'request'),])
        ext_access_search = self.env['mgc.expense.access.configuration'].search([('access_type', '!=', 'request'),])
        
        self.request_connection['dbname'] = request_search.dbname
        self.request_connection['server_ip'] = request_search.server_ip
        self.request_connection['port_number'] = request_search.port_number
        self.request_connection['username'] = request_search.username
        self.request_connection['password'] = request_search.password

        for x in ext_access_search:
            self.ext_Access_Data[x.dbname] = (x.dbname, x.username, x.password, x.server_ip, x.port_number)
            selection_list = selection_list + [(x.dbname, x.dbname),] 


        return selection_list
    '''

    is_changed = False

    name = fields.Char(string="Transaction Number")
    amount = fields.Float(string="Reference Amount", required=True)
    amount_ref = fields.Float(string="Invoice Amount", store=False, default="0")
    with_held_amount = fields.Monetary(string="Withheld Amount", default="0")
    final_amount = fields.Float(string="Payable Amount", required=True, default="0", compute="_get_final_amount_value")
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)    

    expense_credit_account = fields.Many2one(comodel_name="account.account", string="Credit Entry", ondelete='cascade', required=True)
    expense_tax_credit_account = fields.Many2one(comodel_name="account.account", string="Tax Credit Entry", ondelete='cascade')
    expense_in_tax_credit_account = fields.Many2one(comodel_name="account.account", string="Input Tax Credit Entry", ondelete='cascade')
    expense_type = fields.Selection(selection=[('item','Payment for Purchased Items'),('service','Payment for Rendered Service/s'), ('bill', 'Payment for Bills'), ('cash','Advance for Operation') ], string="Expense Type")

    purpose = fields.Text(string="Purpose", required=True)

    add_to_soa = fields.Selection(selection=[('0','No'),('1','Yes')], string="Add to S.O.A.", default="1")
    soa_ref_id = fields.Many2one(comodel_name="mgc.expense.soa", string="Included on SOA")
    is_efo = fields.Boolean(string="A.F.O.")
    payable_vendor = fields.Many2one(comodel_name="mgc.expense.vendor", string="Vendor")
    vendor_id = fields.Many2one(string="Vendor/Biller", comodel_name="res.partner")
    date_due_no_vendor_bill = fields.Date(string="Date Due")

    dummy_field = fields.Char(string="Dummy", store=False, default="0")
    vendor_tin = fields.Char(string="T.I.N.", related="vendor_id.tin_number", store=False)
    vendor_vat = fields.Boolean(string="With VAT", related="vendor_id.vatable_vendor", store=False)
    vendor_reputation = fields.Selection(string="Vendor Reputation", selection=[('good','Good'),('nor','Inconsistent'),('bad','Bad')], related="vendor_id.vendor_reputation", store=False)

    journal_id = fields.Many2one(comodel_name="account.move", string="Journal Entry")
    journal_journal = fields.Many2one(comodel_name="account.journal", string="Journal")

    with_tax = fields.Boolean(string="With Taxes")
    tax_ids = fields.Selection(string="Taxes", selection=[(0.01,'1%'),(0.02,'2%')])
    tax_amount_value_ref = fields.Monetary(string="Tax Amount", compute="_get_tax_value")
    tax_amount_value = fields.Monetary(string="Tax Amount")
    total_tax_amount_value = fields.Monetary(string="Total Tax Amount", compute="_get_total_tax_value", store=True)
    input_tax_value = fields.Monetary(string="Input Tax", compute="_get_input_tax_value", store=True)
    net_of_vat_value = fields.Monetary(string="Net of V.A.T.", compute="_get_net_of_vat_value", store=True)

    @api.onchange('tax_amount_value_ref')
    def _onchange_tax_amount_value_ref(self):
        if self.tax_amount_value_ref:
            print("================================================================")
            print(self.tax_amount_value_ref)
            self.tax_amount_value = self.tax_amount_value_ref

    #account_entry = fields.Many2one('account.account', string="COA entry")

    debitList = fields.One2many(comodel_name="mgc.expense.base.line", inverse_name="expense_id",string="Payable's Entries", required=False)
    #transactionRecord = fields.One2many(comodel_name="mgc.specialized.accounting.ledger", inverse_name="reference_pay", string="Transaction Journal", required=False)
    journal_line = fields.One2many(related="journal_id.line_ids", string="Transaction Journal")

    #debit_total_amount = fields.Float(compute="_get_total_debit", string="Debit Amount", store=False)
    #credit_total_amount = fields.Float(compute="_get_total_credit", string="Credit Amount", store=False)
    is_balanced = fields.Boolean(compute="_check_if_balanced", string="Is Balanced", store=False)
    is_shared = fields.Boolean(string="A Shared Expense", compute="_check_if_shared")

    #check_list = fields.One2many('mgc.expense.checks', 'expense_id', string="Prepared Checks")
    #check_list_amount = fields.Float(string='Prepared Checks Amount', compute='_amount_all')
    approve_status = fields.Boolean(string="Approval Status")
    state = fields.Selection(string="Status", selection=[('draft', 'Draft'),('check','Checking'),('cancel','Canceled'),('done','Done'),('confirm','Confirmed'),('open','Open'),('tag','Tagged'), ('paid','Paid')], default='draft', required=False, track_visibility='onchange')    
    payment_status = fields.Selection(string="Payment Status", selection=[('pending','Pending'), ('paid','Paid')], default="pending" )    

    request_reference = fields.Char(store=True,string="Request Reference", required=True)
    request_reference_id = fields.Integer(string="Request ID")
    tagged_request = fields.Boolean(string="Request Already Tagged")
    #request_ref_type_name = fields.Char(related="request_reference.request_type_line_id.fs_class_id.name",string="Request Reference Type Name")
    request_ref_type = fields.Char(string="Reference Type",store=True)
    request_bu_id = fields.Char( string="Business Unit")
    department = fields.Char(string="Department")
    request_type = fields.Char(string="Request Type")
    request_name = fields.Char(string="Request Name")
    request_purpose = fields.Text( string="Request Purpose")
    request_with_spec_instr = fields.Boolean(string="")
    request_spec_instr = fields.Text( string="Request Special Inst:")  
    request_type_id_type = fields.Selection(string="Reference Type", selection=[('cash','Cash Request'),('purchase','Purchase Order')])

    purchase_id_source_type = fields.Char(string='PO Source DB', store=True, default="non-internal")
            
    #purchase_id_ext = fields.Integer(string="Purchase ID")
    purchase_id_number_ext = fields.Many2one(string="Purchase Order", comodel_name="purchase.order")
    purchase_order_name = fields.Char(string="Purchase Order Name", related="purchase_id_number_ext.name")

    #vendor_bill_id_ext = fields.Integer(string="Vendor Bill ID")
    vendor_bill_ext = fields.Many2one(string="Vendor Bill", comodel_name="account.invoice")
    
    vendor_bill_vendor = fields.Many2one(comodel_name="res.partner", related ="vendor_bill_ext.partner_id", string="Vendor/Biller", store=False)
    
    vendor_bill_date = fields.Date(string="Billing Date", related="vendor_bill_ext.date_invoice", store=False)
    vendor_bill_due_date = fields.Date(string="Bill Due Date", related="vendor_bill_ext.date_due", store=False)
    receipt_number = fields.Char(string="Invoice / Document Number")

    #created_by = fields.Many2one(string="Approve by", comodel_name="res.user", default= lambda self: self.env.user)
    validated_by = fields.Many2one(string="Validate by", comodel_name="res.users")
    is_catered =  fields.Boolean(string="Is Catered")
    vated_payable = fields.Boolean(string="With Input Tax")
    
    catered_untaxed_amount = fields.Monetary(string="Catered Untaxed Amount")   
    catered_amount = fields.Monetary(string="Already Paid Amount")
    catered_tax_amount = fields.Monetary(string="Already Paid Tax")
    catered_tax_from_rate_amount = fields.Monetary(string="Already Paid Tax from Rate")
    balance_tax_amount = fields.Monetary(string="Balance Tax to Pay")
    balance_amount = fields.Monetary(string="Balance to Pay", compute="_get_payable_balance")
    balance_untaxed_amount = fields.Monetary(string="Balance Untaxed Amount", compute="_get_untaxed_balance")

    compute_tax = fields.Selection(selection=[('1','Yes'),('0','No')], string="Compute Taxes", default="0")
    company_id = fields.Many2one(comodel_name="res.company", string="Business Unit")
    tax_cater_status = fields.Boolean(string="Tax Paid")
    
    @api.onchange('compute_tax') 
    def _onchange_compute_tax(self):
        if self.compute_tax:
            if self.compute_tax == '0':
                self.tax_amount_value = 0
            else:
                if self.tax_amount_value == 0:
                    self.tax_amount_value = self.tax_amount_value_ref



    #default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)

    '''
    purchase_id = fields.Many2one('purchase.order', string="Purchase Order")
    vendor_bill = fields.Many2one('account.invoice', string="Vendor Bill")
    '''


    #account_location_bu = fields.Many2one(comodel_name="res.company", related="account_location.bu_id_id", string="BU Test", store=False)

    #shareList = fields.One2many('mgc.expense.base.shared.bu','expense_id',string="Sharing B.U.")

    prep_id = None #fields.Many2one('res.partner', string="Prepared by",ondelete='cascade')
    date_prep = None #fields.Date(string="Preparation Date")

    # @api.onchange('vendor_id')
    # def _onchange_vendor_id(self):
    #     if self.vendor_id:
    #         info_data = self.env['res.partner.vendor.additional.information'].search([('vendor','=',self.vendor_id.id)],limit=1)

    #         if len(info_data) != 0:
    #             print("here")
    #             print(info_data.tin_number)
    #             self.vendor_tin = info_data.tin_number
    #             self.vendor_vat = info_data.vatable_vendor
    #             self.vendor_reputation = info_data.vendor_reputation 
    
    # @api.onchange('dummy_field')
    # def _onchange_dummy_field(self):
    #     if self.dummy_field:

    #         self.vendor_tin = self.vendor_id.tin_number
    #         self.vendor_vat = self.vendor_id.vatable_vendor
    #         self.vendor_reputation = self.vendor_id.vendor_reputation
    
    # @api.onchange('compute_tax')
    # def _onchange_compute_tax(self):
    #     for payable in self:

    #         debitList = payable.debitList

    #         if payable.compute_tax == '1':
    #             debitList.append([{
    #                                                     'expense_id': payable.id,
    #                                                     'description': 'Withholding Tax for Payable - ' + str(payable.name),
    #                                                     'entry_type': 'credit',
    #                                                     'amount': payable.total_tax_amount_value,
    #                                                     'account': payable.expense_tax_credit_account.id,
                                    
    #                                                 }])
    #         print("======  ****** ==================")
    #         print(debitList)                                          
  

    @api.onchange('expense_credit_account')
    def _onchange_expense_credit_account(self):
        if self.expense_credit_account:
            self.company_id = self.expense_credit_account.company_id


    @api.onchange('is_efo')
    def _onchange_is_efo(self):
        for payable in self:
            search_ref = ''

            if payable.is_efo == True:
                payable.expense_type = 'cash'
                search_ref = 'aof'
            else:
                payable.expense_type = ''
                search_ref = 'cash'

            journal_ref = self.env['mgc.expense.base.cash.type.journal'].search([('bind_for', '=', search_ref)], limit=1)

            payable.journal_journal = journal_ref.journal_id.id
            payable.expense_credit_account = journal_ref.account_entry.id




    @api.onchange('request_reference')
    def _onchange_request_reference(self):
        if self.request_reference:

            request_search = self.env['mgc.expense.access.configuration'].search([('access_type', '=', 'request'),])

            odoorpcConnection = OdooRPC_Connection()
            odoorpcConnection.set_connection(request_search.server_ip,request_search.port_number,request_search.dbname,request_search.username,request_search.password)
            odoorpcData = odoorpcConnection.findID('account.request', [('name', '=', self.request_reference)])#('mgc_request_number_name', '=', self.request_reference.name)
            if len(odoorpcData) != 0:

            	requestData = odoorpcConnection.odoo.env['account.request'].browse(int(odoorpcData[0]))
                if requestData.state in ['draft','approval','declined','cancel', 'cater']:
                    if requestData.state in ['draft','approval']:
                        raise ValidationError("Invalid Request Form Number. \n * Request process hasn't been completed yet.")
                    if requestData.state == 'declined':
                        raise ValidationError("Invalid Request Form Number. \n * Request was declined by one of the approvers.")
                    if requestData.state == 'cancel':
                        raise ValidationError("Invalid Request Form Number. \n * Request was canceled by the requesting personel.")
                    if requestData.state == 'cater':
                        raise ValidationError("Invalid Request Form Number. \n * Request was closed as it was already catered.")


                else:
                    if requestData.fund_reference == 'corporate':
                        if requestData.request_type_id.type in ['cash','purchase','payment']:
                            if requestData.state == 'tag':
                                self.tagged_request = True

                            self.request_reference_id = int(int(odoorpcData[0]))
                            self.request_bu_id = requestData.company_id.name
                            self.department = requestData.department_id.name
                            self.request_purpose = requestData.purpose
                            self.request_type_id_type = requestData.request_type_id.type
                            self.request_type = requestData.request_type_id.id
                            self.purpose = requestData.purpose
                            self.request_with_spec_instr = requestData.with_special_instruction
                            self.request_spec_instr = requestData.spec_instruction

                            requestLineList = requestData.request_line

                            debit_list = []

                            for x in requestLineList:
                                debit_list.append({ 'description': x.description.name,
            	                                    'entry_type':'debit',
            	                                    'amount': x.price_total,
            	                                  })
                                
                            self.update({'debitList': debit_list})

                            if requestData.request_type_id.type == 'cash' or  requestData.request_type_id.type == 'payment':
                                self.amount = requestData.amount_total
                                self.amount_ref = requestData.amount_total
                                
                                journal_ref = self.env['mgc.expense.base.cash.type.journal'].search([('bind_for', '=', 'cash')], limit=1)
                                
                                self.journal_journal = journal_ref.journal_id.id
                                self.expense_credit_account = journal_ref.account_entry.id
                                self.add_to_soa = '0'

                            else:
                                self.amount = 0
                                self.amount_ref = 0
                        else:
                            raise ValidationError("Invalid Request to Use. \n * The request your trying to use doens't require to conduct any monetary related transaction.")
                    else:
                        raise ValidationError("Invalid Request to Use.\n * The request that your trying to use was already been tagged on a petty cash fund transaction.")

            else:
                raise ValidationError("Invalid Request Form Number. \n * No request form number matched to your given number.")

    '''
    @api.onchange('debitList')
    def _onchange_debitList(self):
    	if self.debitList:
    		self.final_amount = self.amount
    '''
  
    @api.model
    def create(self, values):
            
            temp_tin = ''
            temp_vat = False
            temp_ven_rep = ''
            
            now = date.today()

            if 'amount' in values:
               if values['amount']:
                    
                    creditValue = 0.0
                    for recordLine in values['debitList']:
                       if recordLine[2]['entry_type'] == 'credit':
                           creditValue += recordLine[2]['amount']
                    
                    monthData = monthrange(now.year, now.month)                    
                    sequence = sequence = self.search_count([('id', '!=', '0'),('create_date','>=', str(now.year)+'-'+str(now.month)+'-1'),('create_date','<=',str(now.year)+'-'+str(now.month)+'-'+str(monthData[1]))])
                    years = date.strftime(date.today(), '%y')
                    month = date.strftime(date.today(), '%m')
                    name = 'P-' + str(years) +'-'+str(month)+'-'+'{:05}'.format(sequence + 1)                        
                    
                    values['name'] = name
                    #values['amount'] = values['amount_ref']
                    #values['final_amount'] = values['amount'] - creditValue
                    values['state'] = 'check'
                    temp_tin = values['vendor_tin']
                    temp_vat = values['vendor_vat']
                    temp_ven_rep = values['vendor_reputation']

            result =  super(MGC_Expense, self).create(values)


            debitList = result.debitList
            itemList = []

            if result.compute_tax == '1':
                if result.vated_payable == True:
                    itemList.append({
                                    'expense_id': result.id,
                                    'description': 'Input Tax for Payable - ' + str(result.name),
                                    'entry_type': 'neg-debit',
                                    'amount': result.input_tax_value,
                                    'account': result.expense_in_tax_credit_account.id,
                                })
                    
                    itemList.append({
                                    'expense_id': result.id,
                                    'description': 'Withholding Tax for Payable - ' + str(result.name),
                                    'entry_type': 'credit',
                                    'amount': result.tax_amount_value,
                                    'account': result.expense_tax_credit_account.id,
                                })
                else:
                    itemList.append({
                                    'expense_id': result.id,
                                    'description': 'Withholding Tax for Payable - ' + str(result.name),
                                    'entry_type': 'credit',
                                    'amount': result.total_tax_amount_value,
                                    'account': result.expense_tax_credit_account.id,
                                })  

            for item in itemList:
                debitList.create({
                                    'expense_id': result.id,
                                    'description': item['description'],
                                    'entry_type': item['entry_type'],
                                    'amount': item['amount'],
                                    'account': item['account'],
                                })


            vendor_gen_id = self.env['mgc.expense.vendors'].search([('vendor_id','=',result.vendor_id.id)])

            if len(vendor_gen_id) != 0:
                result.payable_vendor = vendor_gen_id.id
            
            else:
                vendor_create_id = self.env['mgc.expense.vendors'].create({'vendor_id':result.vendor_id.id, 'name':result.vendor_id.name})
                result.payable_vendor = vendor_create_id.id

            request_type = result.request_type_id_type
            journal_result_to_remove = []
           
            if request_type == 'cash':
               print(result.company_id.name)
               journal_gen_id = self.env['account.move'].create({
           													'name':str(result.name)+"/"+str(result.journal_journal.name),
		                                                    'journal_id':result.journal_journal.id,
		                                                    'date': datetime.now(),
		                                                    'company_id':result.company_id.id,
		                                                    'state':'draft',
		                    				})

               result.update({'journal_id':journal_gen_id.id})
               amount_ref = result.amount_ref
               self.create_journal_line(journal_gen_id, result)

          
       	    else:
                journal_id = self.env['account.move'].search([('id', '=', result.journal_id.id)], limit=1)

                journal_result_to_remove = self.journal_line_update(journal_id, result)
            
            self.clean_journal_lines(journal_result_to_remove)

            return result


    def create_journal_line(self, journal_ref, payable_ref):
               
               itemList = []
               amount_ref = 0

               for item in payable_ref.debitList:
                   credit_value = 0
                   debit_value = 0
                   if item.entry_type == 'debit':
                        if payable_ref.vated_payable == True and payable_ref.compute_tax == '1':
   
                            debit_value = round(item.amount / 1.12, 2)
                        else:
                            debit_value = item.amount
                   if item.entry_type == 'neg-debit':
                        debit_value = item.amount

                   if item.entry_type == 'credit':
                       credit_value = item.amount
                       amount_ref = amount_ref - credit_value
                   
                   if item.is_shared:
                       for shareLine in item.shareList:
                           amount_share = debit_value * (shareLine.share * 0.01)
                           account_to_use = 0
                           if shareLine.account.id != False:
                                account_to_use = shareLine.account.id
                           else:
                                account_to_use = item.account.id
                           
    
                           itemList.append({
                                            'move_id':journal_ref.id,
                                            'account_id':account_to_use,
                                            'partner_id':payable_ref.vendor_id.id,
                                            'name':item.description+" "+shareLine.buid.bu_code+" share",
                                            'debit': amount_share,
                                            'credit': 0,
                                            'date_maturity':payable_ref.date_due_no_vendor_bill,
                                            'reconciled':False,
                                            'company_id':payable_ref.company_id.id,
                            })
                            
                   else:
                       itemList.append({
                                        'move_id':journal_ref.id,
                                        'account_id':item.account.id,
                                        'partner_id':payable_ref.vendor_id.id,
                                        'name':item.description,
                                        'debit': debit_value,
                                        'credit': credit_value,
                                        'date_maturity':payable_ref.date_due_no_vendor_bill,
                                        'reconciled':False,
                                        'company_id':payable_ref.company_id.id,
                        })

               name_value = ''
               if payable_ref.is_efo == True:
                    name_value = "Advances for Operation "+payable_ref.name+" as requested for/by " + payable_ref.vendor_id.name
               else:
                    name_value = "Payable: " + payable_ref.name+" for vendor: "+payable_ref.vendor_id.name

               itemList.append({
                                    'move_id':journal_ref.id,
                                    'account_id':payable_ref.expense_credit_account.id,
                                    'partner_id':payable_ref.vendor_id.id,
                                    'name': name_value,
                                    'debit':0,
                                    'credit':payable_ref.amount - abs(amount_ref),
                                    'date_maturity':payable_ref.date_due_no_vendor_bill,
                                    'reconciled':False,
                                    'company_id':payable_ref.company_id.id,
                                })

               # for x in itemList:
               #  print("++++++++++++++++++++")
               #  print("Description: " + str(x['name']))
               #  print("debit: "+ str(x['debit']))
               #  print("credit: "+str(x['credit']))
               #  print("============")


               journal_ref.update({'line_ids':itemList})
               print("Journal Line Created")

    def journal_line_update(self, journal_ref, payable_ref):
                
                journal_result_to_remove = []

                itemList = []
                sum_credit_amount = 0 
                itemList = []

                total_credit_here = 0
                total_debit_here = 0

                for item in payable_ref.debitList:
                    
                    if item.entry_type == 'credit':
                        total_credit_here = total_credit_here + item.amount
                        itemList.append({
                                                'move_id':payable_ref.journal_id.id,
                                                'account_id':item.account.id,
                                                'partner_id':payable_ref.vendor_id.id,
                                                'name':item.description,
                                                'debit': 0,
                                                'credit': item.amount,
                                                'date_maturity':payable_ref.date_due_no_vendor_bill,
                                                'reconciled':False,
                                                'company_id':payable_ref.company_id.id,
                                })
                    
                    if item.entry_type == 'debit':
                        
                        for line in payable_ref.journal_id.line_ids:

                            journal_result_to_remove = journal_result_to_remove + [line.id,]

                        if item.is_shared:

                            total_shared = 0

                            journal_lines = self.env['account.move.line'].search([('move_id','=',journal_ref.id)])
                            amount_base = 0

                            if payable_ref.vated_payable == True and payable_ref.compute_tax == '1':
                                amount_base = round(item.amount / 1.12, 2)
                            else:
                                amount_base = item.amount    

                            for shareLine in item.shareList:
                                amount_share = amount_base * (shareLine.share * 0.01)
                                total_shared = total_shared + amount_share

                                account_to_use = 0
                                if shareLine.account.id != False:
                                    account_to_use = shareLine.account.id
                                else:
                                    account_to_use = item.account.id

                                total_debit_here = total_debit_here + amount_share
                                itemList.append({

                                              'move_id':payable_ref.journal_id.id,
                                              'account_id':account_to_use,
                                              'partner_id':payable_ref.vendor_id.id,
                                              'name':item.description+" "+shareLine.buid.bu_code+" share",
                                              'debit': amount_share,
                                              'credit': 0,
                                              'date_maturity':payable_ref.date_due_no_vendor_bill,
                                              'reconciled':False,
                                              'company_id':payable_ref.company_id.id,
                                                
                              })
                        
                        else:
                            amount_to_journal = 0
                            if payable_ref.vated_payable == True and payable_ref.compute_tax == '1':
                                amount_to_journal = round(item.amount / 1.12, 2)
                            else:
                                amount_to_journal = item.amount

                            total_debit_here = total_debit_here + amount_to_journal
                            itemList.append({
                                                'move_id':payable_ref.journal_id.id,
                                                'account_id':item.account.id,
                                                'partner_id':payable_ref.vendor_id.id,
                                                'name':item.description,
                                                'debit': amount_to_journal,
                                                'credit': 0,
                                                'date_maturity':payable_ref.date_due_no_vendor_bill,
                                                'reconciled':False,
                                                'company_id':payable_ref.company_id.id,
                                })

                    if item.entry_type == 'neg-debit':
                        total_debit_here = total_debit_here + item.amount
                        itemList.append({

                                         'move_id':payable_ref.journal_id.id,
                                         'account_id':item.account.id,
                                         'partner_id':payable_ref.vendor_id.id,
                                         'name':item.description,
                                         'debit': item.amount,
                                         'credit': 0,
                                         'date_maturity':payable_ref.date_due_no_vendor_bill,
                                         'reconciled':False,
                                         'company_id':payable_ref.company_id.id,
                                                        
                            })

                        
                 
                itemList.append({

                                 'move_id':payable_ref.journal_id.id,
                                 'account_id':payable_ref.expense_credit_account.id,
                                 'partner_id':payable_ref.vendor_id.id,
                                 'name':"Payable: " + payable_ref.name,
                                 'debit': 0,
                                 'credit': payable_ref.amount - total_credit_here,
                                 'date_maturity':payable_ref.date_due_no_vendor_bill,
                                 'reconciled':False,
                                 'company_id':payable_ref.company_id.id,
                                                
                    })

                # print(" =========== =============== =============== =============== ===================== ")
                # for x in itemList:
                #     print("Entry: "+str(x['name']))
                #     print("Credit Amount: "+str(x['credit']))
                #     print("Debit Amount: "+str(x['debit']))

                journal_ref.update({'line_ids':itemList})

                return journal_result_to_remove


    def clean_journal_lines(self, journal_result_to_remove):
            if journal_result_to_remove != []:
                for id in journal_result_to_remove:
                    print("deleting")
                    self.env.cr.execute("delete from account_move_line where id = " + str(id) + "")

  
    @api.multi
    def write(self, vals):

            # for request in self:

                # amount_data = request.get_base_and_tax()

                # base = amount_data['base']
                # pay_vat_tax_value = request.amount - base
                # total_tax_value = pay_vat_tax_value + request.tax_amount_value 
                # pay_final_value = request.amount - total_tax_value

                # # vals['total_tax_amount_value'] = total_tax_value 
                # # vals['final_amount'] = pay_final_value

                # request.update({'total_tax_amount_value': total_tax_value,'final_amount':pay_final_value})

            result =  super(MGC_Expense, self).write(vals)

            if self.state == 'tag':
                pass

            if self.state == 'paid':
                
                request_search = self.env['mgc.expense.access.configuration'].search([('access_type', '=', 'request'),])
                odoorpcConnection = OdooRPC_Connection()
                odoorpcConnection.set_connection(request_search.server_ip,request_search.port_number,request_search.dbname,request_search.username,request_search.password)
                odoorpcData = odoorpcConnection.findID('account.request', [('name', '=', self.request_reference)])
                requestData = odoorpcConnection.odoo.env['account.request'].browse(int(odoorpcData[0]))
                
                requestData.update({'state':'cater',})

            return result

            '''
            for record in result.debitList:
                                                   
                                                   
                                                   #entry_type = 'debit'
                                                   #    if record.entry_type == 'neg-credit' or record.entry_type == 'credit':
                                                   #        entry_type = 'credit
                                                   
                                                   self.env['mgc.specialized.accounting.ledger'].create({  'reference_code': result.name,
                                                                                                           'reference_pay': result.id,
                                                                                                           'reference_type': 'payable', 
                                                                                                           'location_id': result.account_location.id,
                                                                                                           'description': record.description,
                                                                                                           'account_name': record.account.id,
                                                                                                           'entry_type': record.entry_type,
                                                                                                           'amount': record.amount,
                                                                                                       })
                                               
                                               self.env['mgc.specialized.accounting.ledger'].create({  'reference_code': result.name,
                                                                                                       'reference_pay': result.id,
                                                                                                       'reference_type': 'payable', 
                                                                                                       'location_id':  result.account_location.id,
                                                                                                       'description': result.purpose,
                                                                                                       'account_name': result.expense_type.id,
                                                                                                       'entry_type':'credit',
                                                                                                       'amount': result.final_amount,
                                                                                                       
                                                                                                       })
                                       
                                               if result.is_balanced == False:
                                                   raise ValidationError("Entries are not balanced. \n \n** Debit: " + str(result.debit_total_amount)+" \n * Credit: " + str(result.credit_total_amount))
                                               else: 
            '''

    def save_cash_payable(self):
         pass      




    '''    
    @api.onchange('request_reference')
    def _onchange_request_reference(self):
        
        if self.request_reference:
            purString = ''
            purString = purString + self.request_reference.purpose

            self.purpose = purString

            #self.request_ref_type = self.request_reference.request_type_line_id.fs_class_id.id
            self.request_type_id_type = str(self.request_reference.request_type_id.type)

            if self.request_reference.request_type_id.type == 'cash' or self.request_reference.request_type_id.type == 'payment':
                self.amount = self.request_reference.amount_total
                self.amount_ref = self.request_reference.amount_total
            else:
                self.amount = 0
            
            sequence = self.search_count([('id', '!=', '0')])
            years = date.strftime(date.today(), '%y')
            name = 'P-' + str(years) + '-' + '{:09}'.format(sequence + 1)
            self.name = name
            #self.bu_id = self.request_reference.request_source_company_id
    '''
    '''    
    @api.onchange('purchase_id_number_ext')
    def _onchange_purchase_id_number_ext(self):
        if self.purchase_id_number_ext:
            xmlrpc_accessData = self.ext_Access_Data[self.purchase_id_source_type]
            
            odoorpcConnection = OdooRPC_Connection()
            odoorpcConnection.set_connection(xmlrpc_accessData[3], xmlrpc_accessData[4],xmlrpc_accessData[0], xmlrpc_accessData[1], xmlrpc_accessData[2])
            odoorpcData = odoorpcConnection.findID('purchase.order', [('name', '=', self.purchase_id_number_ext), ('mgc_request_number_name', '=', self.request_reference)])

            if odoorpcData == []:
                raise ValidationError("Invalid Purchase Order. \n * Purcahse Order may not be existing or the purchase order is not referenced to the given Request Form")
            else:
                self.purchase_id_ext = odoorpcData[0]
    '''

    # @api.onchange('tax_ids')
    # def _onchange_tax_ids(self):
    #     if self.tax_ids:
    #         total_tax_value = 0
    #         debit_lines = []

    #         for tax_line in self.tax_ids:
    #             tax_value = self.amount * (tax_line.amount * 0.01)
    #             total_tax_value = total_tax_value + tax_value
    #             debit_lines.append({ 
    #                                  'description': tax_line.name,
    #                                  'entry_type':'credit',
    #                                  'amount': tax_value,
    #                                  'ref_description':tax_line.name,
    #                                  # 'ref_line_id':item.id,
    #                             })

    #         #self.is_changed = True
    #         self.tax_amount_value = total_tax_value
    #         self.final_amount = self.amount - total_tax_value
    #         #self.write({'debitList': debit_lines})

    @api.onchange('vendor_id')
    def _onchange_vendor_id(self):
        if self.vendor_id:
            self.vated_payable = self.vendor_id.vatable_vendor


    @api.onchange('vendor_bill_ext')
    def _onchange_vendor_bill_ext(self):
        if self.vendor_bill_ext:
            self.amount = self.vendor_bill_ext.amount_total_signed
            self.amount_ref = self.vendor_bill_ext.amount_total_signed
            self.vendor_id = self.vendor_bill_ext.partner_id
            self.date_due_no_vendor_bill = self.vendor_bill_ext.date_due


            print(self.vendor_bill_ext.partner_id.vatable_vendor)

            journal = self.env['account.move'].search([('id','=', self.vendor_bill_ext.move_id.id)], limit=1)
            self.env.cr.execute("update account_move set state = 'draft' where id = "+ str(self.vendor_bill_ext.move_id.id))
            
            #journal.write({'state':'draft'})
            
            credit_entry = 0
            for journal_item in journal.line_ids:
                journal_line_item = self.env['account.move.line'].search([('id','=', journal_item.id)], limit=1)
                self.env.cr.execute("update account_move_line set reconciled = FALSE where id = "+str(journal_item.id))
                #journal_line_item.write({'reconciled': False})
                
                if journal_line_item.credit != 0:
                    credit_entry = journal_line_item.account_id.id
  
            self.expense_credit_account = credit_entry

            self.journal_id = self.vendor_bill_ext.move_id
            self.journal_journal = self.vendor_bill_ext.move_id.journal_id


            print(self.journal_journal)

            itemLine = []

            for item in self.vendor_bill_ext.invoice_line_ids:
                description = str(item.quantity)+" "+item.uom_id.name+" - "+item.product_id.name
                amount = item.quantity * item.price_unit
                entry = ''
                if item.price_unit < 0:
                    entry = 'credit'
                else:
                    entry = 'debit'

                itemLine.append({    'description': description,
                                     'entry_type':entry,
                                     'amount': amount,
                                     'account': item.account_id.id,
                                     'ref_description':str(item.product_id.name),
                                     # 'ref_line_id':item.id,
                                })

            self.update({'debitList': itemLine})

    def update_catered_values(self, taxed, untaxed, tax, update_type):
        for payable in self:

                update_taxed_amount_value = 0
                update_untaxed_amount_value = 0
                update_tax_amount_value = 0
                update_balance = 0
                update_balance_tax = 0 
                is_catered = False
                state_value = 'open'

                if update_type == 'add':
                    update_taxed_amount_value = payable.catered_amount + taxed
                    update_untaxed_amount_value = payable.catered_untaxed_amount + untaxed
                    update_tax_amount_value = payable.catered_tax_amount + tax
                    update_balance = payable.final_amount - update_taxed_amount_value
                    update_balance_tax = payable.total_tax_amount_value - update_tax_amount_value

                else:
                    if payable.catered_amount != 0:
                        update_taxed_amount_value = payable.catered_amount - taxed
                        update_untaxed_amount_value = payable.catered_untaxed_amount - untaxed
                        update_tax_amount_value = payable.catered_tax_amount - tax
                        update_balance = payable.final_amount + update_taxed_amount_value
                        update_balance_tax = payable.total_tax_amount_value + update_tax_amount_value


                if update_untaxed_amount_value != 0:
                    is_catered = True
                    state_value = 'tag'


                payable.update({
                                    'catered_amount':update_taxed_amount_value,
                                    'catered_untaxed_amount':update_untaxed_amount_value,
                                    'catered_tax_amount':update_tax_amount_value,
                                    'balance_amount': update_balance,
                                    'balance_tax_amount':update_balance_tax,
                                    'is_catered':is_catered,
                                    'state':state_value,
                                })




    @api.constrains('amount')
    def _amount_check(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError("Invalid expense cost. \n * Please enter the amount of the payable.")


class MGC_ExpenseLine(models.Model):
    _name = 'mgc.expense.base.line'

    expense_id = fields.Many2one('mgc.expense.base', string="Expense Number")
    #account_type = fields.Many2one('mgc.coa_legend.fs_class_chart', string="Account Type", store=False)
    account = fields.Many2one('account.account', string="Account Name", default="0")
    # selected_account_type = fields.Many2one(related="account.fs_class_id", string="Account Type", store=False)
    description = fields.Char(string="Description")
    amount = fields.Float(string="Amount")
    entry_type = fields.Selection(selection=[('debit', 'Debit'), ('credit', 'Credit'), ('neg-debit','Debit')], string="Account Type", default="debit")
    is_shared = fields.Boolean(string="Shared Expense")
    shareList = fields.One2many(comodel_name='mgc.expense.base.shared.bu',inverse_name='expense_line_id',string="Sharing B.U.")
    ref_line_id = fields.Integer(string="Line ID Reference Number")
    ref_description = fields.Char(string="Reference Product")

    @api.onchange('amount')
    def  _onchange_amount(self):
        if self.amount:
            if self.amount <= 0:
                if self.amount < 0:
                    self.entry_type = 'credit'
                    self.amount = abs(self.amount)
                else:
                    raise ValidationError("Zero value on amount is not allowed.") 
    @api.multi
    def write(self, vals):

            result = super(MGC_ExpenseLine, self).write(vals)

            expense_id = self.expense_id

            request_type = expense_id.request_type_id_type
            journal_result_to_remove = []

            if request_type == 'cash':
               journal_gen_id = self.env['account.move'].search([('id','=',expense_id.journal_id.id)])

               amount_ref = expense_id.amount_ref
               itemList = []
               total_tax_credit = 0
               
               journal_result_to_remove = []
               
               journal_lines = self.env['account.move.line'].search([('move_id','=',journal_gen_id.id)])


               if len(journal_lines) != 0:
                   for line in journal_lines:
                        journal_result_to_remove = journal_result_to_remove + [line.id,]


                   for item in expense_id.debitList:
                       credit_value = 0
                       debit_value = 0
                       if item.entry_type == 'debit':
                           debit_value = item.amount
                       else:
                           credit_value = item.amount
                           total_tax_credit = total_tax_credit + credit_value
                           amount_ref = amount_ref - credit_value
                       if item.is_shared:
                           for shareLine in item.shareList:
                               amount_share = item.amount * (shareLine.share * 0.01)
                               account_to_use = 0
                               if shareLine.account.id != False:
                                    account_to_use = shareLine.account.id
                               else:
                                    account_to_use = item.account.id    
                               itemList.append({
                                                'move_id':journal_gen_id.id,
                                                'account_id':account_to_use,
                                                'partner_id':expense_id.vendor_id.id,
                                                'name':item.description+" "+shareLine.buid.bu_code+" share",
                                                'debit': amount_share,
                                                'credit': 0,
                                                'date_maturity':expense_id.date_due_no_vendor_bill,
                                                'reconciled':False,
                                                'company_id':self.env.user.company_id.id,
                                })
                                
                       else:
                           itemList.append({
                                            'move_id':journal_gen_id.id,
                                            'account_id':item.account.id,
                                            'partner_id':expense_id.vendor_id.id,
                                            'name':item.description,
                                            'debit': debit_value,
                                            'credit': credit_value,
                                            'date_maturity':expense_id.date_due_no_vendor_bill,
                                            'reconciled':False,
                                            'company_id':self.env.user.company_id.id,
                            })

                   itemList.append({
                                        'move_id':journal_gen_id.id,
                                        'account_id':expense_id.expense_credit_account.id,
                                        'partner_id':expense_id.vendor_id.id,
                                        'name':"Payable: "+ expense_id.name,
                                        'debit':0,
                                        'credit':expense_id.amount - total_tax_credit,
                                        'date_maturity':expense_id.date_due_no_vendor_bill,
                                        'reconciled':False,
                                        'company_id':self.env.user.company_id.id,
                                    })

                   journal_gen_id.update({'line_ids':itemList})
                   if journal_result_to_remove != []:
                        for id in journal_result_to_remove:
                            print("deleting")
                            self.env.cr.execute("delete from account_move_line where id = " + str(id) + "")

            
            else:

                journal = self.env['account.move'].search([('id','=', expense_id.vendor_bill_ext.move_id.id)], limit=1)
                self.env.cr.execute("update account_move set state = 'draft' where id = "+ str(expense_id.vendor_bill_ext.move_id.id))
                #journal.write({'state':'draft'})
                credit_entry = 0
                for journal_item in journal.line_ids:
                        journal_line_item = self.env['account.move.line'].search([('id','=', journal_item.id)], limit=1)
                        self.env.cr.execute("update account_move_line set reconciled = FALSE where id = "+str(journal_item.id))
                        #journal_line_item.write({'reconciled': False})

                journal_id = self.env['account.move'].search([('id', '=', expense_id.journal_id.id)], limit=1)
                journal_line = journal_id.line_ids
                journal_line_credit = journal_line[0]
                #self.env.cr.execute("update account_move_line set credit = "+str(self.final_amount)+" where credit = "+str(self.amount)+" and move_id = "+str(self.journal_id.id)+"")
                #self.env.cr.execute("delete from account_move_line where move_id = "+str(self.journal_id.id)+"")

                itemList = []
                sum_credit_amount = 0 
                itemList = []

                total_credit = 0
                total_debit = 0

                for item in expense_id.debitList:

                        if item.entry_type == 'credit':
                            total_credit = total_credit + item.amount
                            itemList.append({
                                                    'move_id':expense_id.journal_id.id,
                                                    'account_id':item.account.id,
                                                    'partner_id':expense_id.vendor_id.id,
                                                    'name':item.description,
                                                    'debit': 0,
                                                    'credit': item.amount,
                                                    'date_maturity':expense_id.date_due_no_vendor_bill,
                                                    'reconciled':False,
                                                    'company_id':self.env.user.company_id.id,
                                    })
                        else:

                            journal_lines = self.env['account.move.line'].search([('move_id','=',journal_id.id)])

                            for line in journal_lines:
                                journal_result_to_remove = journal_result_to_remove + [line.id,]
                                #line.unlink()

                            if item.is_shared:
                                total_shared = 0

                                for shareLine in item.shareList:
                                    amount_share = item.amount * (shareLine.share * 0.01)
                                    total_shared = total_shared + amount_share

                                    account_to_use = 0
                                    if shareLine.account.id != False:
                                        account_to_use = shareLine.account.id
                                    else:
                                        account_to_use = item.account.id

                                    # self.env['account.move.line'].create({
                                             #        })
                                    # print("Creation Done").
                                    total_debit = total_debit + amount_share
                                    itemList.append({

                                                    
                                                    'move_id':journal_id.id,
                                                    'account_id':account_to_use,
                                                    'partner_id':expense_id.vendor_id.id,
                                                    'name':item.description+" "+shareLine.buid.bu_code+" share",
                                                    'debit': amount_share,
                                                    'credit': 0,
                                                    'date_maturity':expense_id.date_due_no_vendor_bill,
                                                    'reconciled':False,
                                                    'company_id':self.env.user.company_id.id,       
                                    })
                            else:
                                total_debit = total_debit + item.amount
                                itemList.append({
                                                    'move_id':expense_id.journal_id.id,
                                                    'account_id':item.account.id,
                                                    'partner_id':expense_id.vendor_id.id,
                                                    'name':item.description,
                                                    'debit': item.amount,
                                                    'credit': 0,
                                                    'date_maturity':expense_id.date_due_no_vendor_bill,
                                                    'reconciled':False,
                                                    'company_id':self.env.user.company_id.id,
                                    })
                                     #'|',('credit','=', item.amount),print(total_shared)

                    
                itemList.append({
                                        'move_id':journal_id.id,
                                        'account_id':expense_id.expense_credit_account.id,
                                        'partner_id':expense_id.vendor_id.id,
                                        'name':"/",
                                        'debit': 0,
                                        'credit': expense_id.amount - total_credit,
                                        'date_maturity':expense_id.date_due_no_vendor_bill,
                                        'reconciled':False,
                                        'company_id':self.env.user.company_id.id,
                                                    
                    })


                journal_id.update({'line_ids':itemList})
                # journal_self.unlink()
                if journal_result_to_remove != []:
                    for id in journal_result_to_remove:
                            self.env.cr.execute("delete from account_move_line where id = " + str(id) + "")


            return result



class MGC_ExpenseJournal_Line(models.Model):
		_name = 'mgc.expense.base.journal.line'

		payable_id = fields.Many2one(comodel_name="mgc.expense.base", srting="Payable")
		account_entry = fields.Many2one(comodel_name="account.account", String="Account", store=False)
		currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id, store=False)
		partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", store=False)
		label = fields.Char(string="Label", store=False)
		debit_value = fields.Monetary(string="Debit", store=False)
		credit_value = fields.Monetary(string="Credit", store=False)
		date_due = fields.Date(string="Date Due", store=False)


class MGC_ExpenseBaseSharedBU(models.Model):
        _name = 'mgc.expense.base.shared.bu'

        buid = fields.Many2one('mgc.expense.bu', string="Business Unit")
        name = fields.Char(related="buid.bu_complete_name", string="Business Unit")
        account = fields.Many2one(comodel_name="account.account", string="Account Entry")
        share = fields.Integer(string="Share in Percent (%)")
        expense_line_id = fields.Many2one('mgc.expense.base.line', string="Expense Number")

class MGCExpenseDefaultJournalConfig(models.Model):
    _name = 'mgc.expense.base.cash.type.journal'

    name = fields.Char(string="Journal")
    bind_for = fields.Selection(selection=[('aof','Advance for Operation'),('cash','Cash')], string="Default for")
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal Reference")
    account_entry = fields.Many2one(comodel_name="account.account", string="Credit Account")

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if self.journal_id:
            self.name = self.journal_id.name
            if len(self.journal_id.default_credit_account_id) != 0:
                self.account_entry = self.journal_id.default_credit_account_id.id





	            
