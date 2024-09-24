import winreg
import re
import model
import config


RE_MATCHING = re.compile(r'(\<(/?[^>]+)>)')
RE_WORDS = re.compile(r'[\w+]{3,}')
RE_LITERALS = re.compile(r'[^\w ]')


def get_access() -> bool:
    result = False

    try:
        with winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, 'Software\SFS') as key:
            value, type_value = winreg.QueryValueEx(key, 'SFS_key')
            result = (value == config.KEY_ACCESS_VALUE)
    except FileNotFoundError:
        if config.DEBUG:
            print('Не найден ключ защиты')

    return result


def create_full_text_search() -> None:
    model.create_virtual_table()
    model.fill_virtual_table()


# заменю некоторые ПЕЧАТНЫЕ мнемоники HTML на их коды, так записано в БД ответов.
def replace_mnemonics_html(text_question: str) -> str:
    mnemonics = {
        '…': '&hellip;',
        '–': '&ndash;',
        '«': '&laquo;',
        '»': '&raquo;',
    }

    for key, value in mnemonics.items():
        text_question = text_question.replace(key, value)

    return text_question


def get_text_without_tags(text: str) -> str:
    return re.sub(RE_MATCHING, '', text)


# оставляет в тексте только буквы, цифры и пробелы
def get_text_only_literals(text: str) -> str:
    return re.sub(RE_LITERALS, '', text)


def get_separation_words(text: str) -> list[str]:
    words = re.findall(RE_WORDS, text)
    words.sort(key=len, reverse=True)

    return words


def full_text_search(search_text: str) -> dict:
    dict_answers = {}
    answers_info = model.full_text_search(search_text)

    for answer_info in answers_info:
        answer_id = answer_info[0]
        question_id = answer_info[1]
        question_block_id = answer_info[2]
        type_question = answer_info[3]
        text_question = get_text_without_tags(answer_info[4])

        _, _, title_predmet = model.get_predmet(question_block_id)

        key = f'Код предмета: {question_block_id}\n{title_predmet}\n{question_id} - {text_question}'

        if type_question == 'textEntry':
            # бывает, что в базе для текстового ввода есть больше одного ID, тексты в них одинаковы, потому берем первый
            if ',' in answer_id and '|' not in answer_id:
                answer_id = answer_id.split(',')[0]
                answer_text = model.get_text_answer(answer_id, question_id)
            else:
                answer_text = model.get_text_answer(answer_id, question_id)

            add_value_to_dict(dict_answers, key, answer_text)
        elif type_question == 'choice':
            answer_text = model.get_text_answer(answer_id, question_id)
            answer_text = get_text_without_tags(answer_text)
            add_value_to_dict(dict_answers, key, answer_text)
        elif type_question == 'choiceMultiple':
            answers_id = answer_id.split(',')

            for answer_id in answers_id:
                answer_text = model.get_text_answer(answer_id, question_id)
                answer_text = get_text_without_tags(answer_text)
                add_value_to_dict(dict_answers, key, answer_text)

        elif type_question == 'match':
            if ',' in answer_id and '|' in answer_id and ';' not in answer_id:
                answer_text = get_match_answer(answer_id, question_id)
                key = f'{title_predmet}\n{question_id} - {text_question}'
                add_value_to_dict(dict_answers, key, answer_text)

        elif type_question == 'matchMultiple':
            if ',' in answer_id and '|' in answer_id and ';' in answer_id:
                answer_text = get_match_multiple_answer(answer_id, question_id)
                add_value_to_dict(dict_answers, key, answer_text)

        elif type_question == 'order':
            answers_id = answer_id.split(',')

            for answer_id in answers_id:
                answer_text = model.get_text_answer(answer_id, question_id)
                answer_text = get_text_without_tags(answer_text)
                add_value_to_dict(dict_answers, key, answer_text)

    return dict_answers


# Простой и точный поиск текста ответа для вывода на экран по параметрам из списка всех вопросов конкретного предмета
def search_answer(text_question: str, answer_id: str, type_question: str, question_id: int, question_block_id: int) -> dict:
    dict_answers = {}

    _, _, title_predmet = model.get_predmet(question_block_id)
    # key = f'Код предмета: {question_block_id}\n{title_predmet}\n{question_id} - {text_question}'
    key = text_question

    if type_question == 'textEntry':
        # бывает, что в базе для текстового ввода есть больше одного ID, тексты в них одинаковы, потому берем первый
        if ',' in answer_id and '|' not in answer_id:
            answer_id = answer_id.split(',')[0]
            answer_text = model.get_text_answer(answer_id, question_id)
        else:
            answer_text = model.get_text_answer(answer_id, question_id)

        add_value_to_dict(dict_answers, key, answer_text)
    elif type_question == 'choice':
        answer_text = model.get_text_answer(answer_id, question_id)
        answer_text = get_text_without_tags(answer_text)
        add_value_to_dict(dict_answers, key, answer_text)
    elif type_question == 'choiceMultiple':
        answers_id = answer_id.split(',')

        for answer_id in answers_id:
            answer_text = model.get_text_answer(answer_id, question_id)
            answer_text = get_text_without_tags(answer_text)
            add_value_to_dict(dict_answers, key, answer_text)

    elif type_question == 'match':
        if ',' in answer_id and '|' in answer_id and ';' not in answer_id:
            answer_text = get_match_answer(answer_id, question_id)
            key = f'{title_predmet}\n{question_id} - {text_question}'
            add_value_to_dict(dict_answers, key, answer_text)

    elif type_question == 'matchMultiple':
        if ',' in answer_id and '|' in answer_id and ';' in answer_id:
            answer_text = get_match_multiple_answer(answer_id, question_id)
            add_value_to_dict(dict_answers, key, answer_text)

    elif type_question == 'order':
        answers_id = answer_id.split(',')

        for answer_id in answers_id:
            answer_text = model.get_text_answer(answer_id, question_id)
            answer_text = get_text_without_tags(answer_text)
            add_value_to_dict(dict_answers, key, answer_text)

    return dict_answers


def add_value_to_dict(variants_answers: dict, key: str, value: str) -> None:
    if key in variants_answers:
        answer = variants_answers[key]
        answer.append(value)
        variants_answers[key] = answer
    else:
        new_value = [value, ]
        variants_answers[key] = new_value


def get_match_answer(answer_id: str, question_id: str) -> str:
    answer_text = ''
    answer_pairs = answer_id.split(',')

    for answer_pair in answer_pairs:
        sides = answer_pair.split('|')
        side1 = sides[0]
        side2 = sides[1]
        answer_side1 = model.get_text_answer(side1, question_id)
        answer_side2 = model.get_text_answer(side2, question_id)
        answer_side1 = get_text_without_tags(answer_side1)
        answer_side2 = get_text_without_tags(answer_side2)
        answer_text += f'{answer_side1} <==> {answer_side2}\n'

    return answer_text


def get_match_multiple_answer(answer_id: str, question_id: str) -> str:
    answer_text = ''
    answer_pairs = answer_id.split(',')

    for answer_pair in answer_pairs:
        sides = answer_pair.split('|')
        side1 = sides[0]
        side2 = sides[1]
        answer_side1 = model.get_text_answer(side1, question_id)
        answer_side1 = get_text_without_tags(answer_side1)
        sub_answer_text = f'{answer_side1} <==> '

        for sub_side in side2:
            answer_sub_side = model.get_text_answer(sub_side, question_id)
            answer_sub_side = get_text_without_tags(answer_sub_side)
            sub_answer_text += f'{answer_sub_side}; '

        answer_text += f'{sub_answer_text}\n'

    return answer_text


def find_all_questions_for_block(question_block_id: int) -> list[tuple[str, str, str, int]]:
    questions_predmet = []
    questions_predmet = model.get_all_questions_for_block(question_block_id)
    sorted_questions_predmet = []

    # Уберу теги из текста вопроса и отсортирую список, так у меня список кортежей,
    # то придется собрать новый словарь из кортежей с измененным первым элементом(текстом вопроса)
    for question_predmet in questions_predmet:
        predmet = (get_text_without_tags(question_predmet[0]),
                   question_predmet[1],
                   question_predmet[2],
                   question_predmet[3])
        sorted_questions_predmet.append(predmet)

    sorted_questions_predmet = sorted(sorted_questions_predmet)

    return sorted_questions_predmet
