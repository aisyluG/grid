import openpyxl  as xl
import pandas as pd
file = 'D:/ucheba/python/grid/datasets_excel/42P - миник, хорнер, нолти.xlsx'

class autoSettingsExcel(object):
    def __init__(self):
        self.book = None
        self.sheet_names = []
        self.sheets_count = 0

    def set_filename(self, file):
        self.book = xl.load_workbook(file)
        self.sheet_names = self.book.sheetnames
        self.sheets_count = len(self.sheet_names)

    def __isNumber(self, cell):
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
        print(begin)
        print(end)
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

        print(begin, end)
        if end < 0:
            return None
        return begin, end

    def get_sheet_names(self):
        return self.sheet_names

    def get_auto_settingsForSheet(self, sheet_number_or_name):
        print('**')
        sheet = pd.DataFrame(self.book[sheet_number_or_name].values)
        sheet = self.__del_blank_rows_and_columns(sheet)
        begin_and_end_header = self.__header_rows(sheet)
        if begin_and_end_header == None:
            begin_and_end_meaning_data = self.__meaning_rows(sheet)
        else:
            begin_and_end_meaning_data = self.__meaning_rows(sheet[begin_and_end_header[1] + 1:])
        return dict(header=begin_and_end_header, data=begin_and_end_meaning_data)
