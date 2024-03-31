import random
from CONSTANTS import colors

player_colors = {}
participants = {}
first_name_to_id = {'Joseph': 6960356990, 'Alexandr': 805222144, 'gfgfgfg': 54656565, 'dfhfhfhf': 6435345435,
                    'dhfdhfhf': 32432, 'sfsdfds': 65765, 'fhfgfghnfd': 2342345, 'asfwegerg': 678657, 'fgmfgbdfv': 235465,
                    'fgnfgnfg': 45756574}


def assign_roles(player_count, imposter_count):
    global player_colors
    roles = ['Экипаж', 'Предатель']
    players = list(first_name_to_id.keys())
    imposters = random.sample(players, imposter_count)
    available_colors = colors.copy()
    for player_id in players:
        role = roles[1] if player_id in imposters else roles[0]
        participants[player_id] = role
        color = random.choice(available_colors)  # Выбираем случайный цвет из доступных
        available_colors.remove(color)  # Удаляем выбранный цвет из списка доступных
        player_colors[player_id] = color  # Сохраняем цвет для игрока
        print(player_colors)
    print(f"Распределенные роли: {participants}")

assign_roles(10, 3)
