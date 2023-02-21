from copy import deepcopy
from tkinter import *
from tkinter.ttk import *
from tkinter.simpledialog import askstring
from tkinter import font as tkfont
from time import perf_counter
import game_tracker_class

class AppWindow(Tk):
    def __init__(self):
        super().__init__()
        #---------------------------------------- App Initialization ------------------------------
        self.title('Wordle Scratchpad by Nate')
        self.state('normal')

        #---------------------------------------- Initialize Frames -------------------------------
        self.title_font = tkfont.Font(family='Helvetica', size=20)
        self.container = Frame(self)
        self.container.pack(side='top', fill='both', expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartFrame, TextInputFrame, WordRecognizeFrame, MainFrame):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            frame.pack(side='top', fill='both', expand=True)

            self.frames[page_name] = frame

        self.current_frame = 'StartFrame'
        self.show_frame('StartFrame')

    def show_frame(self, page_name):
        for frame in self.frames.values():
            frame.pack_forget()
        frame = self.frames[page_name]
        frame.pack(side='top', fill='both', expand=True)
        frame.focus()
        self.current_frame = page_name

        if page_name == 'StartFrame':
            # frame.entry_box.delete(0,END)
            # frame.entry_box.insert(0,'')
            frame.start_entry.focus_set()

    def start_game(self, user_entry):
        if user_entry.isalpha():
            word_length = len(user_entry)
            solution_word = user_entry.upper()
        else:
            word_length = int(user_entry)
            solution_word = False

        game_tracker_class.GameData(word_length=word_length, solution_word=solution_word)

class StartFrame(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        start_label = Label(self, text='Enter a known solution for hints to be automatically generated\n- OR -\nEnter a number to set the word length and enter hints manually from an external game.', font=controller.title_font)
        start_label.pack()
        self.start_entry = Entry(self, font=('calibre', 36, 'normal'), justify='center')
        self.start_entry.pack()

        self.start_entry.bind('<Return>', self.pass_value)

    def pass_value(self, event):
        self.controller.start_game(self.start_entry.get())


class MainFrame(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

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