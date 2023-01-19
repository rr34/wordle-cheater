from tkinter import Tk, StringVar, Label
from tkinter.filedialog import askopenfilename
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
        words_list = functions.word_list_generator1(words_list_filename)
        elapsed_time = perf_counter() - start_time
        self.log_string += f'Parsed words into list in {elapsed_time} seconds.\n'
        letters_list = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
        start_time = perf_counter()
        letters_freq_list = functions.letter_counter(words_list, letters_list)
        elapsed_time = perf_counter() - start_time
        self.log_string += f'Counted word list letters, sorted by frequency in {elapsed_time} seconds.\n'
        start_time = perf_counter()
        words_scored_list = functions.word_scorer(words_list, letters_freq_list)
        elapsed_time = perf_counter() - start_time
        self.log_string += f'Scored words based on high-frequency letters in {elapsed_time} seconds.\n'
        #---------------------------------------- App Variables -----------------------------------
        self.recommend_guess = StringVar(self)
        self.recommend_guess.set(words_scored_list[0][0])
        #---------------------------------------- Layout ------------------------------------------
        self.doing_now_label = Label(self, textvariable=self.recommend_guess)
        self.doing_now_label.pack()
        print(words_scored_list[0][0])

#------------------------------------------- Procedural --------------------------------------
if __name__ == '__main__':
    wordle_cheater_nate = AppWindow()
    wordle_cheater_nate.mainloop()