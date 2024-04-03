from collections import defaultdict

# Словарь для хранения ролей игроков
participants = {"Игрок1": "Экипаж", "Игрок2": "Предатель", "Игрок3": "Экипаж"}


# Функция для проведения голосования и обработки результатов
def vote(votes):
    global participants
    # Проверяем, завершено ли голосование
    if len(votes) == len(participants):
        # Находим игрока с наибольшим количеством голосов
        max_votes = max(votes.values())
        max_voted_players = [name for name, votes_count in votes.items() if votes_count == max_votes]

        # Если только один игрок получил наибольшее количество голосов, выкидываем его
        if len(max_voted_players) == 1:
            player_to_eliminate = max_voted_players[0]
            del participants[player_to_eliminate]
            print(f"Игрок '{player_to_eliminate}' исключен из игры!")
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


# Имитация голосования
votes = defaultdict(int)
votes["Игрок1"] = 2
votes["Игрок2"] = 2
votes["Игрок3"] = 1

# Вызов функции для проверки результатов голосования
vote(votes)
print(votes)
