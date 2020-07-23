import openpyxl  as xl
import xlrd
import re
import pandas as pd

class autoSettingsExcel(object):
    def __init__(self):
        self.book = None
        self.sheet_names = []
        self.sheets_count = 0
        self.isXls = False

    def set_filename(self, file):
        if re.search(r'xls$', file) == None:
            self.book = xl.load_workbook(file, read_only=True, data_only=True)
            self.sheet_names = self.book.sheetnames
            self.sheets_count = len(self.sheet_names)
        else:
            self.isXls = True
            self.book = xlrd.open_workbook(file, on_demand=True)
            self.sheet_names = self.book.sheet_names()
            self.sheets_count = len(self.sheet_names)


    def __isNumber(self, cell):
        if  type(cell) != str:
            return True
        try:
            float(cell)
        except ValueError:
            try:
                float(cell.replace(',', '').replace(':', '').replace(' ', '').replace('-', '').replace('.', ''))
            except ValueError:
                return False
        return True

    def __del_blank_rows_and_columns(self, sheet):
        max_count = 0
        for n, column in sheet.items():
            count = column.count()
            if count <= 1:
                sheet = sheet.drop(n, axis=1)
            if max_count < count:
                max_count = count
        rows = []
        for n, row in sheet.iterrows():
            count = row.count()
            if len(rows) == max_count:
                break
            if count != 0:
                rows.append(n)

        sheet = sheet.loc[rows]
        return sheet

    def __header_rows(self, sheet):
        begin = 0
        end = -1
        columns = 0
        for n, row in sheet.iterrows():
            count = row.count()
            if columns < count:
                columns = count
                begin = n

        sheet = sheet[begin:]
        for n, row in sheet.iterrows():
            if True in [self.__isNumber(x) for x in row if x != None]:
                end = n-1
                break
            else:
                continue
        if end < 0:
            return None
        return begin, end

    def __meaning_rows(self, sheet):
        begin = 0
        end = -1
        for n, column in sheet.items():
            count = column.count()
            if count <= 1:
                sheet = sheet.drop(n, axis=1)
            # if max_count < count:
            #     max_count = count
        for n, row in sheet.iterrows():
            if True in [self.__isNumber(x) for x in row if x != None]:
                begin = n
                break
        for n in range(1,sheet.shape[0]):
            if True in [self.__isNumber(x) for x in sheet.iloc[-n] if x != None]:
                end = sheet.iloc[-n].name
                break

        if end < 0:
            return None
        return begin, end

    def __meaning_columns(self, sheet):
        for n, column in sheet.items():
            count = column.count()
            if count <= 1:
                sheet = sheet.drop(n, axis=1)
        return list(sheet.columns)

    def get_sheet_names(self):
        return self.sheet_names

    def __correcting_cells(self, cell):
        if cell.value != '':
            return cell.value
        else:
            return None

    def get_auto_settingsForSheet(self, sheet_number_or_name):
        if self.isXls == True:
            if type(sheet_number_or_name) == int:
                sheet = pd.DataFrame(self.book.sheet_by_index(sheet_number_or_name).get_rows())
            else:
                sheet = pd.DataFrame(self.book.sheet_by_name(sheet_number_or_name).get_rows())
            sheet = sheet.applymap(self.__correcting_cells)
        else:
            sheet = pd.DataFrame(self.book[sheet_number_or_name].values)
        sheet = self.__del_blank_rows_and_columns(sheet)
        begin_and_end_header = self.__header_rows(sheet)
        if begin_and_end_header is None:
            begin_and_end_meaning_data = self.__meaning_rows(sheet)
        else:
            begin_and_end_meaning_data = self.__meaning_rows(sheet[begin_and_end_header[1] + 1:])
        columns = self.__meaning_columns(sheet[begin_and_end_meaning_data[0]:begin_and_end_meaning_data[1]])
        if begin_and_end_meaning_data is None:
            return None
        return dict(header=begin_and_end_header, data=begin_and_end_meaning_data, columns=columns)

    def check_settings(self, filename, sheet_name, setting):
        if setting is None:
            return False
        else:
            begin_data, end_data = setting['data']
            if setting['header'] is None:
                header = None
                nrows = end_data - begin_data + 1
                skiprows = list(range(0, begin_data))
            else:
                begin_head, end_head = setting['header']
                header = list(range(begin_head - end_head + 1))
                nrows = end_data - begin_data + 1 + len(header)
                skiprows = [x for x in list(range(0, begin_data)) if x < begin_head or x > end_head]
            columns = setting['columns']
            try:
                table = pd.read_excel(filename, sheet_name=sheet_name,
                                      header=header,
                                      usecols=columns,
                                      skiprows=skiprows,
                                      nrows=nrows)
            except Exception:
                return False
            return True



