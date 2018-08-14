import os
import xlrd
import xlwt
from xlutils.copy import copy


class ExcelRw:
    def __init__(self):
        print("ExcelRw init")

    @classmethod
    def create_tample_file(cls, filename, sheetlist):
        wb = xlwt.Workbook()
        for sheetname in sheetlist:
            wb.add_sheet(sheetname)
        wb.save(filename)

    def createfile_ifneed(cls, filename, sheetname):
        """
        :param filename: Excel file name
        :param sheetname: excel file's sheet name
        :return: None
        """
        if not os.path.isfile(filename):
            wb = xlwt.Workbook()
            wb.add_sheet(sheetname)
            wb.save(filename)
 #           sheetlist =[]
 #           sheetlist.append(sheetname)
 #           for sname in sheetlist:
 #               wb.add_sheet(sname)
 #           wb.save(filename)

    createfile_ifneed = classmethod(createfile_ifneed)

    @classmethod
    def read(cls, filename, sheetname, row, colum):
        cls.createfile_ifneed(filename, sheetname)
        xl = xlrd.open_workbook(filename)
        sheet = xl.sheet_by_name(sheetname)
        return sheet.cell(row, colum).value

    @classmethod
    def write(cls, filename, sheetname, row, colum, value):
        """
        :param filename: Excel file name
        :param sheetname: Excel file's sheet name
        :param row:
        :param colum:
        :param value: Data was written to excell's sheet
        :return:
        """
        cls.createfile_ifneed(filename, sheetname)

        rb = xlrd.open_workbook(filename)
        numberofsheets = rb.nsheets
        # build interface
        wb = copy(rb)

        snamel = [rb.sheet_by_index(sheetnum).name for sheetnum in range(numberofsheets)]
        if sheetname in snamel:
            for sheetnum, name in enumerate(snamel):
                if name == sheetname:
                    ws = wb.get_sheet(sheetnum)
                    ws.write(row, colum, value)
                    wb.save(filename)
                #    print("File {} save".format(filename))

    @classmethod
    def write_table(cls, filename, sheetname, write_table):
        """
        :param filename: Excel file name
        :param sheetname: Excel file's sheet name
        :param write_table: table that were written to excell's sheet
        :return: A xls file with written table
        """
        for c, text in enumerate(write_table):
            for r, value in enumerate(text):
                cls.write(filename, sheetname, r, c, value)
