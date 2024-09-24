import sqlite3 as sq
import config


def create_virtual_table() -> None:
    with sq.connect(config.DB_ANSWERS_FILE_NAME) as con:
        cur = con.cursor()
        cur.executescript("""
        CREATE VIRTUAL TABLE IF NOT EXISTS index_questions USING FTS5(
        correctResponse,
        questionId,
        questionBlockId,
        questionType,
        question,
        tokenize='trigram')
        """)


def fill_virtual_table() -> None:
    if exist_virtual():
        return

    with sq.connect(config.DB_ANSWERS_FILE_NAME) as con:
        cur = con.cursor()
        cur.execute(f"""
        SELECT correctResponse, questionId, questionBlockId, questionType, question FROM questions
        """)
        rows = cur.fetchall()

        cur.executemany("""
        INSERT INTO index_questions(correctResponse, questionId, questionBlockId, questionType, question) 
        VALUES (?,?,?,?,?)
        """, rows)


# проверю существование заполненной таблицы
def exist_virtual():
    row = None

    with sq.connect(config.DB_ANSWERS_FILE_NAME) as con:
        cur = con.cursor()
        cur.execute(f"""
        SELECT * FROM index_questions
        """)
        row = cur.fetchone()

    return row


def full_text_search(question: str) -> list[tuple]:
    answer_info = []

    with sq.connect(config.DB_ANSWERS_FILE_NAME) as con:
        parameters = (question,)
        cur = con.cursor()
        cur.execute("""
        SELECT correctResponse, questionId, questionBlockId, questionType, question FROM index_questions 
        WHERE index_questions MATCH ?
        """, parameters)
        rows = cur.fetchall()

        if rows:
            answer_info.extend(rows)

    return answer_info


# Простой поиск ответа по идентификатору вопроса и id предмета
def search_answer(identifier: str, question_id: int) -> str:
    with sq.connect(config.DB_ANSWERS_FILE_NAME) as con:
        parameters = (identifier, question_id)
        cur = con.cursor()
        cur.execute("""
        SELECT answer FROM question_answers 
        WHERE identifier=? AND questionId=?
        """, parameters)
        row = cur.fetchone()

        if row:
            text_answer = row[0]
    
    return text_answer


def get_predmet(question_block_id: int) -> tuple[int, int, str]:
    predmet_info = (0, 0, '')
    parent_block_id = question_block_id

    with sq.connect(config.DB_ANSWERS_FILE_NAME) as con:
        cur = con.cursor()

        while parent_block_id:
            parameters = (parent_block_id,)
            cur.execute("""
            SELECT questionBlockId, parentBlockId, title FROM question_blocks
            WHERE questionBlockId=?
            """, parameters)
            row = cur.fetchone()

            if not row:
                return predmet_info

            parent_block_id = row[1]

        predmet_info = row

    return predmet_info


# получает текст ответа по его id (нужно когда требуется напечатать ответ в поле или вывести текстовые варианты ответов на экран)
def get_text_answer(identifier: str, id_question: int = 0) -> str:
    text_answer = ''

    if id_question:
        parameters = (identifier, id_question)
        additional_filter = ' AND questionId=?'
    else:
        parameters = (identifier,)
        additional_filter = ''

    with sq.connect(config.DB_ANSWERS_FILE_NAME) as con:
        cur = con.cursor()
        cur.execute(f"""
        SELECT answer FROM question_answers 
        WHERE identifier=?{additional_filter}
        """, parameters)
        row = cur.fetchone()

        if row:
            text_answer = row[0]

    return text_answer


def get_all_questions_for_block(question_block_id: int) -> list[tuple[str, str, str, int]]:
    questions = []
    parent_block_id = question_block_id

    with sq.connect(config.DB_ANSWERS_FILE_NAME) as con:
        cur = con.cursor()

        # while parent_block_id:
        parameters = (parent_block_id,)
        cur.execute("""
        SELECT question, correctResponse, questionType, questionId FROM questions
        WHERE questionBlockId=?
        """, parameters)
        rows = cur.fetchall()

        if not rows:
            return questions

        # parent_block_id = row[1]

        questions = rows

    return questions
