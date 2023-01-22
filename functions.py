from time import perf_counter
from re import finditer, findall
from math import prod
from statistics import mean, median

def word_list_parser1():
    word_length = 5
    text_file_path = './wordle-2309.txt'
    with open(text_file_path, 'r') as words_file:
        words_str = words_file.read()
    words_starts = [i.start() for i in finditer(': ', words_str)]
    words_list = [words_str[i+2:i+2+word_length].strip() for i in words_starts]

    return words_list

def word_list_parser2():
    word_length = 5
    text_file_path = './websters-unabridged.txt'
    with open(text_file_path, 'r') as words_file:
        whole_dictionary = words_file.read()
    dictionary_words_list = whole_dictionary.split(sep=None)
    selected_words_list = []
    for text_str in dictionary_words_list:
        if text_str.isalpha() and text_str == text_str.upper() and len(list(text_str)) == word_length:
            selected_words_list.append(text_str)
            if text_str == 'STEAM':
                pass
    
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

def word_scorer(words_list, letters_freq):
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
            chars_boolean = [(letter_tuple[0] == i) for i in list(word)]
            positional_totals = [prod(i) for i in zip(chars_boolean, letter_tuple[1])]
            positional_score = max(positional_totals)
            score += positional_score
            if any(chars_boolean):
                score += letter_tuple[3]

        words_scored_list.append((word, word_pos_scores, score))

    words_scored_list.sort(key=lambda x: x[-1], reverse=True)

    return words_scored_list

def hint_generator(guess_word, solution_word):
    word_length = 5
    guess_word = list(guess_word)
    solution_word = list(solution_word)
    if len(guess_word) == word_length and len(solution_word) == word_length:
        i = 0
        hint = ['B' for element in range(word_length)]
        for i in range(word_length):
            if guess_word[i] == solution_word[i]:
                hint[i] = 'G'
            elif guess_word[i] in solution_word:
                hint[i] = 'O'
        return ''.join(hint)
    else:
        return False

def process_hint(guess, hint, words_list_in):
    removed_words_list = []
    black_letters = []
    blacks = [i for i, x in enumerate(hint) if x=='B']
    for i in blacks:
        if guess[i] not in black_letters:
            black_letters.append(guess[i])

    orange_letters = []
    orange_positional = []
    oranges = [i for i, x in enumerate(hint) if x=='O']
    for i in oranges:
        orange_letters.append(guess[i])
        orange_positional.append((guess[i], i))

    green_positional = []
    greens = [i for i, x in enumerate(hint) if x=='G']
    for i in greens:
        green_positional.append((guess[i], i))

    for word in words_list_in:
        word_list = list(word)
        next_word = False

        if set(word_list) & set(black_letters):
            removed_words_list.append(word)
            next_word = True
        if len(orange_letters) != 0 and not next_word:
            for orange_tuple in orange_positional:
                if word_list[orange_tuple[1]] == orange_tuple[0] and not next_word:
                    removed_words_list.append(word)
                    next_word = True
            if not next_word:
                check_oranges_in = [(i in word_list) for i in orange_letters]
                if not all(i for i in check_oranges_in):
                    removed_words_list.append(word)
                    next_word = True

        if not next_word:
            for green_tuple in green_positional:
                if word_list[green_tuple[1]] != green_tuple[0] and not next_word:
                    removed_words_list.append(word)
                    next_word = True

    words_list_in = list(set(words_list_in) - set(removed_words_list))

    return words_list_in

def rank_guesses(words_list, test_solutions):
    number_to_test = 50
    test_solutions = test_solutions[0:number_to_test]
    total_test_count = len(test_solutions)
    count = 0
    guesses_ranked = []
    start_count = len(test_solutions)
    start_time = perf_counter()
    for guess in words_list:
        start_time = perf_counter()
        word_count_list = []
        for test_solution in test_solutions:
            maybe_hint = hint_generator(guess, test_solution)
            maybe_remaining_words_list = process_hint(guess, maybe_hint, test_solutions)
            word_count_list.append(len(maybe_remaining_words_list))
        average1 = round(1 - mean(word_count_list) / start_count, 3)
        average2 = round(1 - median(word_count_list) / start_count, 3)
        elapsed_time = round(perf_counter() - start_time, 3)
        count += 1
        countdown = len(words_list) - count
        guess_eval = (guess, average1, average2)
        print(f"Evaluated guess: '{str(guess_eval)}' with {total_test_count} test solutions in {elapsed_time} seconds. {countdown} to go.")
        guesses_ranked.append(guess_eval)
        
    guesses_ranked.sort(key=lambda x: x[-1], reverse=True)

    return guesses_ranked