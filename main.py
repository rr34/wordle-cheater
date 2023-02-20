from copy import deepcopy
from tkinter import *
from tkinter.ttk import *
from tkinter.simpledialog import askstring
from time import perf_counter
import functions

class AppWindow(Tk):
    def __init__(self):
        super().__init__()
        #---------------------------------------- App Initialization ------------------------------
        self.title('Wordle Scratchpad by Nate')
        self.state('normal')

        #---------------------------------------- Initialize Frames -------------------------------
        self.container = Frame(self)
        self.container.pack(side='top', fill='both', expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (TextInputFrame, WordRecognizeFrame, MainFrame):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            frame.pack(side='top', fill='both', expand=True)

            self.frames[page_name] = frame

        self.current_frame = 'MainFrame'
        self.show_frame('MainFrame')

    def show_frame(self, page_name):
        print(f'Im here right? {page_name}')
        if self.current_frame == 'TextInputFrame':
            user_input = self.frames['TextInputFrame'].entry_box.get().upper()
            self.frames['MainFrame'].user_input.set(user_input)

        for frame in self.frames.values():
            frame.pack_forget()
        frame = self.frames[page_name]
        frame.pack(side='top', fill='both', expand=True)
        frame.focus()
        self.current_frame = page_name

        if page_name == 'TextInputFrame':
            frame.entry_box.delete(0,END)
            frame.entry_box.insert(0,'')
            frame.entry_box.focus_set()


class MainFrame(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        #---------------------------------------- Layout -----------------------------------
        screen_width = 1600
        screen_height = 1200
        cell_width = int(screen_width/10)
        cell_height = int(screen_height/50)
        self.user_input = StringVar()
        self.user_input.set('User input')
        self.user_input_label = Label(self, textvariable=self.user_input)
        self.user_input_label.grid(row=0, column=0)

        self.guess_hint_pairs_str = StringVar()
        self.guess_hint_pairs_str.set('Guess-Hint Pairs')
        self.guess_hint_pairs_label = Label(self, textvariable=self.guess_hint_pairs_str)
        self.guess_hint_pairs_label.grid(row=0, column=1, ipadx=cell_width, ipady=cell_height)

        self.practice_guess_str = StringVar()
        self.practice_guess_str.set('Enter a practice guess with <a> key')
        self.practice_guess_label = Label(self, textvariable=self.practice_guess_str)
        self.practice_guess_label.grid(row=1, column=2, ipadx=cell_width, ipady=cell_height)
        self.practice_solution_str = StringVar()
        self.practice_solution_str.set('Enter a practice solution with <s> key')
        self.practice_solution_label = Label(self, textvariable=self.practice_solution_str)
        self.practice_solution_label.grid(row=0, column=2, ipadx=cell_width, ipady=cell_height)
        self.practice_hint_str = StringVar()
        self.practice_hint_str.set('Will show hint with valid guess and solution.')
        self.practice_hint_label = Label(self, textvariable=self.practice_hint_str)
        self.practice_hint_label.grid(row=2, column=2, ipadx=cell_width, ipady=cell_height)
        self.lucas_situation_letters = StringVar()
        self.lucas_situation_letters.set('Enter letters to play and type <l> to find words.')
        self.lucas_situation_label = Label(self, textvariable=self.lucas_situation_letters)
        self.lucas_situation_label.grid(row=3, column=2, ipadx=cell_width, ipady=cell_height)

        self.user_input_label = Label(self, text='<t> Input text\n<g> Enter guess\n<h> Enter hint\n<a> Enter practice guess\n<s> Enter practice solution word\n<r> Reset all\n<c> Show possible solutions\n<b> Recommend guesses based on unique hints generated\n<v> Show words containing letters entered on the clipboard.\n<Ctrl-x> Close with log file save')
        self.user_input_label.grid(row=4, column=0, columnspan=3)

        self.info_string = StringVar()
        self.info_string.set(pretty_str)
        self.info_label = Label(self, textvariable=self.info_string)
        self.info_label.grid(row=5, column=0, columnspan=3)

        #---------------------------------------- Control Keys ------------------------------------
        self.bind('<t>', self.get_text_input)
        self.bind('<g>', self.new_guess)
        self.bind('<h>', self.new_hint)
        self.bind('<a>', self.new_practice_guess)
        self.bind('<s>', self.new_practice_solution)
        self.bind('<c>', self.cheat1)
        self.bind('<v>', self.cheat2)
        self.bind('<b>', self.cheat3)
        self.bind('<n>', self.cheat4)
        self.bind('<p>', self.new_play_these_letters)
        self.bind('<l>', self.save_log)
        self.bind('<r>', self.reset_variables)
        self.bind('<Control-Key-x>', self.exit_with_logfile)

    #-------------------------------------------- Main Functions -----------------------------------
    def reset_variables(self, event):
        self.guesses = []
        self.hints = []
        self.remaining_words = deepcopy(self.all_words_set)
        self.utility_words = deepcopy(self.all_words_set)
        self.guess_count = 0
        self.hint_count = 0
        self.word_length = 5

    def get_text_input(self, event):
        self.controller.show_frame('TextInputFrame')

class TextInputFrame(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        self.entry_box = Entry(self, font=('calibre', 36, 'normal'))
        self.entry_box.grid(row=0, column=0)

        self.entry_box.bind('<Return>', self.pass_value)

    def pass_value(self, event):
        self.controller.show_frame('MainFrame')

class WordRecognizeFrame(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        self.test_label = Frame(self)
        self.test_label.grid(row=0, column=0, ipadx=100, ipady=10)

#------------------------------------------- Procedural --------------------------------------
if __name__ == '__main__':
    wordle_scratchpad_nate = AppWindow()
    wordle_scratchpad_nate.mainloop()