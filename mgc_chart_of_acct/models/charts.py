from odoo import fields, api, models

class BU_Chart_Of_Accounts(models.Model):

	_name= 'mgc.account_chart.bu'

	name = fields.Char(string="Account Code", default="00000000000000")
	loc_id = fields.Many2one('mgc.acct_chart.acct_location', string="Account Location")
	fs_id = fields.Many2one('mgc.acct_chart.acct_finance',string="FS Class")

	loc_name= fields.Char(related="loc_id.name", string="Location Description")
	loc_bu = fields.Char(related="loc_id.bu_id.name",string="Business Unit")
	loc_bu_name = fields.Char(related="loc_id.bu_id.bu_id.name",string="Business Unit")
	loc_area = fields.Char(related="loc_id.loc_id.name", string="Location")
	bd_name = fields.Char(related="loc_id.bd_id.name", string="Branch")
	bt_name = fields.Char(related="loc_id.bt_id.name", string="Business Type")
	cen_name = fields.Char(related="loc_id.cen_id.name",string="Center")

	fs_class_name = fields.Char(related="fs_id.name",string="FS Description")
	fs_class_id_name = fields.Char(related="fs_id.fs_class_id.name", string="FS Class")
	sub_class_id_name = fields.Char(related="fs_id.sub_class_id.name", string="Sub Class")
	spec_id_name = fields.Char(related="fs_id.spec_id.name", string="Specific")

	@api.onchange('loc_id')
	def _onchange_loc_id(self):

		nameString = self.name

		if self.loc_id:
			nameList = list(nameString)
			nameList[0] = str(self.loc_id.acct_loc_id)[0]
			nameList[1] = str(self.loc_id.acct_loc_id)[1]
			nameList[2] = str(self.loc_id.acct_loc_id)[2]
			nameList[3] = str(self.loc_id.acct_loc_id)[3]
			nameList[4] = str(self.loc_id.acct_loc_id)[4]
			nameList[5] = str(self.loc_id.acct_loc_id)[5]
			nameList[6] = str(self.loc_id.acct_loc_id)[6]
			nameString = "".join(nameList)
			self.name = nameString

	@api.onchange('fs_id')
	def _onchange_fs_id(self):

		nameString = self.name

		if self.fs_id:
			nameList = list(nameString)
			nameList[7] = str(self.fs_id.acct_fs_id)[0]
			nameList[8] = str(self.fs_id.acct_fs_id)[1]
			nameList[9] = str(self.fs_id.acct_fs_id)[2]
			nameList[10] = str(self.fs_id.acct_fs_id)[3]
			nameList[11] = str(self.fs_id.acct_fs_id)[4]
			nameList[12] = str(self.fs_id.acct_fs_id)[5]
			nameList[13] = str(self.fs_id.acct_fs_id)[6]
			
			nameString = "".join(nameList)
			self.name = nameString
			#self.department_id = self.employee_id.department_id.id


class AcctChartLocation(models.Model):
	_name='mgc.acct_chart.acct_location'

	acct_loc_id = fields.Char(string="Location Code", default="0000000")
	name = fields.Char(string="Account Location Name")
	bu_id = fields.Many2one('mgc.coa_legend.bu_chart',string="Business Unit")
	loc_id = fields.Many2one('mgc.coa_legend.loc_chart',string="Location") 
	bd_id = fields.Many2one('mgc.coa_legend.bd_chart',string="Branch/Department")
	bt_id = fields.Many2one('mgc.coa_legend.bt_chart',string="Business Type") 
	cen_id = fields.Many2one('mgc.coa_legend.center_chart',string="Center")	
	
	nameDisplay = '*/ - /*/ - /*/ - /*'.split('/')

	@api.onchange('bu_id')
	def _onchange_bu_id(self):

		nameString = self.acct_loc_id

		if self.bu_id:
			nameList = list(nameString)
			nameList[0] = str(self.bu_id.idcode)[0]
			nameList[1] = str(self.bu_id.idcode)[1]
			nameString = "".join(nameList)
			
			self.acct_loc_id = nameString
			
			self.nameDisplay[0] = self.bu_id.name
			nameDisString = "".join(self.nameDisplay)

			self.name = nameDisString

	
	@api.onchange('loc_id')
	def _onchange_loc_id(self):

		nameString = self.acct_loc_id

		if self.loc_id:
			nameList = list(nameString)
			nameList[2] = str(self.loc_id.idcode)[0]
			nameList[3] = str(self.loc_id.idcode)[1]
			nameString = "".join(nameList)
			self.acct_loc_id = nameString

			self.nameDisplay[2] = self.loc_id.name
			nameDisList = self.nameDisplay
			nameDisString = "".join(nameDisList)

			self.name = nameDisString
	
	@api.onchange('bd_id')
	def _onchange_bd_id(self):

		nameString = self.acct_loc_id

		if self.bd_id:
			nameList = list(nameString)
			nameList[4] = str(self.bd_id.idcode)[0]
			nameString = "".join(nameList)
			self.acct_loc_id = nameString
			
			self.nameDisplay[6] = self.bd_id.name
			nameDisList = self.nameDisplay
			nameDisString = "".join(nameDisList)

			self.name = nameDisString

	
	@api.onchange('bt_id')			
	def _onchange_bt_id(self):

		nameString = self.acct_loc_id

		if self.bt_id:
			nameList = list(nameString)
			nameList[5] = str(self.bt_id.idcode)[0]
			nameString = "".join(nameList)
			self.acct_loc_id = nameString
			
			self.nameDisplay[4] = self.bt_id.name
			nameDisList = self.nameDisplay
			nameDisString = "".join(nameDisList)

			self.name = nameDisString
	
	@api.onchange('cen_id')
	def _onchange_cen_id(self):

		nameString = self.acct_loc_id

		if self.cen_id:
			nameList = list(nameString)
			nameList[6] = str(self.cen_id.idcode)[0]
			nameString = "".join(nameList)
			self.acct_loc_id = nameString

	

class AcctChartFinance(models.Model):
	_name='mgc.acct_chart.acct_finance'

	acct_fs_id = fields.Char(string="Finance Code", default="0000000")
	name = fields.Char(string="FS Name")
	fs_class_id = fields.Many2one('mgc.coa_legend.fs_class_chart', string="FS Class")
	sub_class_id = fields.Many2one('mgc.coa_legend.sub_class_chart', string="FS Sub class")
	spec_id = fields.Many2one('mgc.coa_legend.specific', string="Specifics")
	
	nameDisplay = '*/ - /*'.split('/')

	@api.onchange('fs_class_id')
	def _onchange_fs_class_id(self):

		nameString = self.acct_fs_id

		if self.fs_class_id:
			nameList = list(nameString)
			nameList[0] = str(self.fs_class_id.idcode)[0]
			nameList[1] = str(self.fs_class_id.idcode)[1]
			nameString = "".join(nameList)
			self.acct_fs_id = nameString
			#self.department_id = self.employee_id.department_id.id
			
			self.nameDisplay[0] = self.fs_class_id.name
			nameDisList = self.nameDisplay
			nameDisString = "".join(nameDisList)

			self.name = nameDisString			


	
	@api.onchange('sub_class_id')
	def _onchange_sub_class_id(self):

		nameString = self.acct_fs_id

		if self.sub_class_id:
			nameList = list(nameString)
			nameList[2] = str(self.sub_class_id.idcode)[0]
			nameList[3] = str(self.sub_class_id.idcode)[1]
			nameList[4] = str(self.sub_class_id.idcode)[2]
			nameString = "".join(nameList)
			self.acct_fs_id = nameString
			
			self.nameDisplay[2] = self.sub_class_id.name
			nameDisList = self.nameDisplay
			nameDisString = "".join(nameDisList)

			self.name = nameDisString			

	@api.onchange('spec_id')
	def _onchange_spec_id(self):

		nameString = self.acct_fs_id

		if self.spec_id:
			nameList = list(nameString)
			nameList[5] = str(self.spec_id.idcode)[0]
			nameList[6] = str(self.spec_id.idcode)[1]
			nameString = "".join(nameList)
			self.acct_fs_id = nameString
			#self.department_id = self.employee_id.department_id.id



class BU_Chart(models.Model):
	_name = 'mgc.coa_legend.bu_chart'

	idcode = fields.Char(string="BU Code") 
	name = fields.Char(string="Abbreviation")
	bu_id = fields.Many2one('res.company',string="Business Unit")
	#bd_list = fields.One2many('mgc.coa_legend.bd_chart','bu_id', string="Branch/Department")
	#abvName = fields.Char(string="Abbreviation")

	@api.onchange('bu_id')
	def _onchange_bu_id(self):
		if self.bu_id:
			self.name = self.bu_id.partner_id.abbreviation
	
class Loc_Chart(models.Model):
	_name = 'mgc.coa_legend.loc_chart'

	idcode = fields.Char(string="Location Code")
	name = fields.Char(string="Location Name")
	bu_id = fields.Many2one('mgc.coa_legend.bu_chart',string="Business Unit")
	#bu_id_name = fields.Char(related="bu_id.bu_id.name", string="Business Unit")

class BranDept_Chart(models.Model):
	_name = 'mgc.coa_legend.bd_chart'

	idcode = fields.Char(string="Branch/Department Code")
	name = fields.Char(string="Branch/Department Name")
	bu_id = fields.Many2one('mgc.coa_legend.bu_chart',string="Business Unit")


class BusType_Chart(models.Model):
	_name = 'mgc.coa_legend.bt_chart'

	idcode = fields.Char(string="Bus. Type Code")
	name = fields.Char(string="Bus. Type Name")


class Center_Chart(models.Model):
	_name = 'mgc.coa_legend.center_chart'

	idcode = fields.Char(string="Center Code")
	name = fields.Char(string="Center Description")


class FS_Class_Chart(models.Model):
	_name = 'mgc.coa_legend.fs_class_chart'

	idcode = fields.Char(string="FS-class Code")
	name = fields.Char(string="FS-class Name")
	sub_class_list = fields.One2many('mgc.coa_legend.sub_class_chart','fs_id',string="Sub Class List") 

class Sub_Class_Chart(models.Model):
	_name = 'mgc.coa_legend.sub_class_chart'
	
	idcode = fields.Char(string="Sub-class Code")
	name = fields.Char(string="Sub-class Name")
	fs_id = fields.Many2one('mgc.coa_legend.fs_class_chart', srting="FS Class")

class Specifics_Chart(models.Model):
	_name = 'mgc.coa_legend.specific'

	idcode = fields.Char(string="Specific Code")
	name = fields.Char(string="Specific Name")
	sub_class = fields.Many2one('mgc.coa_legend.sub_class_chart', string="FS Sub Class")