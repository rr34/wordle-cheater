from copy import deepcopy
from tkinter import *
from tkinter.ttk import *
from tkinter import font as tkfont
from time import perf_counter
import models

class AppWindow(Tk):
    def __init__(self):
        super().__init__()
        #---------------------------------------- App Initialization ------------------------------
        self.title('Wordle Scratchpad by Nate')
        self.state('normal')

        #---------------------------------------- Frames Container --------------------------------
        self.prompt_font = tkfont.Font(family='Helvetica', size=20)
        self.container = Frame(self)
        self.container.pack(side='top', fill='both', expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        #---------------------------------------- Controller Variables ----------------------------
        self.guess_prompt = StringVar()
        self.guess_prompt.set('guess_prompt initial value')
        self.cheat1_str = StringVar()
        self.cheat1_str.set('cheat 1 initial value')
        self.cheat2_str = StringVar()
        self.cheat2_str.set('cheat 2 initial value')
        self.cheat3_str = StringVar()
        self.cheat3_str.set('cheat 3 initial value')
        self.cheat4_str = StringVar()
        self.cheat4_str.set('cheat 4 initial value')

        #---------------------------------------- Generate Frames ---------------------------------
        self.frames = {}

        for F in (StartFrame, GuessHintEntry, CullSolutions, Cheat1, Cheat2, Cheat3, Cheat4):
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
            frame.start_entry.focus_set()

    def start_game(self, user_entry):
        if user_entry.isalpha():
            word_length = len(user_entry)
            solution_word = user_entry.upper()
        else:
            word_length = int(user_entry)
            solution_word = False

        self.current_game = models.GameData(word_length=word_length, solution_word=solution_word)

        self.enter_guess()

    def enter_guess(self):
        guess_number = self.current_game.guess_count + 1
        guesses_hints_str = self.current_game.guesses_hints_display()
        prompt_str = guesses_hints_str+ f'Enter guess # {guess_number}'
        self.guess_prompt.set(prompt_str)

        self.show_frame('GuessHintEntry')
        self.frames['GuessHintEntry'].guess_entry.focus_set()

    def hint_entered(self, event):
        hint = self.frames['GuessHintEntry'].hint_entry.get().upper()
        result_str = self.current_game.new_hint(hint)
        print(result_str)
        unmarked = self.current_game.sort_obscure_human()

        if unmarked:
            self.cull_solutions_init(unmarked)
        else:
            self.generate_show_results()

    def cull_solutions_init(self, unmarked):
        for word in unmarked:
            self.frames['CullSolutions'].unmarked_listbox.insert(END, word)
            
        self.show_frame('CullSolutions')
        self.frames['CullSolutions'].unmarked_listbox.focus_set()

    def cull_receive(self, event):
        obscure_list = list(self.frames['CullSolutions'].marked_obscure_listbox.get(0, END))
        unmarked = list(self.frames['CullSolutions'].unmarked_listbox.get(0, END))
        human_list = list(self.frames['CullSolutions'].marked_human_listbox.get(0, END))
        self.current_game.store_user_selections(obscure_list, human_list, unmarked)
        self.hint_entered(event=None)

    def generate_show_results(self):
        self.current_game.prepare_cheats()
        self.cheat1_str = self.current_game.cheat1_display(top_to_show=25)
        self.cheat2_str = self.current_game.cheat2_display(top_to_show=25)
        self.cheat3_str = self.current_game.cheat3_display(top_to_show=25)
        self.cheat4_str = self.current_game.cheat4_display(top_to_show=25)
        self.show_frame('Cheat1')

class StartFrame(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        start_label = Label(self, text='Enter a known solution for hints to be automatically generated\n- OR -\nEnter a number to set the word length and enter hints manually from an external game.', font=controller.prompt_font)
        start_label.pack()
        self.start_entry = Entry(self, font=('calibre', 36, 'normal'), justify='center')
        self.start_entry.pack()

        self.start_entry.bind('<Return>', self.pass_value)

    def pass_value(self, event):
        user_entry = self.start_entry.get().upper()
        self.controller.start_game(user_entry)

class GuessHintEntry(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        prompt_label = Label(self, textvariable=self.controller.guess_prompt, font=self.controller.prompt_font)
        prompt_label.pack()

        self.guess_entry = Entry(self, font=('calibre', 36, 'normal'), justify='center')
        self.guess_entry.pack()
        self.guess_entry.bind('<Return>', self.guess_entered)

        self.hint_entry = Entry(self, font=('calibre', 36, 'normal'), justify='center')
        self.hint_entry.pack()
        self.hint_entry.bind('<Return>', self.controller.hint_entered)

    def guess_entered(self, event):
        guess = self.guess_entry.get().upper()
        hint = self.controller.current_game.new_guess(guess)
        if hint:
            self.hint_entry.insert(0, hint)
            self.controller.hint_entered(event=None)
        else:
            self.hint_entry.focus_set()
    
class CullSolutions(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        self.marked_obscure_listbox_label = Label(self, text='<O> Obscure words:')
        self.marked_obscure_listbox_label.grid(row=0, column=0)
        self.marked_obscure_listbox = Listbox(self, selectmode='multiple', height=50)
        self.marked_obscure_listbox.grid(row=1, column=0)

        self.unmarked_listbox_label = Label(self, text='<U> Unmarked words:')
        self.unmarked_listbox_label.grid(row=0, column=1)
        self.unmarked_listbox = Listbox(self, selectmode='multiple', height=50)
        self.unmarked_listbox.grid(row=1, column=1)

        self.marked_human_listbox_label = Label(self, text='<H> Human words:')
        self.marked_human_listbox_label.grid(row=0, column=2)
        self.marked_human_listbox = Listbox(self, selectmode='multiple', height=50)
        self.marked_human_listbox.grid(row=1, column=2)

        widgets = (self.marked_obscure_listbox, self.unmarked_listbox, self.marked_human_listbox)
        for each_widget in widgets:
            each_widget.bind('<o>', self.mark_obscure)
            each_widget.bind('<h>', self.mark_human)
            each_widget.bind('<u>', self.unmark)
            each_widget.bind('<a>', self.obscure_the_rest)
            each_widget.bind('<Return>', self.controller.cull_receive)

    def mark_obscure(self, event):
        selection = self.unmarked_listbox.curselection()
        for index in selection:
            self.marked_obscure_listbox.insert(END, self.unmarked_listbox.get(index))
        for index in selection[::-1]:
            self.unmarked_listbox.delete(index)

        selection = self.marked_human_listbox.curselection()
        for index in selection:
            self.marked_obscure_listbox.insert(END, self.marked_human_listbox.get(index))
        for index in selection[::-1]:
            self.marked_human_listbox.delete(index)

        self.unmarked_listbox.select_clear(0, END)
        self.marked_human_listbox.select_clear(0, END)

    def unmark(self, event):
        selection = self.marked_obscure_listbox.curselection()
        for index in selection:
            self.unmarked_listbox.insert(END, self.marked_obscure_listbox.get(index))
        for index in selection[::-1]:
            self.marked_obscure_listbox.delete(index)

        selection = self.marked_human_listbox.curselection()
        for index in selection:
            self.unmarked_listbox.insert(END, self.marked_human_listbox.get(index))
        for index in selection[::-1]:
            self.marked_human_listbox.delete(index)

        self.marked_obscure_listbox.select_clear(0, END)
        self.marked_human_listbox.select_clear(0, END)

    def mark_human(self, event):
        selection = self.marked_obscure_listbox.curselection()
        for index in selection:
            self.marked_human_listbox.insert(END, self.marked_obscure_listbox.get(index))
        for index in selection[::-1]:
            self.marked_obscure_listbox.delete(index)

        selection = self.unmarked_listbox.curselection()
        for index in selection:
            self.marked_human_listbox.insert(END, self.unmarked_listbox.get(index))
        for index in selection[::-1]:
            self.unmarked_listbox.delete(index)

        self.marked_obscure_listbox.select_clear(0, END)
        self.unmarked_listbox.select_clear(0, END)

    def obscure_the_rest(self, event):
        for word in self.unmarked_listbox.get(0, END):
            self.marked_obscure_listbox.insert(END, word)

        self.unmarked_listbox.delete(0, END)

        self.marked_obscure_listbox.select_clear(0, END)
        self.unmarked_listbox.select_clear(0, END)

class Cheat1(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        cheat_label = Label(self, textvariable=self.controller.cheat1_str, font=controller.prompt_font)
        cheat_label.pack()

class Cheat2(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        cheat_label = Label(self, textvariable=self.controller.cheat2_str, font=controller.prompt_font)
        cheat_label.pack()

class Cheat3(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        cheat_label = Label(self, textvariable=self.controller.cheat3_str, font=controller.prompt_font)
        cheat_label.pack()

class Cheat4(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        cheat_label = Label(self, textvariable=self.controller.cheat4_str, font=controller.prompt_font)
        cheat_label.pack()


#------------------------------------------- Procedural --------------------------------------
if __name__ == '__main__':
    wordle_scratchpad_nate = AppWindow()
    wordle_scratchpad_nate.mainloop()