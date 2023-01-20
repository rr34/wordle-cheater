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
        self.title('Wordle Cheater by Nate')
        self.log_string = ''
        words_list_filename = askopenfilename(title='Select words list file.')
        start_time = perf_counter()
        self.all_words_list = functions.word_list_generator1(words_list_filename)
        elapsed_time = perf_counter() - start_time
        self.log_string += f'Parsed words into list in {elapsed_time} seconds.\n'
        self.alphabet = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
        start_time = perf_counter()
        letters_freq_list = functions.letter_counter(self.all_words_list, self.alphabet)
        elapsed_time = perf_counter() - start_time
        self.log_string += f'Counted word list letters, sorted by frequency in {elapsed_time} seconds.\n'
        start_time = perf_counter()
        words_scored_list = functions.word_scorer(self.all_words_list, letters_freq_list)
        elapsed_time = perf_counter() - start_time
        self.log_string += f'Scored words based on high-frequency letters in {elapsed_time} seconds.\n'
        #---------------------------------------- App Variables -----------------------------------
        self.guesses = []
        self.hints = []
        self.remaining_words = deepcopy(self.all_words_list)
        self.black_letters = []
        self.orange_letters = []

        #---------------------------------------- Layout -----------------------------------
        self.user_input = StringVar()
        self.user_input.set('User input')
        self.user_input_label = Label(textvariable=self.user_input)
        self.user_input_label.grid(row=0, column=0)

        self.guess_hint_pairs_str = StringVar()
        self.guess_hint_pairs_str.set('Guess-Hint Pairs')
        self.guess_hint_pairs_label = Label(textvariable=self.guess_hint_pairs_str)
        self.guess_hint_pairs_label.grid(row=0, column=1, rowspan=10)

        self.practice_guess_str = StringVar()
        self.practice_guess_str.set('Enter a practice guess with <a> key')
        self.practice_guess_label = Label(textvariable=self.practice_guess_str)
        self.practice_guess_label.grid(row=1, column=2)
        self.practice_solution_str = StringVar()
        self.practice_solution_str.set('Enter a practice solution with <s> key')
        self.practice_solution_label = Label(textvariable=self.practice_solution_str)
        self.practice_solution_label.grid(row=0, column=2)
        self.practice_hint_str = StringVar()
        self.practice_hint_str.set('Will show hint with valid guess and solution.')
        self.practice_hint_label = Label(textvariable=self.practice_hint_str)
        self.practice_hint_label.grid(row=2, column=2)

        self.user_input_label = Label(text='<t> Input text\n<g> Enter guess\n<h> Enter hint\n<a> Enter practice guess\n<s> Enter practice solution word\n<r> Rank guesses')
        self.user_input_label.grid(row=10, column=0, columnspan=3)

        self.info_string = StringVar()
        self.info_string.set(self.log_string)
        self.info_label = Label(textvariable=self.info_string)
        self.info_label.grid(row=11, column=0, columnspan=3)

        #---------------------------------------- Control Keys ------------------------------------
        self.bind('<t>', self.get_text_input)
        self.bind('<g>', self.new_guess)
        self.bind('<h>', self.new_hint)
        self.bind('<a>', self.new_practice_guess)
        self.bind('<s>', self.new_practice_solution)
        self.bind('<r>', self.cheat)

    #-------------------------------------------- App Functions -----------------------------------
    def get_text_input(self, event):
        input_now = askstring(title='', prompt='Enter text here').upper()
        self.user_input.set(input_now)

    def new_guess(self, event):
        self.guesses.append(self.user_input.get())
        self.display_guesses_hints()

    def new_hint(self, event):
        self.hints.append(self.user_input.get())
        self.display_guesses_hints()
        start_time = perf_counter()
        start_words = len(self.remaining_words)
        self.remaining_words = functions.process_hint(self.guesses[-1], self.hints[-1], self.remaining_words)
        end_words = len(self.remaining_words)
        elapsed_time = round(perf_counter() - start_time, 3)
        self.log_string += f'From {start_words} words to {end_words} words in {elapsed_time} seconds.'
        self.info_string.set(self.log_string)

        
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

    def cheat(self, event):
        guesses_ranked = functions.rank_guesses(self.all_words_list, self.remaining_words)
        guesses_rank_str = ''
        for guess_ranked in guesses_ranked:
            guesses_rank_str += str(guess_ranked) + '\n'
        with open('./guesses_ranked.txt', 'w') as file:
            file.write(guesses_rank_str)
        print('I did it?')

        # need hint_to_remaining_words, hint_generator, guess_evaluator, 

#------------------------------------------- Procedural --------------------------------------
if __name__ == '__main__':
    wordle_cheater_nate = AppWindow()
    wordle_cheater_nate.mainloop()