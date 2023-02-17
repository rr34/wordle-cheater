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

        #---------------------------------------- Initialize --------------------------------------
        self.log_string = ''
        self.section_separator = '\n----------------------------------------------------------------------------------------------------\n'
        start_time = perf_counter()
        self.all_words_list = functions.word_list_parser2()
        elapsed_time = round(perf_counter() - start_time, 6)
        pretty_str = f"Parsed Webster's Unabridged Dictionary plus Collins Scrabble into 5-letter word list in {elapsed_time} seconds.\n"
        self.log_string += pretty_str
        self.alphabet = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
        #---------------------------------------- App Variables -----------------------------------
        self.reset_variables(self)

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
        self.remaining_words = deepcopy(self.all_words_list)
        self.utility_words = deepcopy(self.all_words_list)
        self.guess_count = 0
        self.hint_count = 0
        self.word_length = 5
        self.known_positions = [False for i in range(self.word_length)]

    def get_text_input(self, event):
        self.controller.show_frame('TextInputFrame')

    def new_guess(self, event):
        self.guess_count += 1
        self.guesses.append(self.user_input.get())

        self.display_guesses_hints()

    def new_hint(self, event):
        self.hint_count += 1
        self.hints.append(self.user_input.get())
        self.log_string += self.section_separator
        self.log_string += f'{self.guesses[-1]}: guess #{self.guess_count}\n'
        self.log_string += f'{self.hints[-1]}: hint #{self.hint_count}\n'
        self.display_guesses_hints()
        start_time = perf_counter()
        start_words = len(self.remaining_words)
        self.remaining_words = functions.process_hint(self.guesses[-1], self.hints[-1], self.remaining_words)
        end_words = len(self.remaining_words)
        elapsed_time = round(perf_counter() - start_time, 6)
        pretty_str = f'From {start_words} words to {end_words} words in {elapsed_time} seconds.\n'
        self.log_string += pretty_str
        self.info_string.set(pretty_str)
        
    def display_guesses_hints(self):
        guesses_hints_str = ''
        guesses_count = len(self.guesses)
        hints_count = len(self.hints)
        for i in range(guesses_count):
            if i < guesses_count:
                guesses_hints_str += self.guesses[i] + '\n'
            if i < hints_count:
                guesses_hints_str += self.hints[i] + '\n'
        self.guess_hint_pairs_str.set(guesses_hints_str)

    def new_practice_guess(self, event):
        self.practice_guess_str.set(self.user_input.get())
        new_practice_hint = functions.hint_generator(self.practice_guess_str.get(), self.practice_solution_str.get())
        self.practice_hint_str.set(new_practice_hint)

    def new_practice_solution(self, event):
        self.practice_solution_str.set(self.user_input.get())
        new_practice_hint = functions.hint_generator(self.practice_guess_str.get(), self.practice_solution_str.get())
        self.practice_hint_str.set(new_practice_hint)

    def cheat1(self, event):
        start_time = perf_counter()
        self.letters_freq_list = functions.letter_counter(self.remaining_words, self.alphabet)
        elapsed_time = round(perf_counter() - start_time, 6)
        self.log_string += f'\nCounted word list letters, sorted by frequency in {elapsed_time} seconds.\n'
        pretty_str = ''
        for letter_data in self.letters_freq_list:
            pretty_str += f"'{str(letter_data[0])}' frequency, positional: {str(letter_data[1])}, by letter: {str(letter_data[2])}, by word appearance: {str(letter_data[3])}\n"
        self.log_string += 'Letters ranked by frequency of single appearance in possible solutions list:\n' + pretty_str
        
        start_time = perf_counter()
        words_scored_list = functions.guess_scorer(self.remaining_words, self.letters_freq_list)
        elapsed_time = round(perf_counter() - start_time, 6)
        self.log_string += f"\nPossible solutions ranked by sum of each letter [positional frequency + word appearance frequency] (each unique letter single count, so repeat letters don't add) in {elapsed_time} seconds.\n"
        
        pretty_str = 'Top possible solutions:\n(Word, positional frequencies, score)\n'
        top_to_show = min(len(words_scored_list), 25)
        rank_count = 1
        for word_data in words_scored_list[0:top_to_show]:
            pretty_str += f'{rank_count}. {str(word_data)}\n'
            rank_count += 1
        self.info_string.set(self.info_string.get() + pretty_str)

        pretty_str = '\nPossible solutions:\n'
        rank_count = 1
        for word_data in words_scored_list:
            pretty_str += f'{rank_count}. {str(word_data)}\n'
            rank_count += 1
        self.log_string += pretty_str + '\n'

    def cheat2(self, event):
        start_time = perf_counter()
        words_scored_list, guesses_detail = functions.rank_guesses(self.remaining_words, self.remaining_words)
        elapsed_time = round(perf_counter() - start_time, 6)
        pretty_str = f"\nPossible solutions ranked using performance against remaining solutions in {elapsed_time} seconds.\n"
        pretty_str += 'Top possible-solution guesses by most unique hints generated:\n(Word, possible solution Y/N, worst-case, best-case, mean, median, modes, unique hints generated)\n'
        top_to_show = min(len(words_scored_list), 50)
        rank_count = 1
        for word_data in words_scored_list[0:top_to_show]:
            pretty_str += f'{rank_count}. {str(word_data)}\n'
            rank_count += 1
        self.info_string.set(pretty_str)
        self.log_string += pretty_str

    def cheat3(self, event):
        start_time = perf_counter()
        words_scored_list, guesses_detail = functions.rank_guesses(self.utility_words, self.remaining_words)
        elapsed_time = round(perf_counter() - start_time, 6)
        pretty_str = f"\nGuesses ranked using performance against remaining solutions in {elapsed_time} seconds.\n"
        pretty_str += 'Top guesses by most unique hints generated:\n(Word, possible solution Y/N, worst-case, best-case, mean, median, modes, unique hints generated)\n'
        top_to_show = min(len(words_scored_list), 50)
        rank_count = 1
        for word_data in words_scored_list[0:top_to_show]:
            pretty_str += f'{rank_count}. {str(word_data)}\n'
            rank_count += 1
        self.info_string.set(pretty_str)
        self.log_string += pretty_str

    def cheat4(self, event):
        start_time = perf_counter()
        words_scored_list, guesses_detail = functions.rank_guesses(self.remaining_words, self.remaining_words, return_detail=True)
        elapsed_time = round(perf_counter() - start_time, 6)
        pretty_str = f"\nGuesses detail calculated in {elapsed_time} seconds.\n"
        pretty_str += 'Guesses with remaining-after-hint groups:'
        for word_data in guesses_detail:
            pretty_str += f'\nIf you guess: {word_data[0]}, these are your possible scenarios:\n'
            for i in range(len(word_data[1])):
                pretty_str += f'Hint: {word_data[1][i]}, Remaining:\n{str(word_data[2][i])}\n'
        self.info_string.set(pretty_str)
        self.log_string += pretty_str

    def new_play_these_letters(self, event):
        self.lucas_situation_letters.set(self.user_input.get())
        start_time = perf_counter()
        play_letters_guesses = functions.guess_scorer(self.utility_words, self.letters_freq_list, scoring_type='play letters', letters_to_play=self.lucas_situation_letters.get())
        elapsed_time = round(perf_counter() - start_time, 6)

        self.log_string += f"Guesses with needed letters ranked in {elapsed_time} seconds.\n"
        pretty_str = f"Top 'play-these-letters' for these letters: {self.lucas_situation_letters.get()}:\n"
        top_to_show = min(len(play_letters_guesses), 25)
        rank_count = 1
        for word_data in play_letters_guesses[0:top_to_show]:
            pretty_str += f'{rank_count}. {str(word_data)}\n'
            rank_count += 1
        self.info_string.set(pretty_str)

        pretty_str = f"Top 'play-these-letters' for these letters: {self.lucas_situation_letters.get()}:\n"
        rank_count = 1
        top_to_show = min(len(play_letters_guesses), 25)
        for word_data in play_letters_guesses[0:top_to_show]:
            pretty_str += f'{rank_count}. {str(word_data)}\n'
            rank_count += 1
        self.log_string += pretty_str + '\n'

    def save_log(self, event):
        log_filename = self.practice_solution_str.get().lower() + '.txt'
        with open(log_filename, 'w') as file:
            file.write(self.log_string)

    def exit_with_logfile(self, event):
        self.save_log(self)
        self.controller.destroy()


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