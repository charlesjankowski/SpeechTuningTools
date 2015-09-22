import xlrd
import re
import os

class ExcelData:

    def __init__(self,filename,**args):
        self.data = {}
        self.rdata = {}
        self.headers = {}
        book = xlrd.open_workbook(filename)
        for sheet in book.sheet_names():
            self.data[sheet] = []
            self.rdata[sheet] = {}
            self.headers[sheet] = []

            # If specified, for each sheet, look for a .tsv file first, and take the data from that sheet if we have it, as opposed to the Excel file.

            dotsv = False

            if 'doTSV' in args and args['doTSV']:
                matches = re.search('^(.*)\.xl\w+$',filename)
                prefix = matches.group(1)
                tsvfile = '%s_%s.tsv' % (prefix,sheet)
                if os.path.exists(tsvfile):
                    dotsv = True
                
            if dotsv:
                # Read .tsv file

                rx = 0
                with open(tsvfile, 'U') as f:
                    for line in f:
                        line = re.sub('\n','',line)
                        fields = line.split('\t')

                        if rx == 0:

                            # Get rid of empty '' at the end of the column headers

                            item = fields.pop()
                            while item == '':
                                item = fields.pop()
                            fields.extend([item])

                            ncols = len(fields)

                            self.numcols = ncols
                            for cx in range(ncols):
                                val = fields[cx]

                                if isinstance(val,basestring):
                                    val = val.rstrip().lstrip()
                                self.headers[sheet].append(val)
                        else:
                            element = {}
                            for cx in range(self.numcols):

                                # Make sure we have something for the column even if we don't have the data in the row

                                if cx < len(fields):
                                    val = fields[cx]
                                else:
                                    val = ''

                                element[self.headers[sheet][cx]] = val

                                if cx == 0:
                                    rdatakey = val
                                    self.rdata[sheet][rdatakey] = []
                                else:
                                    self.rdata[sheet][rdatakey].append(val)
                            self.data[sheet].append(element)
                        rx += 1
            else:
                # Read Excel file

                sh = book.sheet_by_name(sheet)
                self.numrows = sh.nrows

                for rx in range(sh.nrows):
                    row = sh.row(rx)
                    ncols = len(row)
            
                    if rx == 0:
                        self.numcols = ncols
                        for cx in range(ncols):
                            val = sh.cell_value(rx,cx)

                            if isinstance(val,basestring):
                                val = val.rstrip().lstrip()
                            self.headers[sheet].append(val)
                    else:
                        element = {}
                        for cx in range(self.numcols):
                            element[self.headers[sheet][cx]] = sh.cell_value(rx,cx)
                            if cx == 0:
                                rdatakey = sh.cell_value(rx,cx)
                                self.rdata[sheet][rdatakey] = []
                            else:
                                self.rdata[sheet][rdatakey].append(sh.cell_value(rx,cx))
                        self.data[sheet].append(element)

    def getData(self,sheet):
        return self.data[sheet]

    def getRowData(self,sheet):
        return self.rdata[sheet]

    def getHeaders(self,sheet):
        return self.headers[sheet]

    def getSheets(self):
        return self.data.keys()
