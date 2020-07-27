import xml.etree.ElementTree as ET
import os

# поиск контекста с заданным именем в файле
def find_context(tree_root, name):
    return tree_root.find(".//name/..[name='{0}']".format(name))

#
def get_sources_of_context_messages(context):
    return list(map(lambda x: x.text, context.findall('*/source')))

# дополняем контекст (первый аргумент) сообщениями из другого контекста (второй аргумент)
def complete_context(changing_context, unchanging_context):
    messages_in_context = get_sources_of_context_messages(changing_context)
    # перебираем сообщения второго контекста
    for n, message in enumerate(unchanging_context):
        # если элемент - message и текущего сообщения нет в дополняемом контексте
        if message.tag == 'message' and message.find('source').text not in messages_in_context:
            changing_context.insert(n, message)
        else:
            continue

# дополняем контексты первого дерева отсутсвующими переводами из второго  дерева
def update(main_root, complementary_root):
    missing_contexts = []
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
                # context2.find('name').text
                # проверяем множества сообщений
                # если совпадают, переходим к следующему
                if set(get_sources_of_context_messages(context)) == set(get_sources_of_context_messages(context_main)):
                    continue
                else:
                    # дополняем дерево   отсуствующими переводами
                    complete_context(context_main, context)
                    continue

            # если контекста в файле нет, то добавлям его в файл
            except AttributeError:
                main_root.insert(n, context)

def complement_translations(file1_In, file2_In, file1_Out, file2_Out):
    # читаем файлы
    tree_1 = ET.parse(file1_In)
    root_of_fst_tree = tree_1.getroot()

    tree_2 = ET.parse(file2_In)
    root_of_snd_tree = tree_2.getroot()

    # дополняем файлы переводами и отсутсвующими контекстами
    update(root_of_snd_tree, root_of_fst_tree)
    update(root_of_fst_tree, root_of_snd_tree)

    # добавляем обновленные деревья в новый файл
    fst = open(file1_Out, 'ab')
    tree_1.write(fst, 'utf-8')

    snd = open(file2_Out, 'ab')
    tree_2.write(snd, 'utf-8')



if __name__=='__main__':
    path = 'D:/ucheba/python/grid/translate'
    rex_ru_old_file = os.path.join(path, "ru1.ts")
    rex_ru_new_file = os.path.join(path, "ru_new1.ts")
    rex_en_old_file = os.path.join(path, "en1.ts")
    rex_en_new_file = os.path.join(path, "en_new1.ts")
    complement_translations(rex_ru_old_file, rex_en_old_file, rex_ru_new_file, rex_en_new_file)