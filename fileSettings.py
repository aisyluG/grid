from chardet.universaldetector import UniversalDetector
import re
import pandas as pd

class fileSettings(object):
    def __init__(self):
        # возможные разделители строк
        self.row_separators = [b'\r\n', b'\n\r', b'\r', b'\n']
        # возможные разделители колонок
        self.column_separators = pd.Series([b' ', b';', b',', b'\t', b'.'])
        # детектор для определения кодировки
        self.detector = UniversalDetector()
        self.column_sep = b''
        self.row_sep = b''
        self.decimal_sep = b''
        self.code_standart = ''
        self.rubbish_lines_afterHead = 0
        self.head_lines = 0
        self.rubbish_lines_toHead = 0
        self.sgnfnt_data_lines = 0


    def __separator(self, byteString):
        for sep in self.row_separators:
            if (sep in byteString) == True:
                return sep
        return None

    def __separatorChecking(self, separator, byteString):
        splittedS = byteString.split(sep=separator)
        for s in splittedS:
            if self.__separator(splittedS) != None:
                return False
        return True

    def __searchRowSeparator(self, string):
        Sep = self.__separator(string)
        if self.__separatorChecking(Sep, string) == True:
            return Sep
        else:
            if b'\r\n' in string and b'\n\r' in string:
                Sep = b'\n\r'
                if self.__separatorChecking(Sep, string) == True:
                    return Sep
            # есть строка с символами перехода на новую строку (либо \n, либо \r)
            _, Sep = max(list(zip(map(string.count, self.row_separators), self.row_separators)))
            return Sep

    # делим данные на строки
    def __splitToRows(self, string):
        for sep in self.row_separators:
            string = string.replace(sep, b'\n')
        return string.split(sep=b'\n')

    # определеяем кодировку
    def __codeStandart(self, byte_rows):
        # определение кодировки
        for line in byte_rows:
            self.detector.feed(line)
            if self.detector.done == True:
                break
        self.detector.close()
        code = self.detector.result['encoding']
        return code

    # определяем, является ли полученная строка, строкой с числовыми данными
    def __isStringOfNumbers(self, stringLine, column_separator):
        sgnf_data_line = [ch for ch in stringLine.split(column_separator) if ch != b'']
        for number in sgnf_data_line:
            try:
                float(number)
            except ValueError:
                try:
                    float(number.replace(b',', b'').replace(b':', b'').replace(b' ', b'').replace(b'.', b'').replace(b'-',
                                                                                                                   b''))
                except ValueError:
                    return False
        return True

    # делим строку на столбцы
    def __splitToColumns(self, string):
        # убираем пустые строки, которые получается если несколько разделителей идут подряд
        columns = [ch for ch in string.split(self.column_sep) if ch != b'']
        return columns

    # делим строку на столбцы
    def __splitToColumns_specSep(self, string, column_separator):
        # убираем пустые строки, которые получается если несколько разделителей идут подряд
        columns = [ch for ch in string.split(column_separator) if ch != b'']
        return columns

    # определяем число строк с мусором в конце файла
    # функция работает с перевернутым списком строк
    def __rubbish_afterData(self, rows_of_data_reverse):
        # определение количества строк мусора после значащих данных
        rubbishRows_afterSgnfData = -1
        number_of_columns = 0
        for line in rows_of_data_reverse:
            # число столбцов в строке
            count = len(self.__splitToColumns(line))
            if count != 0 and count == number_of_columns and self.__isStringOfNumbers(line, self.column_sep) == True:
                return rubbishRows_afterSgnfData, number_of_columns
            else:
                rubbishRows_afterSgnfData = rubbishRows_afterSgnfData + 1
                number_of_columns = count
        # количество строк мусора после значащих данных
        return rubbishRows_afterSgnfData, number_of_columns

    # определяем есть ли в строке буквы
    def __haveStringLetters(self, string):
        #ищем все буквы, кроме e, так как числа могут быть представлены в экспоненциальной форме
        if re.search(r'[^\W\d_e]', string.decode(self.code_standart)) is None:
            return False
        else:
            return True

    # определяем число строк с мусором после заголовка
    # функция работает с перевернутым списокмо строк
    def __rubbish_afterHead(self, rows_of_data_reverse, number_of_columns):
        rubbishRows_afterHead = 0
        # находим начало строк с значащими данными
        for i, line in enumerate(rows_of_data_reverse):
            # число столбцов в строке
            count = len(self.__splitToColumns(line))
            if count == number_of_columns and self.__isStringOfNumbers(line, self.column_sep) == True:
                continue
            else:
                rows_of_data_reverse = rows_of_data_reverse[i:]
                break
        print(rows_of_data_reverse)
        for line in rows_of_data_reverse:
            # число столбцов в строке
            count = len(self.__splitToColumns(line))
            print(number_of_columns)
            if count == number_of_columns and self.__haveStringLetters(line) == True:
                return rubbishRows_afterHead, rows_of_data_reverse
            else:
                rubbishRows_afterHead = rubbishRows_afterHead + 1
        # количество строк мусора после заголовка
        return rubbishRows_afterHead, rows_of_data_reverse

    # определяем число строк заголовка
    # функция работает с перевернутым списокмо строк
    def __headRows(self, rows_of_data_reverse, number_of_columns):
        # определение количества строк заголовка
        headRows = 0
        for line in rows_of_data_reverse:
            count = len(self.__splitToColumns(line))
            if count == number_of_columns and self.__haveStringLetters(line) == True:
                headRows = headRows + 1
            else:
                return headRows
        return headRows

    # определяем число строк мусора до заголовка
    def __rubbish_toHead(self, rows_of_data_reverse):
        return len(rows_of_data_reverse)

    # определение десятичного разделителя
    def __decimalSeparator(self, numbers):
        for number in numbers:
            try:
                float(number)
            except ValueError:
                try:
                    float(number.replace(b',', b'.'))
                except ValueError:
                    continue
                else:
                    return b','
        return b'.'

    #определение разделителя колонок
    def __searchColumnSeparator(self, rows_of_data):
        for i, line in enumerate(rows_of_data):
            # убираем пробелы в начале и конце строки
            line.strip()
            if self.__haveStringLetters(line)==True or re.search(r'[^\d\t- :;.,e]',line.decode(self.code_standart)) is None:
                continue
            else:
                rows_of_data = rows_of_data[i:]
                break

        columns_sep = b' '
        columns_count = -1
        for line in rows_of_data:
            line.strip()
            if columns_count == len(self.__splitToColumns_specSep(line, columns_sep)):
                break
            else:
                l = zip(list(self.column_separators.keys()), list(map(lambda x: len(self.__splitToColumns_specSep(line, x)), self.column_separators)))
                for i, count in l:
                    if count == 1 or self.__isStringOfNumbers(line,self.column_separators[i]) == False:
                        del self.column_separators[i]
                    else:
                        chars = re.search(r'(\s+)', line.decode(self.code_standart))
                        if columns_sep==b' ' and chars is not None:
                            columns_sep = chars.group().encode(self.code_standart)
                            columns_count = len(self.__splitToColumns_specSep(line, columns_sep))
                        else:
                            columns_sep = self.column_separators[i]
                            columns_count = count
                        break
        return columns_sep

    def get_auto_settings(self, filename):
        # открываем файл в байтовом режиме
        with open(filename, 'rb') as dataBytes:
            s = dataBytes.read()
            dataRows_begin = s[:10000]
            dataRows_end = s[-10000:]

            # находим разделитель строк
            self.row_sep = self.__searchRowSeparator(dataRows_begin)
            # делим на строки
            dataRows_begin = self.__splitToRows(dataRows_begin)
            dataRows_end = self.__splitToRows(dataRows_end)

            # опредеялем кодировку файла
            self.code_standart = self.__codeStandart(dataRows_begin + dataRows_end)

            # удаляем лишние пробелы с начала и конца строк
            dataRows_begin = list(map(lambda x: x.strip(), dataRows_begin))
            dataRows_end = list(map(lambda x: x.strip(), dataRows_end))

            # определение разделителя колонок
            dataRows_end_reversed = dataRows_end.copy()
            dataRows_end_reversed.reverse()
            # dtRowsNotByte = list(map(lambda x: x.decode(code), dataRows_begin))
            # str = '\n'.join(map(lambda x: x.strip(), dtRowsNotByte))
            # dialect = csv.Sniffer().sniff(str)
            # print("'" + dialect.delimiter + "'")
            # полученный разделитель колонок
            self.column_sep = self.__searchColumnSeparator(dataRows_end_reversed)

            # число строк с мусором после данных
            rubbish_lines_afterData, number_of_columns = self.__rubbish_afterData(dataRows_end_reversed)

            # число строк с мусором после заголовка
            dataRows_begin_reversed = dataRows_begin.copy()[:-1]
            #удаляем первую(последнюю) строку, так как она может быть неполной
            dataRows_begin_reversed.reverse()
            self.rubbish_lines_afterHead, dataRows_begin_reversed = self.__rubbish_afterHead(dataRows_begin_reversed, number_of_columns)

            # число строк заголовка
            self.head_lines = self.__headRows(dataRows_begin_reversed[self.rubbish_lines_afterHead:], number_of_columns)

            # число строк с мусором до заголовка
            self.rubbish_lines_toHead = self.__rubbish_toHead(dataRows_begin_reversed[self.head_lines + self.rubbish_lines_afterHead:])

            # число строк значащих данных
            self.sgnfnt_data_lines = len(
                self.__splitToRows(s)) - self.rubbish_lines_toHead - self.rubbish_lines_afterHead - rubbish_lines_afterData - self.head_lines

            # десятичный разделитель
            decimal_sep = self.__decimalSeparator(self.__splitToColumns(dataRows_end_reversed[rubbish_lines_afterData]))


        return dict(column_separator=self.column_sep, row_separator=self.row_sep, decimal_separator=decimal_sep,
                    code_standart=self.code_standart, number_of_rows_with_rubbish_toHead=self.rubbish_lines_toHead,
                    number_of_head_lines=self.head_lines,
                    number_of_rows_with_rubbish_afterHead=self.rubbish_lines_afterHead,
                    number_of_rows_with_significant_data=self.sgnfnt_data_lines)


