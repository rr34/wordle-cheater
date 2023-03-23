from copy import deepcopy
from tkinter import *
from tkinter.ttk import *
from tkinter import scrolledtext, END, font as tkfont
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
        self.small_font = tkfont.Font(family='Helvetica', size=12)
        self.container = Frame(self)
        self.container.pack(side='top', fill='both', expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        #---------------------------------------- Controller Variables ----------------------------
        self.guess_prompt = StringVar()
        self.guess_prompt.set('guess_prompt initial value')
        self.CullSolutions_obscurecount = StringVar()
        self.CullSolutions_obscurecount.set(f'<O> Obscure words: {0}')
        self.CullSolutions_unmarkedcount = StringVar()
        self.CullSolutions_unmarkedcount.set(f'<U> Unmarked words: {0}')
        self.CullSolutions_humancount = StringVar()
        self.CullSolutions_humancount.set(f'<H> Human words: {0}')
        self.show_once = 1
        self.cheat1_str = StringVar()
        self.cheat1_str.set('cheat 1 initial value')
        self.cheat2_str = StringVar()
        self.cheat2_str.set('cheat 2 initial value')
        self.cheat3_str = StringVar()
        self.cheat3_str.set('cheat 3 initial value')
        self.cheat4_str = 'Shows possible scenario details with less than 12 remaining words.'

        #---------------------------------------- Generate Frames ---------------------------------
        self.frames = {}

        for F in (StartFrame, GuessHintEntry, CullSolutions, Cheat1, Cheat2, Cheat3, Cheat4):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            frame.pack(side='top', fill='both', expand=True)

            self.frames[page_name] = frame

        self.frames['Cheat4'].update_result()

        self.current_frame = 'StartFrame'
        self.show_frame('StartFrame')

        self.bind_all('<Control-Key-x>', self.save_and_exit)

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

        self.enter_guess(event=None)

    def enter_guess(self, event):
        guess_number = self.current_game.guess_count + 1
        guesses_hints_str = self.current_game.guesses_hints_display()
        prompt_str = guesses_hints_str+ f'Enter guess # {guess_number}'
        self.guess_prompt.set(prompt_str)

        self.show_frame('GuessHintEntry')
        self.frames['GuessHintEntry'].guess_entry.delete(0, END)
        self.frames['GuessHintEntry'].hint_entry.delete(0, END)
        self.frames['GuessHintEntry'].guess_entry.focus_set()

    def hint_entered(self, event):
        hint = self.frames['GuessHintEntry'].hint_entry.get().upper()
        result_str = self.current_game.new_hint(hint)
        print(result_str)
        self.marked_obscure, self.unmarked, self.marked_human = self.current_game.sort_obscure_human()

        if self.show_once > 0:
            self.cull_solutions_init()
            self.show_once -= 1
        else:
            self.generate_show_results()

    def cull_solutions_init(self):

        for word in self.marked_obscure:
            self.frames['CullSolutions'].marked_obscure_listbox.insert(END, word)
        for word in self.unmarked:
            self.frames['CullSolutions'].unmarked_listbox.insert(END, word)
        for word in self.marked_human:
            self.frames['CullSolutions'].marked_human_listbox.insert(END, word)

        unmarkedcount = len(self.frames['CullSolutions'].unmarked_listbox.get(0, END))
        self.CullSolutions_unmarkedcount.set(f'<U> Unmarked words: {unmarkedcount}')

        self.show_frame('CullSolutions')
        self.frames['CullSolutions'].unmarked_listbox.focus_set()

    def cull_receive(self, event):
        obscure_list = set(self.frames['CullSolutions'].marked_obscure_listbox.get(0, END))
        unmarked = set(self.frames['CullSolutions'].unmarked_listbox.get(0, END))
        human_list = set(self.frames['CullSolutions'].marked_human_listbox.get(0, END))
        self.current_game.update_obscure_human(obscure_list, human_list, unmarked)
        self.current_game.remove_obscure()
        self.generate_show_results()
        # self.hint_entered(event=None)

    def generate_show_results(self):
        self.current_game.prepare_cheats()
        self.cheat1_str.set(self.current_game.cheat1_display(top_to_show=25))
        self.cheat2_str.set(self.current_game.cheat2_display(top_to_show=25))
        self.cheat3_str.set(self.current_game.cheat3_display(top_to_show=25))
        if len(self.current_game.remaining_words) <= 12:
            self.cheat4_str = self.current_game.cheat4_display()
            self.frames['Cheat4'].update_result()
        self.show_frame('Cheat1')
        solutions_frames = ('Cheat1', 'Cheat2', 'Cheat3', 'Cheat4')
        for solution_frame in solutions_frames:
            self.frames[solution_frame].bind('<Key-1>', self.show_one)
            self.frames[solution_frame].bind('<Key-2>', self.show_two)
            self.frames[solution_frame].bind('<Key-3>', self.show_three)
            self.frames[solution_frame].bind('<Key-4>', self.show_four)
            self.frames[solution_frame].bind('<g>', self.enter_guess)

    def show_one(self, event):
        self.show_frame('Cheat1')

    def show_two(self, event):
        self.show_frame('Cheat2')

    def show_three(self, event):
        self.show_frame('Cheat3')

    def show_four(self, event):
        self.show_frame('Cheat4')

    def save_and_exit(self, event):
        self.current_game.save_log_file()
        self.destroy()

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

        self.marked_obscure_listbox_label = Label(self, textvariable=self.controller.CullSolutions_obscurecount)
        self.marked_obscure_listbox_label.grid(row=0, column=0)
        self.marked_obscure_listbox = Listbox(self, selectmode='multiple', height=25, font=self.controller.small_font)
        self.marked_obscure_listbox.grid(row=1, column=0)

        self.unmarked_listbox_label = Label(self, textvariable=self.controller.CullSolutions_unmarkedcount)
        self.unmarked_listbox_label.grid(row=0, column=1)
        self.unmarked_listbox = Listbox(self, selectmode='multiple', height=25, font=self.controller.small_font)
        self.unmarked_listbox.grid(row=1, column=1)

        self.marked_human_listbox_label = Label(self, textvariable=self.controller.CullSolutions_humancount)
        self.marked_human_listbox_label.grid(row=0, column=2)
        self.marked_human_listbox = Listbox(self, selectmode='multiple', height=25, font=self.controller.small_font)
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
        self.set_counts()

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
        self.set_counts()

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
        self.set_counts()

    def obscure_the_rest(self, event):
        for word in self.unmarked_listbox.get(0, END):
            self.marked_obscure_listbox.insert(END, word)

        self.unmarked_listbox.delete(0, END)

        self.marked_obscure_listbox.select_clear(0, END)
        self.unmarked_listbox.select_clear(0, END)
        self.set_counts()

    def set_counts(self):
        count = len(self.marked_obscure_listbox.get(0, END))
        self.controller.CullSolutions_obscurecount.set(f'<O> Obscure words: {count}')
        count = len(self.unmarked_listbox.get(0, END))
        self.controller.CullSolutions_unmarkedcount.set(f'<U> Unmarked words: {count}')
        count = len(self.marked_human_listbox.get(0, END))
        self.controller.CullSolutions_humancount.set(f'<H> Human words: {count}')

class Cheat1(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        cheat_label = Label(self, textvariable=self.controller.cheat1_str, font=controller.small_font)
        cheat_label.pack()

class Cheat2(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        cheat_label = Label(self, textvariable=self.controller.cheat2_str, font=controller.small_font)
        cheat_label.pack()

class Cheat3(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        cheat_label = Label(self, textvariable=self.controller.cheat3_str, font=controller.small_font)
        cheat_label.pack()

class Cheat4(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        self.cheat_label = scrolledtext.ScrolledText(self, width=100, height=40, font=controller.small_font)
        self.cheat_label.pack()

    def update_result(self):
        self.cheat_label.delete('0.0',END)
        self.cheat_label.insert('0.0', self.controller.cheat4_str)


#------------------------------------------- Procedural --------------------------------------
if __name__ == '__main__':
    wordle_scratchpad_nate = AppWindow()
    wordle_scratchpad_nate.mainloop()