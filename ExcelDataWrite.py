from xlwt import Workbook

class ExcelDataWrite:

    def __init__(self):

        self.book = Workbook()
        self.currentsheetname = 'Sheet1'
        self.sheets = {}
        self.columns = {}
        self.currentcolumns = {}
        self.currentrows = {}



    def putData(self,data,**attrs):

        # Set up the sheet if we haven't already

        if 'sheet' in attrs:
            self.currentsheetname = attrs['sheet']

        if not self.currentsheetname in self.sheets:
            newsheet = self.book.add_sheet(self.currentsheetname)
            self.sheets[self.currentsheetname] = newsheet
            self.currentcolumns[self.currentsheetname] = 0
            self.currentrows[self.currentsheetname] = 1
            self.columns[self.currentsheetname] = {}

        for header in data:

            # If we do not yet have a header, put it in

            if not header in self.columns[self.currentsheetname]:
                self.sheets[self.currentsheetname].write(0,self.currentcolumns[self.currentsheetname],header)
                col = self.currentcolumns[self.currentsheetname]
                self.currentcolumns[self.currentsheetname] += 1
                self.columns[self.currentsheetname][header] = col
            else:
                col = self.columns[self.currentsheetname][header]

            # The data

            self.sheets[self.currentsheetname].write(self.currentrows[self.currentsheetname],col,data[header])

        # Increment row

        self.currentrows[self.currentsheetname] += 1
                


    def setSheet(self,sheetname):

        self.currentsheetname = sheetname


    def addColumn(self,columnname,**attrs):

        # Set up the sheet if we haven't already

        if 'sheet' in attrs:
            self.currentsheetname = attrs['sheet']

        if not self.currentsheetname in self.sheets:
            newsheet = self.book.add_sheet(self.currentsheetname)
            self.sheets[self.currentsheetname] = newsheet
            self.currentcolumns[self.currentsheetname] = 0
            self.currentrows[self.currentsheetname] = 1
            self.columns[self.currentsheetname] = {}

        # Add the column 

        if not columnname in self.columns[self.currentsheetname]:
            self.sheets[self.currentsheetname].write(0,self.currentcolumns[self.currentsheetname],columnname)
            col = self.currentcolumns[self.currentsheetname]
            self.currentcolumns[self.currentsheetname] += 1
            self.columns[self.currentsheetname][columnname] = col
        


    def write(self,filename):

        self.book.save(filename)
