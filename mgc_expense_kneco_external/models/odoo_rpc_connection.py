import xmlrpclib
import odoorpc

class OdooRPC_Connection:
    odoo = None
    dbname = ''
    username = ''
    password = ''

    def set_connection(self, server_ip, port_number, dbname, username, password):

        self.dbname = dbname
        self.username = username
        self.password = password    
        self.odoo = odoorpc.ODOO(server_ip, port=port_number)
        self.odoo.login(dbname, username, password)
        print("Connection Set")

    def findID(self, modelname, condition):
        return self.odoo.execute(modelname, 'search', condition)

    def getDataFromSingleID(self, modelname, idreference):
        return self.odoo.execute(modelname, 'read', [idreference])

    def getDataFromMultiLineID(self, modelname, idList):
        outputData = []
        
        for idValue in idList:
            idData = self.odoo.execute(modelname, 'read', [idValue])
            outputData = outputData + idData

        return outputData

    def odoo_class(self):
        return self.odoo
            
