import random


def generate_random_number():
    return random.randint(10000000, 99999999)


def format_random_number(number):
    formatted_number = "{:09d}".format(number)
    return formatted_number[:3] + '-' + formatted_number[3:6] + '-' + formatted_number[6:8]


def end_game():
    global game_over
    game_over = True