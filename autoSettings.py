from chardet.universaldetector import UniversalDetector
import re
import pandas as pd

class autoSettings(object):
    def __init__(self):
        # возможные разделители строк (байты, потому что разделитель строк находим в строке байтов)
        self.row_separators = [b'\r\n', b'\n\r', b'\r', b'\n']
        # возможные разделители колонок
        self.column_separators = pd.Series([' ', ';', ',', '\t', '.', '\s+'])
        # детектор для определения кодировки
        self.detector = UniversalDetector()
        # разделитель строк
        self.column_sep = ''
        # разделитель колонок
        self.row_sep = ''
        # десятичный разделитель
        self.decimal_sep = ''
        # кодировка файла
        self.code_standart = ''
        # число строк с мусором после заголовка
        self.rubbish_lines_afterHead = 0
        # число строк заголовка
        self.head_lines = 0
        # число строк с мусором до заголовка
        self.rubbish_lines_toHead = 0
        # число значащих строк данных
        self.meaning_data_lines = 0


    # находим первый разделитель в файле
    def __separator(self, byteString):
        for sep in self.row_separators:
            if (sep in byteString) == True:
                return sep
        return None

    # проверяем, остались ли еще разделители в файле после разделения на строки заданным разделителем
    def __separatorChecking(self, separator, byteString):
        splittedS = byteString.split(sep=separator)
        for s in splittedS:
            if self.__separator(splittedS) != None:
                return False
        return True

    # определение разделителя строк
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

    # определяем, является ли заданная строка, строкой с числовыми данными
    def __isStringOfNumbers(self, stringLine, column_separator):
        meaning_data_line = [ch for ch in stringLine.split(column_separator) if ch != '']
        for number in meaning_data_line:
            try:
                float(number)
            except ValueError:
                try:
                    float(number.replace(',', '').replace(':', '').replace(' ', '').replace('.', '').replace('-',
                                                                                                                   ''))
                except ValueError:
                    return False
        return True

    # делим строку на столбцы
    def __splitToColumns(self, string):
        # убираем пустые строки, которые получается если несколько разделителей идут подряд
        columns = [ch for ch in re.split(self.column_sep, string) if ch != '']
        return columns

    # делим строку на столбцы с заданным разделителем
    def __splitToColumns_specSep(self, string, column_separator):
        # убираем пустые строки, которые получается если несколько разделителей идут подряд
        columns = [ch for ch in re.split(column_separator, string) if ch != '']
        return columns

    # определяем число строк с мусором в конце файла
    # функция работает с перевернутым списком строк
    def __rubbish_afterData(self, rows_of_data_reverse):
        # определение количества строк мусора после значащих данных
        rubbishRows_afterMeaningData = -1
        number_of_columns = -1
        for line in rows_of_data_reverse:
            # число столбцов в строке
            count = len(self.__splitToColumns(line))
            print(count)
            if count != 1 and count == number_of_columns and self.__isStringOfNumbers(line, self.column_sep) == True:
                return rubbishRows_afterMeaningData, number_of_columns
            else:
                rubbishRows_afterMeaningData = rubbishRows_afterMeaningData + 1
                number_of_columns = count
        # количество строк мусора после значащих данных
        return rubbishRows_afterMeaningData, number_of_columns

    # определяем есть ли в строке буквы
    def __haveStringLettersOrDigits(self, string):
        for cell in self.__splitToColumns(string):
            if re.search(r'[^\W_]', string) is None:
                return False
            else:
                continue
        return True

    # определяем число строк с мусором после заголовка
    # функция работает с перевернутым списокмо строк
    def __rubbish_afterHead(self, rows_of_data_reverse, number_of_columns):
        rubbishRows_afterHead = 0
        # находим начало строк с значащими данными
        for i, line in enumerate(rows_of_data_reverse):
            # число столбцов в строке
            count = len(self.__splitToColumns(line))
            print(count)
            if count == number_of_columns and self.__isStringOfNumbers(line, self.column_sep) == True:
                continue
            else:
                rows_of_data_reverse = rows_of_data_reverse[i:]
                break
        for line in rows_of_data_reverse:
            # число столбцов в строке
            count = len(self.__splitToColumns(line))
            if count == number_of_columns and self.__haveStringLettersOrDigits(line) == True:
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
            if count == number_of_columns and self.__haveStringLettersOrDigits(line) == True:
                headRows = headRows + 1
            else:
                return headRows
        return headRows

    # # определяем число строк мусора до заголовка
    # def __rubbish_toHead(self, rows_of_data_reverse):
    #     return len(rows_of_data_reverse)

    # определение десятичного разделителя
    def __decimalSeparator(self, numbers):
        for number in numbers:
            try:
                float(number)
                continue
            except ValueError:
                try:
                    float(number.replace(',', '.'))
                except ValueError:
                    continue
                else:
                    return ','
        return '.'

    #определение разделителя колонок
    # начинает поиск с последней строки
    def __searchColumnSeparator(self, rows_of_data):
        for i, line in enumerate(rows_of_data):
            # ищем начало строк со значащими данными (пропускаем строки с мусором)
            #если в строке есть буквы или любые другие символы, кроме указанных в квадратных скобках, переходим к следующей строке
            if re.search(r'[^\d\t- :;.,e]', line) is None:
                continue
            else:
                rows_of_data = rows_of_data[i:]
                break

        columns_sep = ' '
        columns_count = -1
        #начинаем поиск разделителя колонок с последней строки
        column_separators = self.column_separators.copy()
        for line in rows_of_data:
            if columns_count == len(self.__splitToColumns_specSep(line, columns_sep)):
                break
            else:
                l = zip(list(column_separators.keys()), list(map(lambda x: len(self.__splitToColumns_specSep(line, x)), column_separators)))
                for i, count in l:
                    if count == 1 or self.__isStringOfNumbers(line, column_separators[i]) == False:
                        del column_separators[i]
                    else:
                        if (columns_sep == ' ' or columns_sep == '\t') and re.search(r'\s+', line) is not None:
                            columns_sep = r'\s+'
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

            # определение разделителя строк
            self.row_sep = self.__searchRowSeparator(dataRows_begin)
            # делим на строки
            dataRows_begin = self.__splitToRows(dataRows_begin)
            dataRows_end = self.__splitToRows(dataRows_end)

            # опредеялем кодировку файла
            self.code_standart = self.__codeStandart(dataRows_begin+dataRows_end)

            #декодируем данные
            dataRows_begin = [x.decode(self.code_standart) for x in dataRows_begin]
            dataRows_end = [x.decode(self.code_standart) for x in dataRows_end]

            # удаляем лишние пробелы с начала и конца строк
            # удаляем последнюю и первые строки соответственно, так как они могут быть неполными (так как читается N знаков,
            # а не определенное число строк)
            dataRows_begin = (list(map(lambda x: x.strip(), dataRows_begin)))[:-1]
            dataRows_end = (list(map(lambda x: x.strip(), dataRows_end)))[1:]

            # определение разделителя колонок
            # ищем с конца файла!!!!
            dataRows_end_reversed = dataRows_end.copy()
            dataRows_end_reversed.reverse()
            self.column_sep = self.__searchColumnSeparator(dataRows_end_reversed)

            # число строк с мусором после данных
            # так же с конца файла!!!!
            rubbish_lines_afterData, number_of_columns = self.__rubbish_afterData(dataRows_end_reversed)
            print(number_of_columns)
            # число строк с мусором после заголовка
            # работаем с перевернутым файлом!!!!
            dataRows_begin_reversed = dataRows_begin.copy()
            dataRows_begin_reversed.reverse()
            self.rubbish_lines_afterHead, dataRows_begin_reversed = self.__rubbish_afterHead(dataRows_begin_reversed, number_of_columns)

            # число строк заголовка
            # работаем с перевернутым файлом!!!!
            self.head_lines = self.__headRows(dataRows_begin_reversed[self.rubbish_lines_afterHead:], number_of_columns)

            # число строк с мусором до заголовка
            # работаем с перевернутым файлом!!!!
            self.rubbish_lines_toHead = len(dataRows_begin_reversed[self.head_lines + self.rubbish_lines_afterHead:])

            # число строк значащих данных
            self.meaning_data_lines = len(
                self.__splitToRows(s)) - self.rubbish_lines_toHead - self.rubbish_lines_afterHead - rubbish_lines_afterData - self.head_lines

            # десятичный разделитель
            # функция работает со строкой, в которой находятся значащие числовые данные
            decimal_sep = self.__decimalSeparator(self.__splitToColumns(dataRows_end_reversed[rubbish_lines_afterData]))


        return dict(column_separator=self.column_sep, row_separator=self.row_sep.decode(self.code_standart), decimal_separator=decimal_sep,
                    code_standart=self.code_standart, number_of_rows_with_rubbish_toHead=self.rubbish_lines_toHead,
                    number_of_head_lines=self.head_lines,
                    number_of_rows_with_rubbish_afterHead=self.rubbish_lines_afterHead,
                    number_of_rows_with_significant_data=self.meaning_data_lines)



