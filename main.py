from copy import deepcopy
from tkinter import Tk, StringVar, Label, Entry, Toplevel
from tkinter.filedialog import askopenfilename
from tkinter.simpledialog import askstring
from time import perf_counter
import functions

class AppWindow(Tk):
    def __init__(self):
        super().__init__()
        #---------------------------------------- App Initialization ------------------------------
        self.title('Wordle Scratchpad by Nate')
        self.state('normal')
        self.log_string = ''
        start_time = perf_counter()
        self.all_words_list = functions.word_list_parser2()
        elapsed_time = round(perf_counter() - start_time, 6)
        pretty_str = f"Parsed Webster's Unabridged Dictionary into 5-letter word list in {elapsed_time} seconds.\n"
        self.log_string += pretty_str
        self.alphabet = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
        #---------------------------------------- App Variables -----------------------------------
        self.reset_variables(self)

        #---------------------------------------- Layout -----------------------------------
        cell_width = 100
        cell_height = 10
        self.user_input = StringVar()
        self.user_input.set('User input')
        self.user_input_label = Label(textvariable=self.user_input)
        self.user_input_label.grid(row=0, column=0, ipadx=cell_width, ipady=cell_height)

        self.guess_hint_pairs_str = StringVar()
        self.guess_hint_pairs_str.set('Guess-Hint Pairs')
        self.guess_hint_pairs_label = Label(textvariable=self.guess_hint_pairs_str)
        self.guess_hint_pairs_label.grid(row=0, column=1, rowspan=10, ipadx=cell_width, ipady=cell_height)

        self.practice_guess_str = StringVar()
        self.practice_guess_str.set('Enter a practice guess with <a> key')
        self.practice_guess_label = Label(textvariable=self.practice_guess_str)
        self.practice_guess_label.grid(row=1, column=2, ipadx=cell_width, ipady=cell_height)
        self.practice_solution_str = StringVar()
        self.practice_solution_str.set('Enter a practice solution with <s> key')
        self.practice_solution_label = Label(textvariable=self.practice_solution_str)
        self.practice_solution_label.grid(row=0, column=2, ipadx=cell_width, ipady=cell_height)
        self.practice_hint_str = StringVar()
        self.practice_hint_str.set('Will show hint with valid guess and solution.')
        self.practice_hint_label = Label(textvariable=self.practice_hint_str)
        self.practice_hint_label.grid(row=2, column=2, ipadx=cell_width, ipady=cell_height)

        self.user_input_label = Label(text='<t> Input text\n<g> Enter guess\n<h> Enter hint\n<a> Enter practice guess\n<s> Enter practice solution word\n<r> Reset all\n<c> Recommend guesses\n<Ctrl-x> Close with log file save')
        self.user_input_label.grid(row=10, column=0, columnspan=3, ipadx=cell_width, ipady=cell_height)

        self.info_string = StringVar()
        self.info_string.set(pretty_str)
        self.info_label = Label(textvariable=self.info_string)
        self.info_label.grid(row=11, column=0, columnspan=3, ipadx=cell_width, ipady=cell_height)

        #---------------------------------------- Control Keys ------------------------------------
        self.bind('<t>', self.get_text_input)
        self.bind('<g>', self.new_guess)
        self.bind('<h>', self.new_hint)
        self.bind('<a>', self.new_practice_guess)
        self.bind('<s>', self.new_practice_solution)
        self.bind('<c>', self.cheat1)
        self.bind('<l>', self.save_log)
        self.bind('<r>', self.reset_variables)
        self.bind('<Control-Key-x>', self.exit_with_logfile)

    #-------------------------------------------- App Functions -----------------------------------
    def reset_variables(self, event):
        self.guesses = []
        self.hints = []
        self.remaining_words = deepcopy(self.all_words_list)
        self.black_letters = []
        self.orange_letters = []
        self.guess_count = 0
        self.hint_count = 0

    def get_text_input(self, event):
        input_now = askstring(title='', prompt='Enter text here').upper()
        self.user_input.set(input_now)

    def new_guess(self, event):
        self.guess_count += 1
        self.guesses.append(self.user_input.get())

        self.display_guesses_hints()

    def new_hint(self, event):
        self.hint_count += 1
        self.hints.append(self.user_input.get())
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
        letters_freq_list = functions.letter_counter(self.remaining_words, self.alphabet)
        elapsed_time = round(perf_counter() - start_time, 6)
        self.log_string += f'Counted word list letters, sorted by frequency in {elapsed_time} seconds.\n'
        pretty_str = ''
        for letter_data in letters_freq_list:
            pretty_str += f"'{str(letter_data[0])}' frequency, positional: {str(letter_data[1])}, by letter: {str(letter_data[2])}, by word appearance: {str(letter_data[3])}\n"
        self.log_string += f'Letters ranked by likelihood of single appearance in word list:\n{pretty_str}\n'
        start_time = perf_counter()
        words_scored_list = functions.word_scorer(self.remaining_words, letters_freq_list)
        elapsed_time = round(perf_counter() - start_time, 6)
        self.log_string += f"Words ranked by sum of each letter [positional frequency + word appearance frequency] (each unique letter single count, so repeat letters don't add) in {elapsed_time} seconds.\n"
        top_to_show = min(len(words_scored_list), 10)
        pretty_str = 'Top words:\n'
        rank_count = 1
        for word_data in words_scored_list[0:top_to_show]:
            pretty_str += f'{rank_count}. {str(word_data)}\n'
            rank_count += 1
        self.info_string.set(pretty_str)
        pretty_str = 'Words ranked:\n'
        rank_count = 1
        for word_data in words_scored_list:
            pretty_str += f'{rank_count}. {str(word_data)}\n'
            rank_count += 1
        self.log_string += pretty_str + '\n'


    def cheat2(self, event):
        guesses_ranked = functions.rank_guesses(self.all_words_list, self.remaining_words)
        guesses_rank_str = ''
        for guess_ranked in guesses_ranked:
            guesses_rank_str += str(guess_ranked) + '\n'
        with open('./guesses_ranked.txt', 'w') as file:
            file.write(guesses_rank_str)
        print('I did it?')

    def save_log(self, event):
        log_filename = self.practice_solution_str.get().lower() + '.txt'
        with open(log_filename, 'w') as file:
            file.write(self.log_string)

    def exit_with_logfile(self, event):
        self.save_log(self)
        self.destroy()

#------------------------------------------- Procedural --------------------------------------
if __name__ == '__main__':
    wordle_scratchpad_nate = AppWindow()
    wordle_scratchpad_nate.mainloop()