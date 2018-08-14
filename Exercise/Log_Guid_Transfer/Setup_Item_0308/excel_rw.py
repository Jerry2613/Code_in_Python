import xlrd
import xlwt
from xlutils.copy import copy


class ExcelRw:
    def __init__(self, filename):
        self.wb = ' '
        self.ws = ' '
        self.colum_width = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.filename = filename
        self.create_tample_file()

    def create_tample_file(self):
        field_name = ['First Layer', 'Second Layer', 'Node', 'Node Type', 'Default Value', 'PID Name',
                      'PID Value', 'Token ID Name', 'Token ID Value']
        sheet_name = 'Gset'
        self.wb = xlwt.Workbook()
        self.ws = self.wb.add_sheet(sheet_name)
        for index, cell in enumerate(field_name):
            self.write(0, index, cell)
            self.record_colum_width(index, cell)
        self.save()

    def read(self, sheet_name, row, colum):
        wb = xlrd.open_workbook(self.filename)
        ws = wb.sheet_by_name(sheet_name)
        return ws.cell(row, colum).value

    def open(self, sheet_name):
        rb = xlrd.open_workbook(self.filename)
        self.wb = copy(rb)
        self.ws = self.wb.get_sheet(sheet_name)

    def write(self, row_i, colum_i, value):
        font = xlwt.Font()
        font.name = 'Arial'
        algn1 = xlwt.Alignment()
        algn1.wrap = 1

        style1 = xlwt.XFStyle()
        style1.alignment = algn1
        style1.font = font
        self.ws.write(row_i, colum_i, value, style1)

    def record_colum_width(self, colum_i, value):
        for index in range(len(self.colum_width)):
            if colum_i == index and len(str(value)) > self.colum_width[index]:
                self.colum_width[index] = len(str(value))

    def adjust_colum_width(self):
        for index in range(len(self.colum_width)):
            if index == 5 or index == 7:
                self.ws.col(index).width = 310 * (self.colum_width[index] + 1)  # Uppercase
            else:
                self.ws.col(index).width = 256 * (self.colum_width[index] + 1)  # lowercase

    def save(self):
        self.wb.save(self.filename)

    def write_table_and_save(self, sheet_name, target_table):
        self.open(sheet_name)
        for total_table_index, row_data in enumerate(target_table):
            for row_data_index, data in enumerate(row_data):
                if isinstance(data, list):
                    for i in data:
                        self.record_colum_width(row_data_index, i)
                    data = '\n'.join(data)
                else:
                    self.record_colum_width(row_data_index, data)
                self.write(total_table_index + 1, row_data_index, data)
        self.adjust_colum_width()
        self.save()

