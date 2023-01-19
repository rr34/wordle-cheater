from re import finditer, findall
from math import prod

def word_list_generator1(text_file_path):
    word_length = 5
    with open(text_file_path, 'r') as words_file:
        words_str = words_file.read()
    words_starts = [i.start() for i in finditer(': ', words_str)]
    words_list = [words_str[i+2:i+2+word_length].strip() for i in words_starts]

    return words_list

def letter_counter(words_list, letters_list):
    word_length = 5
    total_words = len(words_list)
    total_characters = sum(len(i) for i in words_list)
    letters_freq_list = []
    for letter in letters_list:
        positional_totals = list(0 for element in range(word_length)) # zeros
        counter = 0
        for word in words_list:
            chars_boolean = [(letter == i) for i in list(word)]
            positional_totals = [sum(x) for x in zip(chars_boolean, positional_totals)]
            counter += len(findall(letter, word))
        positional_totals = [round(i/total_words, 3) for i in positional_totals]
        letters_freq_list.append((letter, positional_totals, round(counter/total_characters, 3)))

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
            letter_score = max(positional_totals)
            score += letter_score

        words_scored_list.append((word, word_pos_scores, score))
    
    words_scored_list.sort(key=lambda x: x[-1], reverse=True)

    return words_scored_list