from copy import deepcopy
from time import perf_counter
from re import finditer, findall
from math import prod
from statistics import mean, median, multimode
import os, configparser, json

class GameData ():
    def __init__(self, word_length, solution_word) -> None:
        self.log_string = ''
        self.alphabet = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
        self.word_length = word_length
        self.solution_word = solution_word
        self.guess_count = 0
        self.section_separator = '\n----------------------------------------------------------------------------------------------------\n'
        start_time = perf_counter()
        self._parse_words()
        elapsed_time = round(perf_counter() - start_time, 6)
        self.log_string += f"Parsed Webster's Unabridged Dictionary plus Collins Scrabble into {self.word_length}-letter word list in {elapsed_time} seconds.\n"
        self.guesses = []
        self.hints = []
        self.remaining_words = deepcopy(self.all_words_set)
        self.utility_words = deepcopy(self.all_words_set)

    def _parse_words(self, include_collins=True):
        text_file_path = './websters-unabridged.txt'
        with open(text_file_path, 'r') as words_file:
            whole_dictionary = words_file.read()
        dictionary_words_list = whole_dictionary.split(sep=None)

        if include_collins:
            text_file_path = './collins-scrabble.txt'
            with open(text_file_path, 'r') as words_file:
                whole_dictionary = words_file.read()
            dictionary_words_list += whole_dictionary.split(sep=None)

        selected_words_list = []
        for text_str in dictionary_words_list:
            if text_str.isalpha() and text_str == text_str.upper() and len(list(text_str)) == self.word_length:
                selected_words_list.append(text_str)
        
        self.all_words_set = set(selected_words_list)

    def new_guess(self, guess):
        self.guesses.append(guess)
        self.guess_count = len(self.guesses)

        if self.solution_word:
            new_hint = self._hint_generator(guess, self.solution_word)
            return new_hint
        else:
            return False

    def new_hint(self, hint):
        self.hints.append(hint)
        self.log_string += self.section_separator
        self.log_string += f'{self.guesses[-1]}: guess #{len(self.guesses)}\n'
        self.log_string += f'{self.hints[-1]}: hint #{len(self.hints)}\n'
        start_time = perf_counter()
        start_words = len(self.remaining_words)
        self.remaining_words = self._process_hint(self.guesses[-1], self.hints[-1], self.remaining_words)
        end_words = len(self.remaining_words)
        elapsed_time = round(perf_counter() - start_time, 6)
        pretty_str = f'From {start_words} words to {end_words} words in {elapsed_time} seconds.\n'
        self.log_string += pretty_str

        return pretty_str

    def sort_obscure_human(self):
        words_config_parser = configparser.ConfigParser()
        section_name = f'{self.word_length}-letter words'

        if not os.path.exists('words_config.ini'):
            marked_obscure = set()
            marked_human = set()
            words_config_parser[section_name] = {'obscure words': json.dumps(list(marked_obscure)), 'human words': json.dumps(list(marked_human))}
            words_config_parser.write(open('words_config.ini', 'w'))
        else:
            words_config_parser.read('words_config.ini')
            try:
                words_config_parser[section_name]
            except:
                marked_obscure = set()
                marked_human = set()
                words_config_parser[section_name] = {'obscure words': json.dumps(list(marked_obscure)), 'human words': json.dumps(list(marked_human))}
            else:
                marked_obscure = set(json.loads(words_config_parser[section_name]['obscure words']))
                marked_human = set(json.loads(words_config_parser[section_name]['human words']))

        self.remaining_words = self.remaining_words - marked_obscure
        unmarked = self.remaining_words - marked_human
            
        if len(unmarked) == 0:
            return False
        else:
            return unmarked

    def guesses_hints_display(self):
        if len(self.hints) < 1:
            return 'No guesses yet.\n'
        elif len(self.hints) >= 1:
            pretty_str = ''
            for i in range(len(self.hints)):
                pretty_str += f'{self.guesses[i]}: guess #{i+1}\n{self.hints[i]}: hint #{i+1}\n'
            return pretty_str

    def _letter_counter(self):
        total_words = len(self.remaining_words)
        total_characters = sum(len(i) for i in self.remaining_words)
        self.letters_freq_list = []
        for letter in self.alphabet:
            positional_totals = list(0 for element in range(self.word_length)) # zeros
            letter_count = 0
            letter_in_word_counter = 0
            for word in self.remaining_words:
                chars_boolean = [(letter == i) for i in list(word)]
                positional_totals = [sum(x) for x in zip(chars_boolean, positional_totals)]
                letter_count += len(findall(letter, word))
                if letter in word:
                    letter_in_word_counter += 1
            positional_totals = [round(i/total_words, 3) for i in positional_totals]
            letter_freq = round(letter_count/total_characters, 3)
            letter_in_word_freq = round(letter_in_word_counter / total_words, 3)
            self.letters_freq_list.append((letter, positional_totals, letter_freq, letter_in_word_freq))

        self.letters_freq_list.sort(key=lambda x: x[-1], reverse=True)

    def _guess_scorer(self, scoring_type=False, letters_to_play=''):
        words_scored_list = []
        just_letters_list = [i[0] for i in self.letters_freq_list]

        for word in self.remaining_words:
            word_pos_scores = []
            index_in_word = 0
            for word_letter in list(word):
                letter_index = just_letters_list.index(word_letter)
                positional_score = self.letters_freq_list[letter_index][1][index_in_word]
                word_pos_scores.append(positional_score)
                index_in_word += 1

            score = 0
            if not scoring_type:
                for letter_tuple in self.letters_freq_list:
                    chars_boolean = [(letter_tuple[0] == x) for x in list(word)]
                    positional_totals = [prod(i) for i in zip(chars_boolean, letter_tuple[1])]
                    positional_score = max([(abs(x-0.5)*-2+1) for x in positional_totals])
                    frequency_in_words = abs(letter_tuple[3]-0.5)*-2+1

                    score += positional_score
                    if any(chars_boolean):
                        score += frequency_in_words

            elif scoring_type == 'play letters':
                for letter in list(letters_to_play):
                    if letter in word:
                        score += 1
                score = score / self.word_length

            words_scored_list.append((word, word_pos_scores, score))

        words_scored_list.sort(key=lambda x: x[-1], reverse=True)

        return words_scored_list

    def _hint_generator(self, guess_word, solution_word):
        guess_word = list(guess_word)
        solution_word = list(solution_word)
        # guess_duplicates = set(guess_word) == guess_word
        if len(guess_word) == self.word_length and len(solution_word) == self.word_length:
            i = 0
            hint = ['B' for element in range(self.word_length)]
            orange_letters = deepcopy(solution_word)
            for i in range(self.word_length):
                if guess_word[i] == solution_word[i]:
                    hint[i] = 'G'
                    orange_letters.remove(guess_word[i])
            for i in range(self.word_length):
                if hint[i] != 'G' and guess_word[i] in orange_letters:
                    hint[i] = 'O'
                    orange_letters.remove(guess_word[i])

            return ''.join(hint)
        else:
            return False

    def _process_hint(self, guess, hint, words_list_in):
        words_list_out = set()

        for test_solution in words_list_in:
            test_hint = self._hint_generator(guess, test_solution)
            if test_hint == hint:
                words_list_out.add(test_solution)

        return words_list_out

    def _rank_guesses(self, guesses_considered, return_detail=False):
        count = 0
        count_end = len(guesses_considered)
        guesses_ranked = []
        guesses_detail = []
        start_time = perf_counter()
        for guess in guesses_considered:
            start_time = perf_counter()
            if guess in self.remaining_words:
                guess_is_possible = True
                guess_is_possible_str = 'Y'
            else:
                guess_is_possible = False
                guess_is_possible_str = 'N'
            remaining_after_lists = []
            hints_list = []
            remaining_count_list = []
            for test_solution in self.remaining_words:
                if guess != test_solution and (not guess_is_possible or not any(guess in x for x in remaining_after_lists)):
                    maybe_hint = self._hint_generator(guess, test_solution)
                    if not maybe_hint in hints_list:
                        maybe_remaining_words_list = self._process_hint(guess, maybe_hint, self.remaining_words)
                        hints_list.append(maybe_hint)
                        remaining_after_lists.append(maybe_remaining_words_list)

            remaining_count_list = [len(x) for x in remaining_after_lists]
            # remaining_count_list = list(filter((1).__ne__, remaining_count_list))
            remaining_worst_case = max(remaining_count_list)
            remaining_best_case = min(remaining_count_list)
            remaining_mean = round(mean(remaining_count_list), 3)
            remaining_median = round(median(remaining_count_list), 3)
            remaining_mode = multimode(remaining_count_list)
            unique_hints = len(hints_list)
            # normalized_score = round(1 - mean(remaining_count_list)/start_count, 3)
            count += 1
            countdown = count_end - count
            guess_eval = (guess, guess_is_possible_str, remaining_worst_case, remaining_best_case, remaining_mean, remaining_median, remaining_mode, unique_hints)
            guesses_ranked.append(guess_eval)
            if return_detail:
                guess_detail = (guess, hints_list, remaining_after_lists)
                guesses_detail.append(guess_detail)
            elapsed_time = round(perf_counter() - start_time, 6)
            print(f"Evaluation time: {elapsed_time}. Guesses remaining to evaluate: {countdown}")
            
        guesses_ranked.sort(key=lambda x: x[-1], reverse=True)

        return guesses_ranked, guesses_detail

    def guesses_hints_display(self):
        guesses_hints_str = ''
        guesses_count = len(self.guesses)
        hints_count = len(self.hints)
        for i in range(guesses_count):
            if i < guesses_count:
                guesses_hints_str += f'{self.guesses[i]}: guess #{i+1}\n'
            if i < hints_count:
                guesses_hints_str += f'{self.hints[i]}: hint #{i+1}\n'

        return guesses_hints_str
    
    def prepare_cheats(self):
        self._cheat1()
        self._cheat2()
        self._cheat3()
        if len(self.remaining_words) <=12:
            self._cheat4()

    def _cheat1(self):
        start_time = perf_counter()
        self._letter_counter()
        elapsed_time = round(perf_counter() - start_time, 6)
        self.log_string += f'\nCounted word list letters, sorted by frequency in {elapsed_time} seconds.\n'
        pretty_str = ''
        for letter_data in self.letters_freq_list:
            pretty_str += f"'{str(letter_data[0])}' frequency, positional: {str(letter_data[1])}, by letter: {str(letter_data[2])}, by word appearance: {str(letter_data[3])}\n"
        self.log_string += 'Letters ranked by frequency of single appearance in possible solutions list:\n'
        self.log_string += pretty_str
        
        start_time = perf_counter()
        self.words_scored_list = self._guess_scorer()
        elapsed_time = round(perf_counter() - start_time, 6)
        self.log_string += f"\nPossible solutions ranked by sum of each unique letter [positional frequency + word appearance frequency] in {elapsed_time} seconds.\n"
        pretty_str = ''
        rank_count = 1
        for word_data in self.words_scored_list:
            pretty_str += f'{rank_count}. {str(word_data)}\n'
            rank_count += 1
        self.log_string += 'Possible solutions:\n(Word, positional frequencies, score)\n'
        self.log_string += pretty_str + '\n'
    
    def cheat1_display(self, top_to_show):
        pretty_str = 'Top possible solutions:\n(Word, positional frequencies, score)\n'
        top_to_show = min(len(self.words_scored_list), top_to_show)
        rank_count = 1
        for word_data in self.words_scored_list[0:top_to_show]:
            pretty_str += f'{rank_count}. {str(word_data)}\n'
            rank_count += 1

        return pretty_str

    def _cheat2(self):
        start_time = perf_counter()
        self.solution_guesses_ranked, guesses_detail = self._rank_guesses(self.remaining_words)
        elapsed_time = round(perf_counter() - start_time, 6)
        self.log_string += f"\nPossible solutions ranked using performance against remaining solutions in {elapsed_time} seconds.\n"
        pretty_str = ''
        rank_count = 1
        for word_data in self.solution_guesses_ranked:
            pretty_str += f'{rank_count}. {str(word_data)}\n'
            rank_count += 1
        self.log_string += 'Possible-solution guesses by most unique hints generated:\n(Word, possible solution Y/N, worst-case, best-case, mean, median, modes, unique hints generated)\n'
        self.log_string += pretty_str

    def cheat2_display(self, top_to_show):
        top_to_show = min(len(self.solution_guesses_ranked), top_to_show)
        pretty_str = 'Top possible-solution guesses by most unique hints generated:\n(Word, possible solution Y/N, worst-case, best-case, mean, median, modes, unique hints generated)\n'
        rank_count = 1
        for word_data in self.solution_guesses_ranked[0:top_to_show]:
            pretty_str += f'{rank_count}. {str(word_data)}\n'
            rank_count += 1

        return pretty_str

    def _cheat3(self):
        start_time = perf_counter()
        self.guesses_unique_hints, guesses_detail = self._rank_guesses(self.utility_words)
        elapsed_time = round(perf_counter() - start_time, 6)
        self.log_string += f"\nGuesses ranked using performance against remaining solutions in {elapsed_time} seconds.\n"
        pretty_str = ''
        top_to_show = min(len(self.guesses_unique_hints), 50)
        rank_count = 1
        for word_data in self.guesses_unique_hints[0:top_to_show]:
            pretty_str += f'{rank_count}. {str(word_data)}\n'
            rank_count += 1
        self.log_string += 'Top guesses by most unique hints generated:\n(Word, possible solution Y/N, worst-case, best-case, mean, median, modes, unique hints generated)\n'
        self.log_string += pretty_str

    def cheat3_display(self, top_to_show):
        top_to_show = min(len(self.guesses_unique_hints), top_to_show)
        pretty_str = 'Top guesses by most unique hints generated:\n(Word, possible solution Y/N, worst-case, best-case, mean, median, modes, unique hints generated)\n'
        rank_count = 1
        for word_data in self.guesses_unique_hints[0:top_to_show]:
            pretty_str += f'{rank_count}. {str(word_data)}\n'
            rank_count += 1

        return pretty_str

    def _cheat4(self):
        start_time = perf_counter()
        words_scored_list, guesses_detail = self._rank_guesses(self.remaining_words, return_detail=True)
        elapsed_time = round(perf_counter() - start_time, 6)
        pretty_str = f"\nDetailed scenarios calculated in {elapsed_time} seconds.\n"
        pretty_str += 'Guesses with remaining-after-hint groups:'
        for word_data in guesses_detail:
            pretty_str += f'\nIf you guess: {word_data[0]}, these are your possible scenarios:\n'
            for i in range(len(word_data[1])):
                pretty_str += f'Hint: {word_data[1][i]}, Remaining:\n{str(word_data[2][i])}\n'
        self.guesses_detail = pretty_str
        self.log_string += pretty_str

    def cheat4_display(self):

        return self.guesses_detail
    
    def new_play_these_letters(self, letters_str, top_to_show):
        start_time = perf_counter()
        play_letters_guesses = self._guess_scorer(self.utility_words, self.letters_freq_list, scoring_type='play letters', letters_to_play=letters_str)
        elapsed_time = round(perf_counter() - start_time, 6)
        self.log_string += f"Guesses with needed letters ranked in {elapsed_time} seconds.\n"

        pretty_str = f"Top 'play-these-letters' for these letters: {letters_str}:\n"
        top_to_show = min(len(play_letters_guesses), top_to_show)
        rank_count = 1
        for word_data in play_letters_guesses[0:top_to_show]:
            pretty_str += f'{rank_count}. {str(word_data)}\n'
            rank_count += 1
        self.log_string += pretty_str

        return pretty_str

    def save_log(self, event):
        log_filename = self.practice_solution_str.get().lower() + '.txt'
        with open(log_filename, 'w') as file:
            file.write(self.log_string)

    def exit_with_logfile(self, event):
        self.save_log(self)
        self.controller.destroy()

    def store_user_selections(self, obscure, human, unmarked):
        words_config_parser = configparser.ConfigParser()
        section_name = f'{self.word_length}-letter words'

        words_config_parser.read('words_config.ini')

        already_obscure = set(json.loads(words_config_parser[section_name]['obscure words']))
        already_human = set(json.loads(words_config_parser[section_name]['human words']))

        all_obscure = already_obscure | obscure
        all_human = already_human | human
        words_config_parser[section_name]['obscure words'] = json.dumps(list(all_obscure))
        words_config_parser[section_name]['human words'] = json.dumps(list(all_human))

        with open('words_config.ini', 'w') as words_config_file:
            words_config_parser.write(words_config_file)