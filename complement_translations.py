import xml.etree.ElementTree as ET
import os
import datetime

# поиск контекста с заданным именем в файле
def find_context(tree_root, name):
    return tree_root.find(".//name/..[name='{0}']".format(name))

#
def get_sources_of_context_messages(context):
    return list(map(lambda x: x.text, context.findall('*/source')))

# дополняем контекст (первый аргумент) сообщениями из другого контекста (второй аргумент)
def complete_context(changing_context, unchanging_context):
    # счетчик изменений контекста
    messages_count = 0
    messages_in_context = get_sources_of_context_messages(changing_context)
    # перебираем сообщения второго контекста
    for n, message in enumerate(unchanging_context):
        # если элемент - message и текущего сообщения нет в дополняемом контексте
        if message.tag == 'message' and message.find('source').text not in messages_in_context:
            changing_context.insert(n, message)
            messages_count = messages_count + 1
        else:
            continue
    # возвращаем число сообщений, добавленных  в контекст
    return messages_count

# дополняем контексты первого дерева отсутсвующими переводами из второго  дерева
def update(main_root, complementary_root):
    # файл для выгрузки статистики
    stat_file_path = os.path.realpath(os.path.join(__file__, "..", "statistic.txt"))
    stat = open(stat_file_path, 'a')
    stat.write(str(datetime.datetime.now()) + '\n')
    stat.write(main_root.attrib['language'] + '\n')
    # число измененных конткестов
    changed_context_count = 0
    added_context_count = 0
    #для каждого контекста в файле
    for n, context in enumerate(complementary_root):
        # получаем имя контекста
        try:
            context_name = context.find('name').text
        # есть контексты без имен
        # предупреждаем об этом
        except AttributeError:
            print("The context hasn't name!" )
            continue
        else:
            # находим в дополняемом дереве контекст с таким же именем
            try:
                context_main = find_context(main_root, context_name)
                name = context_main.find('name').text
                # проверяем множества сообщений
                # если совпадают, переходим к следующему
                if set(get_sources_of_context_messages(context)) == set(get_sources_of_context_messages(context_main)):
                    continue
                else:
                    # дополняем дерево   отсуствующими переводами
                    # count - число сообщений, добавленный в контекст
                    count = complete_context(context_main, context)
                    changed_context_count = changed_context_count + 1
                    # пишем в файл число добавленный сообщений
                    stat.write('context: ' + name + ' - добавлено ' + str(count) + ' сообщений' + '\n')
                    continue

            # если контекста в файле нет, то добавлям его в файл
            except AttributeError:
                main_root.insert(n, context)
                added_context_count = added_context_count + 1
                # пишем в файл о добавленном контексте
                stat.write('context: ' + context_name + ' - добавлен в файл' + '\n')
    stat.writelines(['Всего изменено элементов context: {0} \n'.format(changed_context_count),
                    'Всего добавлено элементов context: {0} \n'.format(added_context_count), '\n', '\n'])
    # закрываем файл
    stat.close()

def complement_translations(file1_In, file2_In, file1_Out, file2_Out):
    # считываем первую строку с кодировкой
    f = open(file1_In, 'r', encoding='utf-8')
    line1_1 = f.readline()
    line2_1 = f.readline()
    f.close()
    # для второго файла
    f = open(file2_In, 'r', encoding='utf-8')
    line1_2 = f.readline()
    line2_2 = f.readline()
    f.close()

    # читаем файлы
    tree_1 = ET.parse(file1_In)
    root_of_fst_tree = tree_1.getroot()

    tree_2 = ET.parse(file2_In)
    root_of_snd_tree = tree_2.getroot()

    # дополняем файлы переводами и отсутсвующими контекстами
    update(root_of_snd_tree, root_of_fst_tree)
    update(root_of_fst_tree, root_of_snd_tree)

    # записываем в новый файл строку с кодировкой
    tmp = open(file1_Out, 'w', encoding='utf-8')
    tmp.write(line1_1 + line2_1)
    tmp.close()
    # для второго файла
    tmp = open(file2_Out, 'w', encoding='utf-8')
    tmp.write(line1_2 + line2_2)
    tmp.close()

    # добавляем обновленные деревья в новый файл
    fst = open(file1_Out, 'ab')
    tree_1.write(fst, 'utf-8')
    fst.close()
    # для второго файла
    snd = open(file2_Out, 'ab')
    tree_2.write(snd, 'utf-8')
    snd.close()



if __name__=='__main__':
    # path = 'D:/ucheba/python/grid/translate'
    # rex_ru_old_file = os.path.join(path, "ru1.ts")
    # rex_ru_new_file = os.path.join(path, "ru_new1.ts")
    # rex_en_old_file = os.path.join(path, "en1.ts")
    # rex_en_new_file = os.path.join(path, "en_new1.ts")
    rc_folder = os.path.realpath(os.path.join(__file__, "..", "translate"))
    rex_ru_old_file = os.path.join(rc_folder, "rex_ru.ts")
    rex_ru_new_file = os.path.join(rc_folder, "rex_ru_new.ts")
    rex_en_old_file = os.path.join(rc_folder, "rex_en.ts")
    rex_en_new_file = os.path.join(rc_folder, "rex_en_new.ts")
    complement_translations(rex_ru_old_file, rex_en_old_file, rex_ru_new_file, rex_en_new_file)