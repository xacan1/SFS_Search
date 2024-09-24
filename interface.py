from tkinter import *
from tkinter import messagebox
import service
import config


# словарь-соответствие между обозначанием типа ответов на странице и в БД questionType
# MATCHING_QUESTION_TYPES = {
#     'Одиночный выбор • с выбором одного правильного ответа из нескольких предложенных вариантов': 'choice',
#     'Множественный выбор • с выбором нескольких правильных ответов из предложенных вариантов': 'choiceMultiple',
#     'Текcтовый ответ': 'textEntry',
#     'Сортировка': 'order',
#     'Сопоставление': 'match',
# }


class MainWindow:
    def __init__(self) -> None:
        self.name_program = 'SFS search'

        # if not service.get_access():
        #     self.__show_not_access()
        #     return

        service.create_full_text_search()

        self.master = Tk()
        self.master.title(self.name_program)
        self.master.geometry('1024x768')
        self.master.iconbitmap('icons8-32.ico')

        # главное меню
        self.main_menu = Frame(self.master, relief=RAISED, bd=2)
        self.main_menu.pack(side=TOP, expand=NO, fill=X)
        self.menu_btn_about = Menubutton(self.main_menu,
                                         text='Menu',
                                         underline=0)
        self.menu_btn_about.pack(side=LEFT)
        self.menu = Menu(self.menu_btn_about, tearoff=0)
        self.menu.add_command(label='About', command=self.__show_about)
        self.menu_btn_about.configure(menu=self.menu)

        # фрейм верхнего уровня
        self.frame_top = Frame(self.master)
        self.frame_top.pack(side=TOP, fill=BOTH, expand=YES)

        # фрейм общего поиска
        self.frame_top_search = Frame(self.frame_top)
        self.frame_top_search.pack(side=TOP, fill=BOTH, expand=NO)

        # self.frame_label_type = LabelFrame(self.frame_top_search,
        #                                    bd=3,
        #                                    text='Тип вопроса:')
        # self.frame_label_type.pack(side=TOP, fill=X, expand=YES)
        # self.type_question = StringVar(self.frame_label_type, value='choice')
        # position = {"padx": 2, "pady": 2, "anchor": NW}

        # self.type_question_choice = Radiobutton(self.frame_label_type, text='Одиночный выбор • с выбором одного правильного ответа из нескольких предложенных вариантов',
        #                                         value='choice',
        #                                         variable=self.type_question)
        # self.type_question_choice.pack(**position)
        # self.type_question_choice_multiple = Radiobutton(self.frame_label_type, text='Множественный выбор • с выбором нескольких правильных ответов из предложенных вариантов',
        #                                                  value='choiceMultiple',
        #                                                  variable=self.type_question)
        # self.type_question_choice_multiple.pack(**position)
        # self.type_question_choice_multiple = Radiobutton(self.frame_label_type, text='Текcтовый ответ',
        #                                                  value='textEntry',
        #                                                  variable=self.type_question)
        # self.type_question_choice_multiple.pack(**position)
        # self.type_question_choice_multiple = Radiobutton(self.frame_label_type, text='Сортировка',
        #                                                  value='order',
        #                                                  variable=self.type_question)
        # self.type_question_choice_multiple.pack(**position)
        # self.type_question_choice_multiple = Radiobutton(self.frame_label_type, text='Сопоставление',
        #                                                  value='match',
        #                                                  variable=self.type_question)
        # self.type_question_choice_multiple.pack(**position)
        # self.type_question_choice_multiple = Radiobutton(self.frame_label_type, text='Множественное сопоставление',
        #                                                  value='matchMultiple',
        #                                                  variable=self.type_question)
        # self.type_question_choice_multiple.pack(**position)

        self.frame_label_entry = LabelFrame(self.frame_top_search,
                                            bd=3,
                                            font=('arial', config.FONT_SIZE),
                                            text='Текст поиска:')
        self.frame_label_entry.pack(side=LEFT, fill=X, expand=YES)

        self.scroll = Scrollbar(self.frame_label_entry)
        self.scroll.pack(side=RIGHT, fill=Y)
        self.search_text = Text(self.frame_label_entry,
                                background='white',
                                height=5,
                                width=30,
                                font=('arial', config.FONT_SIZE),
                                yscrollcommand=(self.scroll, 'set'))
        self.search_text.bind(
            '<Key-F3>', lambda event: self.__full_text_search())
        self.search_text.pack(side=LEFT, fill=BOTH, expand=YES)
        self.scroll.configure(command=self.search_text.yview)

        # контекстное меню текста поиска
        self.context_menu_search = Menu(self.search_text, tearoff=YES)
        self.context_menu_search.add_command(label='Копировать',
                                             command=self.__copy_text_search)
        self.context_menu_search.add_command(label='Вставить',
                                             command=self.__paste_text_search)
        self.context_menu_search.add_command(label='Очистить',
                                             command=self.__clear_text_search)
        self.search_text.bind('<Button-3>',
                              lambda event: self.context_menu_search.post(event.x_root, event.y_root))

        # фрейм кнопки поиска
        self.frame_top_btn = Frame(self.frame_top)
        self.frame_top_btn.pack(side=TOP, fill=BOTH, expand=NO)
        self.search_button = Button(self.frame_top_btn,
                                    bd=2,
                                    text='Найти',
                                    font='arial 16',
                                    command=self.__full_text_search)
        self.search_button.pack(side=TOP, pady=10)

        # фрейм ответов
        self.frame_top_result = Frame(self.frame_top)
        self.frame_top_result.pack(side=TOP, fill=BOTH, expand=YES)
        # self.frame_header_result = Frame(self.frame_top_result)
        # self.frame_header_result.pack(side=TOP, fill=BOTH, expand=YES)
        # self.header_result = Label(self.frame_header_result, text='')
        # self.header_result.pack_forget()
        self.frame_label_result = LabelFrame(self.frame_top_result,
                                             bd=3,
                                             font=('arial', config.FONT_SIZE),
                                             text='Ответы:')
        self.frame_label_result.pack(side=LEFT, fill=BOTH, expand=YES)

        self.scroll2 = Scrollbar(self.frame_label_result)
        self.scroll2.pack(side=RIGHT, fill=Y)
        self.answer_text = Text(self.frame_label_result,
                                background='white',
                                font=('arial', config.FONT_SIZE),
                                yscrollcommand=(self.scroll2, 'set'))
        self.answer_text.pack(side=TOP, fill=BOTH, expand=YES)
        self.scroll2.configure(command=self.answer_text.yview)

        # фрейм кнопки поиска по коду предмета
        self.frame_predmet = LabelFrame(self.frame_top,
                                        bd=3,
                                        font=('arial', config.FONT_SIZE),
                                        text='Поиск по коду предмета:')
        self.frame_predmet.pack(side=TOP, fill=BOTH, expand=NO)
        self.input_predmet = Entry(self.frame_predmet,
                                   bd=3,
                                   width=60,
                                   font=('arial', config.FONT_SIZE))
        self.input_predmet.pack(side=LEFT, pady=10)
        self.predmet_button = Button(self.frame_predmet,
                                     bd=2,
                                     text='Найти по коду предмета',
                                     font='arial 16',
                                     command=self.__search_all_questions_for_predmet)
        self.predmet_button.pack(side=RIGHT, pady=10)

        # контекстное меню ответов
        self.context_menu_answer = Menu(self.answer_text, tearoff=YES)
        self.context_menu_answer.add_command(label='Копировать',
                                             command=self.__copy_text_answer)
        self.answer_text.bind('<Button-3>',
                              lambda event: self.context_menu_answer.post(event.x_root, event.y_root))

        # контекстное меню поля для кода предмета
        self.context_menu_input_predmet = Menu(self.answer_text, tearoff=YES)
        self.context_menu_input_predmet.add_command(label='Вставить',
                                                    command=self.__paste_input_predmet)
        self.input_predmet.bind('<Button-3>',
                                lambda event: self.context_menu_input_predmet.post(event.x_root, event.y_root))

        self.master.mainloop()

    def __show_not_access(self) -> None:
        messagebox.showinfo(self.name_program,
                            'Не обнаружен ключ защиты программы!')

    def __show_about(self) -> None:
        messagebox.showinfo(self.name_program, '"' + self.name_program +
                            '"' + ' powered by Hasan Smirnov(с) 2024')

    def __show_very_short_question(self) -> None:
        messagebox.showinfo(self.name_program,
                            f'Вопрос должен содержать не менее {config.MINIMUM_LENGTH_QUESTION} символов!')

    def __paste_text_search(self) -> None:
        try:
            self.search_text.insert(INSERT, self.search_text.clipboard_get())
        except TclError:
            pass

    def __paste_input_predmet(self) -> None:
        try:
            self.input_predmet.insert(INSERT, self.search_text.clipboard_get())
        except TclError:
            pass

    def __copy_text_search(self) -> None:
        selection = self.search_text.tag_ranges(SEL)

        if selection:
            self.search_text.clipboard_clear()
            self.search_text.clipboard_append(self.answer_text.get(*selection))

    def __copy_text_answer(self) -> None:
        selection = self.answer_text.tag_ranges(SEL)

        if selection:
            self.answer_text.clipboard_clear()
            self.answer_text.clipboard_append(self.answer_text.get(*selection))

    def __clear_text_search(self) -> None:
        self.search_text.delete('1.0', END)

    def __full_text_search(self) -> None:
        # получим текст вопроса, заменим мнемоники HTML в тексте
        search_text = self.search_text.get('1.0', 'end-1c').strip()
        search_text = service.replace_mnemonics_html(search_text)
        search_text = search_text.replace('\n', '')
        search_text = service.get_text_only_literals(search_text)
        self.search_text.delete('1.0', END)
        self.search_text.insert(END, search_text)

        if len(search_text) < config.MINIMUM_LENGTH_QUESTION:
            self.__show_very_short_question()
            return

        self.answer_text.delete('1.0', END)
        variants_answers = service.full_text_search(search_text)
        self.__insert_answers(variants_answers)

    def __search_all_questions_for_predmet(self) -> None:
        question_block_id = self.input_predmet.get().strip()

        if not question_block_id.isdigit():
            return

        question_block_id = int(question_block_id)

        all_questions = service.find_all_questions_for_block(question_block_id)
        self.answer_text.delete(1.0, END)

        for question in all_questions:
            text_question = question[0]
            correct_response = question[1]
            type_question = question[2]
            question_id = question[3]
            variants_answers = service.search_answer(text_question,
                                                     correct_response,
                                                     type_question,
                                                     question_id,
                                                     question_block_id)
            self.__insert_answers(variants_answers)

    # заполним текстовое поле ответов
    def __insert_answers(self, variants_answers: dict) -> None:
        for key, value in variants_answers.items():
            self.answer_text.insert(END, f'ВОПРОС:\n{key}\n\n')
            count = 0

            for answer in value:
                count += 1
                self.answer_text.insert(END, f'{count}. ОТВЕТ:\n{answer}\n')

            self.answer_text.insert(
                END, '\n====================================================================================\n')
