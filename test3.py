from collections import defaultdict
import re

# Глобальные переменные
voting_active = True
participants = {"Игрок1": "Экипаж", "Игрок2": "Предатель", "Игрок3": "Экипаж", "Игрок4": "Экипаж", "Игрок5": "Экипаж", "Игрок6": "Экипаж", "Игрок7": "Предатель"}
votes = defaultdict(int)
participants_new = []


# Функция для проведения голосования и обработки результатов
def vote(message):
    global voting_active, participants, votes
    # Проверяем, завершено ли голосование
    if len(votes) == len(participants):
        # Находим игрока с наибольшим количеством голосов
        max_votes = max(votes.values())
        max_voted_players = [name for name, votes_count in votes.items() if votes_count == max_votes]

        # Если только один игрок получил наибольшее количество голосов, выкидываем его
        if len(max_voted_players) == 1:
            player_to_eliminate = max_voted_players[0]
            print(f"Игрок '{player_to_eliminate}' исключен из игры!")
            del participants[player_to_eliminate]
        else:
            print("Нет однозначного решения по выбору игрока для исключения.")

        # Выводим статистику
        show_statistics(votes)

        # Проверяем условия победы
        check_victory_conditions()


# Функция для вывода статистики
def show_statistics(votes):
    # Создаем текст статистики
    statistics_text = "Статистика голосования:\n"
    for player, votes_count in votes.items():
        statistics_text += f"{player}: {votes_count} голос(ов)\n"
    print(statistics_text)


# Функция для проверки условий победы
def check_victory_conditions():
    global participants
    crew_count = sum(1 for role in participants.values() if role == "Экипаж")
    traitor_count = sum(1 for role in participants.values() if role == "Предатель")

    if crew_count == 0:
        print("Предатели победили!")
    elif traitor_count == 0:
        print("Экипаж победил!")


# Тестирование функции голосования
votes["Игрок1"] = 1
votes["Игрок2"] = 1
votes["Игрок3"] = 1
votes["Игрок4"] = 1
votes["Игрок5"] = 1
votes["Игрок6"] = 1
votes["Игрок7"] = 1
vote("Игрок1")  # Проверка работы функции голосования

# Тестирование вывода статистики
show_statistics(votes)

# Тестирование проверки условий победы
check_victory_conditions()
