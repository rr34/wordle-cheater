from copy import deepcopy
from time import perf_counter
from re import finditer, findall
from math import prod
from statistics import mean, median, multimode

def word_list_parser1():
    word_length = 5
    text_file_path = './wordle-2309.txt'
    with open(text_file_path, 'r') as words_file:
        words_str = words_file.read()
    words_starts = [i.start() for i in finditer(': ', words_str)]
    words_list = [words_str[i+2:i+2+word_length].strip() for i in words_starts]

    return words_list

def word_list_parser2(include_collins=True):
    word_length = 5
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
        if text_str.isalpha() and text_str == text_str.upper() and len(list(text_str)) == word_length:
            selected_words_list.append(text_str)
    
    selected_words_list = set(selected_words_list)

    return selected_words_list

def word_list_parser3():
    word_length = 5
    text_file_path = './collins-scrabble.txt'
    with open(text_file_path, 'r') as words_file:
        whole_dictionary = words_file.read()
    dictionary_words_list = whole_dictionary.split(sep=None)
    selected_words_list = []
    for text_str in dictionary_words_list:
        if text_str.isalpha() and text_str == text_str.upper() and len(list(text_str)) == word_length:
            selected_words_list.append(text_str)
    
    selected_words_list = set(selected_words_list)

    return selected_words_list

def letter_counter(words_list, letters_list):
    word_length = 5
    total_words = len(words_list)
    total_characters = sum(len(i) for i in words_list)
    letters_freq_list = []
    for letter in letters_list:
        positional_totals = list(0 for element in range(word_length)) # zeros
        letter_counter = 0
        letter_in_word_counter = 0
        for word in words_list:
            chars_boolean = [(letter == i) for i in list(word)]
            positional_totals = [sum(x) for x in zip(chars_boolean, positional_totals)]
            letter_counter += len(findall(letter, word))
            if letter in word:
                letter_in_word_counter += 1
        positional_totals = [round(i/total_words, 3) for i in positional_totals]
        letter_freq = round(letter_counter/total_characters, 3)
        letter_in_word_freq = round(letter_in_word_counter / total_words, 3)
        letters_freq_list.append((letter, positional_totals, letter_freq, letter_in_word_freq))

    letters_freq_list.sort(key=lambda x: x[-1], reverse=True)

    return letters_freq_list

def guess_scorer(words_list, letters_freq, scoring_type=False, letters_to_play=''):
    word_length = 5
    words_scored_list = []
    just_letters_list = [i[0] for i in letters_freq]

    for word in words_list:
        word_pos_scores = []
        index_in_word = 0
        for word_letter in list(word):
            letter_index = just_letters_list.index(word_letter)
            positional_score = letters_freq[letter_index][1][index_in_word]
            word_pos_scores.append(positional_score)
            index_in_word += 1

        score = 0
        for letter_tuple in letters_freq:
            chars_boolean = [(letter_tuple[0] == x) for x in list(word)]
            positional_totals = [prod(i) for i in zip(chars_boolean, letter_tuple[1])]
            positional_score = max([(abs(x-0.5)*-2+1) for x in positional_totals])
            frequency_in_words = abs(letter_tuple[3]-0.5)*-2+1
    
            if not scoring_type:
                score += positional_score
                if any(chars_boolean):
                    score += frequency_in_words
            elif scoring_type == 'utility':
                if letter_tuple[3] != 1.0:
                    score += positional_score
                    score += frequency_in_words
        if scoring_type == 'play letters':
            for letter in list(letters_to_play):
                if letter in word:
                    score += 1
            score = score / word_length

        words_scored_list.append((word, word_pos_scores, score))

    words_scored_list.sort(key=lambda x: x[-1], reverse=True)

    return words_scored_list

def hint_generator(guess_word, solution_word):
    word_length = 5
    guess_word = list(guess_word)
    solution_word = list(solution_word)
    # guess_duplicates = set(guess_word) == guess_word
    if len(guess_word) == word_length and len(solution_word) == word_length:
        i = 0
        hint = ['B' for element in range(word_length)]
        orange_letters = deepcopy(solution_word)
        for i in range(word_length):
            if guess_word[i] == solution_word[i]:
                hint[i] = 'G'
                orange_letters.remove(guess_word[i])
        for i in range(word_length):
            if hint[i] != 'G' and guess_word[i] in orange_letters:
                hint[i] = 'O'
                orange_letters.remove(guess_word[i])

        return ''.join(hint)
    else:
        return False

def process_hint(guess, hint, words_list_in):
    words_list_out = []

    for test_solution in words_list_in:
        test_hint = hint_generator(guess, test_solution)
        if test_hint == hint:
            words_list_out.append(test_solution)

    return words_list_out

def rank_guesses(words_list, test_solutions, return_detail=False):
    count = 0
    guesses_ranked = []
    guesses_detail = []
    start_time = perf_counter()
    for guess in words_list:
        start_time = perf_counter()
        if guess in test_solutions:
            guess_is_possible = True
            guess_is_possible_str = 'Y'
        else:
            guess_is_possible = False
            guess_is_possible_str = 'N'
        remaining_after_lists = []
        hints_list = []
        remaining_count_list = []
        for test_solution in test_solutions:
            if guess != test_solution and (not guess_is_possible or not any(guess in x for x in remaining_after_lists)):
                maybe_hint = hint_generator(guess, test_solution)
                if not maybe_hint in hints_list:
                    maybe_remaining_words_list = process_hint(guess, maybe_hint, test_solutions)
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
        countdown = len(words_list) - count
        guess_eval = (guess, guess_is_possible_str, remaining_worst_case, remaining_best_case, remaining_mean, remaining_median, remaining_mode, unique_hints)
        guesses_ranked.append(guess_eval)
        if return_detail:
            guess_detail = (guess, hints_list, remaining_after_lists)
            guesses_detail.append(guess_detail)
        elapsed_time = round(perf_counter() - start_time, 6)
        print(f"Evaluation time: {elapsed_time}. Guesses remaining to evaluate: {countdown}")
        
    guesses_ranked.sort(key=lambda x: x[-1], reverse=True)

    return guesses_ranked, guesses_detail