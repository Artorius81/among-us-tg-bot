# -*- coding: utf-8 -*-

import time as t
import telebot
import re
import threading as th
from CONSTANTS import *
from functions import *


def main(bot):
    random_number = generate_random_number()
    formatted_random_number = format_random_number(random_number)
    print(f"Код для починки системы вентиляции кислорода: {formatted_random_number}")

    def generate_player_list():
        player_list = "\n".join(
            [f"{index + 1}. {name} ({contestant_color.get(name, 'неизвестный цвет')})" for index, name in
             enumerate(contestant_name.keys())])
        return player_list if player_list else "Список игроков пуст."

    @bot.message_handler(func=lambda message: message.text == "Показать всех игроков")
    def show_player_list(message):
        player_list = generate_player_list()
        bot.send_message(message.chat.id, player_list, parse_mode='HTML')

    def save_name(message):
        name = message.text
        user_id = message.chat.id
        contestant_name[name] = user_id
        print(f"Имена пользователей: {contestant_name}")
        bot.send_message(message.chat.id,
                         '\U0001F44D <b>Ага, запомнил!</b>\n\nА теперь введите себе цвет.\n\n<i>Для красоты можно использовать эмодзи.</i>',
                         parse_mode='HTML')
        bot.register_next_step_handler(message, save_color)

    def save_color(message):
        color = message.text
        user_id = message.chat.id
        for name, ids in contestant_name.items():
            if ids == user_id:
                contestant_color[name] = color
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(telebot.types.KeyboardButton("Войти в хаб"))
        print(f"Цвета пользователей: {contestant_color}")
        bot.send_message(message.chat.id,
                         "\U0001F44D <b>Понял!</b>\n\n<i>Нажмите 'Войти в хаб', чтобы присоединиться.</i>",
                         reply_markup=markup, parse_mode='HTML')

    @bot.message_handler(commands=['start'])
    def start(message):
        bot.send_message(message.chat.id,
                         f"Добро пожаловать в <b>Among МиМ</b> ඞ\n\n📜 Несколько советов для наилучшей игры:\n\n<i>❗ чтобы бот был ещё прекраснее, можно использовать эмодзи при вводе имени и цвета</i>\n\n<i>❗ только один из экипажа что-то делает (вводит код, созывает собрание)</i>\n\n<i>❗ только один из предателей что-то делает (устраивает саботаж и т.д)</i>\n\n✅ Вроде всё. Когда будете готовы, выберите команду /connect в меню.\n\nИ не ломайте бота, пожалуйста 🥺",
                         parse_mode='HTML')

    @bot.message_handler(commands=['connect'])
    def connect(message):
        global game_over
        if game_over:
            contestant_name.clear()
            contestant_color.clear()
            participants.clear()
            player_colors.clear()
            first_name_to_id.clear()
        game_over = False
        bot.send_message(message.chat.id,
                         f"\U0001F4AC <b>Введите себе игровое имя</b>\n\nТак игрокам будет проще понять, кто есть кто.\n\n<i>Для красоты можно использовать эмодзи.</i>",
                         parse_mode='HTML')
        bot.register_next_step_handler(message, save_name)

    @bot.message_handler(func=lambda message: message.text == "Войти в хаб")
    def join_game(message):
        # user_id = message.chat.id
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(telebot.types.KeyboardButton("Показать всех игроков"))
        # markup.add(telebot.types.KeyboardButton("Ожидаем начало..."))
        print(f"Подключенные пользователи: {contestant_name}")
        bot.send_message(message.chat.id, "<b>Ожидаем начало игры...</b>", reply_markup=markup, parse_mode='HTML')

    @bot.message_handler(commands=['run'])
    def setup_game(message):
        admins[message.chat.id] = None
        for adm in admins.keys():
            print(f"id администратора: {adm}")
        bot.send_message(message.chat.id, "Введите количество игроков:")
        bot.register_next_step_handler(message, set_players_count)

    def set_players_count(message):
        try:
            player_count = int(message.text)
            bot.send_message(message.chat.id, "Введите количество предателей:")
            bot.register_next_step_handler(message, set_imposters_count, player_count)
        except ValueError:
            bot.send_message(message.chat.id, "Неправильный формат. Введите число.")

    def set_imposters_count(message, player_count):
        try:
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            imposter_count = int(message.text)
            markup.add(telebot.types.KeyboardButton("Начать игру"))
            bot.send_message(message.chat.id,
                             f"Настройки игры: \n{player_count} игроков, \n{imposter_count} предателей.",
                             reply_markup=markup)
            assign_roles(player_count, imposter_count)
            bot.register_next_step_handler(message, start_game, player_count, imposter_count)
        except ValueError:
            bot.send_message(message.chat.id, "Неправильный формат. Введите число.")

    def start_game(message, player_count, imposter_count):
        global game_started
        if message.text == "Начать игру":
            game_started = 1
            player_list = "\n".join(
                [f"{index + 1}. {name} - Роль: {role}, Цвет: {contestant_color.get(name, 'Не определен')}" for
                 index, (name, role) in
                 enumerate(participants.items())])
            print(f"Игроки:\n {player_list}")
            for admin_id in admins:
                bot.send_message(admin_id, f"<b>Роли игроков:</b>", parse_mode='HTML')
                bot.send_message(admin_id, f"{player_list}")
            notify_participants(f"Игра началась!")
        else:
            bot.send_message(message.chat.id, "Нажмите кнопку 'Начать игру', чтобы начать игру.")

    def assign_roles(player_count, imposter_count):
        roles = ['Экипаж', 'Предатель']
        players = list(contestant_name.keys())
        imposters = random.sample(players, imposter_count)
        for player_id in players:
            role = roles[1] if player_id in imposters else roles[0]
            participants[player_id] = role
        print(f"Распределенные роли: {participants}")

    def notify_participants(message):
        for first_name, role in participants.items():
            user_id = contestant_name.get(first_name)
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            if role == 'Предатель':
                emoji = sad_emoji
                markup.add(telebot.types.KeyboardButton("Саботаж системы вентиляции кислорода"))
                markup.add(telebot.types.KeyboardButton("Саботаж двигателя"))
                markup.add(telebot.types.KeyboardButton("Сообщить о трупе"))
            else:
                emoji = happy_emoji
                markup.add(telebot.types.KeyboardButton("Сообщить о трупе"))
                markup.add(telebot.types.KeyboardButton("Созвать собрание"))
            bot.send_message(user_id,
                             f"\U0001F525 <b>{message}</b> \U0001F525 \n\n<i>Ваша роль:</i> <tg-spoiler>{role} {emoji}</tg-spoiler>\n\n<i>Ваш цвет:</i> <tg-spoiler>{contestant_color[first_name]}</tg-spoiler>",
                             reply_markup=markup,
                             parse_mode='HTML')

    def notify_participants_continue(message):
        for first_name, role in participants.items():
            user_id = contestant_name.get(first_name)
            if user_id:
                markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                if role == 'Предатель':
                    emoji = sad_emoji
                    markup.add(telebot.types.KeyboardButton("Саботаж системы вентиляции кислорода"))
                    markup.add(telebot.types.KeyboardButton("Саботаж двигателя"))
                    markup.add(telebot.types.KeyboardButton("Сообщить о трупе"))
                else:
                    emoji = happy_emoji
                    markup.add(telebot.types.KeyboardButton("Сообщить о трупе"))
                    markup.add(telebot.types.KeyboardButton("Созвать собрание"))
                bot.send_message(user_id,
                                 f"\U0001F525 <b>{message}</b> \U0001F525 \n\n<i>Ваша роль:</i> <tg-spoiler>{role} {emoji}</tg-spoiler>\n\n<i>Ваш цвет:</i> <tg-spoiler>{contestant_color[first_name]}</tg-spoiler>",
                                 reply_markup=markup,
                                 parse_mode='HTML')

    # @bot.message_handler(func=lambda message: message.text == "adm: Продолжить игру")
    # def continue_game(message):
    #     global voting_active
    #
    #     if not voting_active:
    #         return
    #
    #     # подсчет голосов для каждого участника
    #     max_votes = 0
    #     max_voted_players = []
    #     for player, votes_count in votes.items():
    #         if votes_count > max_votes:
    #             max_votes = votes_count
    #             max_voted_players = [player]
    #         elif votes_count == max_votes:
    #             max_voted_players.append(player)
    #
    #     # отправка сообщения о результатах голосования
    #     if max_voted_players:
    #         if len(max_voted_players) == len(participants):
    #             send_message_to_all("Принято решение никого не выбрасывать")
    #             bot.register_next_step_handler(message, notify_participants_continue("Игра продолжается"))
    #         else:
    #             for player in max_voted_players:
    #                 send_message_to_all(f"{player} был выкинут из шлюза большинством голосов.\n\nПомянем.")
    #
    #                 # игрок стерт со словаря = выкинут из игры
    #                 del participants[player]
    #                 bot.register_next_step_handler(message, notify_participants_continue("Игра продолжается"))
    #
    #     voting_active = False
    #     votes.clear()
    #
    #     # Проверка условий победы
    #     crew_left = any(role == "Экипаж" for role in participants.values())
    #     traitors_left = any(role == "Предатель" for role in participants.values())
    #     if not crew_left:
    #         # Предатели победили
    #         send_message_to_all(
    #             "<b>Предатели победили!</b>\n\nВесь личный состав экипажа ликвидирован.\n\nСпасибо за игру!\n\nЧтобы начать новую игру, нажмите <b>&#47;start</b>")
    #     elif not traitors_left:
    #         # Экипаж победил
    #         send_message_to_all(
    #             "<b>Экипаж победил!</b>\n\nВсе предатели ликвидированы.\n\nСпасибо за игру!\n\nЧтобы начать новую игру, нажмите <b>&#47;start</b>")
    #
    #     # Убедимся, что кнопка "adm: Продолжить игру" доступна админу после завершения голосования
    #     markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    #     markup.add(telebot.types.KeyboardButton("adm: Продолжить игру"))
    #     for admin_id in admins:
    #         bot.send_message(admin_id,
    #                          "<b>adm: Закончить голосование</b>\n\nНажмите кнопку, чтобы завершить голосование.",
    #                          reply_markup=markup, parse_mode='HTML')
    #     bot.register_next_step_handler(message, notify_participants_continue("Игра продолжается"))

    @bot.message_handler(func=lambda message: message.text == "adm: Продолжить игру")
    def continue_game(message):
        global voting_active, game_over

        hide_markup = telebot.types.ReplyKeyboardRemove()

        if not voting_active:
            return

        print(len(votes), len(participants))
        # print(f"Так выглялит словарь votes {votes}")
        # print(f"Так выглядит словарь {contestant_color}")

        # Проверяем, завершено ли голосование
        if len(votes) == len(participants):
            # Находим игрока с наибольшим количеством голосов
            max_votes = max(votes.values())
            max_voted_players = [name for name, votes_count in votes.items() if votes_count == max_votes]

            # Если только один игрок получил наибольшее количество голосов, выкидываем его
            if len(max_voted_players) == 1:
                player_to_eliminate = max_voted_players[0]
                formatted_votes = "\n".join([f"{player}: {count} голос (ов)" for player, count in votes.items()])
                for admin in admins:
                    bot.send_message(admin, f"<b>adm: Статистика голосов:</b>\n\n{formatted_votes}", parse_mode='HTML',
                                     reply_markup=hide_markup)
                # notify_participants_continue("Игра продолжается")
                del participants[player_to_eliminate]
                if player_to_eliminate in contestant_color.keys():
                    del contestant_color[player_to_eliminate]
                send_message_to_all(
                    f"{player_to_eliminate} ({contestant_color.get(player_to_eliminate)}) был выкинут из шлюза большинством голосов.\n\nПомянем.")
                notify_participants_continue("Игра продолжается")
            else:
                formatted_votes = "\n".join([f"Игрок {player}: {count} голос (ов)" for player, count in votes.items()])
                for admin in admins:
                    bot.send_message(admin, f"<b>adm: Статистика голосов:</b>\n\n{formatted_votes}", parse_mode='HTML',
                                     reply_markup=hide_markup)
                send_message_to_all("Принято решение никого не выбрасывать")
                notify_participants_continue("Игра продолжается")

        voting_active = False
        votes.clear()

        # Выводим статистику
        # show_statistics(votes)

        # Проверяем условия победы
        check_victory_conditions()

        # Убедимся, что кнопка "adm: Продолжить игру" доступна админу после завершения голосования
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(telebot.types.KeyboardButton("adm: Продолжить игру"))

    # Функция для проверки условий победы
    def check_victory_conditions():
        global game_over
        # Проверка условий победы
        crew_left = any(role == "Экипаж" for role in participants.values())
        traitors_left = any(role == "Предатель" for role in participants.values())
        if not crew_left:
            # Предатели победили
            game_over = True
            send_message_to_all(
                "<b>Предатели победили!</b>\n\nВесь личный состав экипажа ликвидирован.\n\nСпасибо за игру!\n\nЧтобы начать новую игру, нажмите <b>&#47;connect</b>")
        elif not traitors_left:
            # Экипаж победил
            game_over = True
            send_message_to_all(
                "<b>Экипаж победил!</b>\n\nВсе предатели ликвидированы.\n\nСпасибо за игру!\n\nЧтобы начать новую игру, нажмите <b>&#47;connect</b>")
        elif len(participants) == 2:
            roles = list(participants.values())
            if roles.count("Экипаж") == 1 and roles.count("Предатель") == 1:
                game_over = True
                send_message_to_all(
                    "<b>Предатели победили!</b>\n\nОстались только два игрока: один экипаж и один предатель.\n\nСпасибо за игру!\n\nЧтобы начать новую игру, нажмите <b>&#47;connect</b>")

    # Функция для вывода статистики
    def show_statistics(votes):
        # Создаем текст статистики
        hide_markup = telebot.types.ReplyKeyboardRemove()
        statistics_text = "Статистика голосования:\n"
        for player, votes_count in votes.items():
            statistics_text += f"{player}: {votes_count} голос(ов)\n"
        for admin in admins:
            bot.send_message(admin, statistics_text, parse_mode='HTML', reply_markup=hide_markup)

    def send_message_to_all(message):
        hide_markup = telebot.types.ReplyKeyboardRemove()
        for user_id in contestant_name.values():
            bot.send_message(user_id, '\U0001F3C6 ' + message, parse_mode='HTML', reply_markup=hide_markup)

        for admin_id in admins:
            bot.send_message(admin_id, 'adm: ' + message, parse_mode='HTML', reply_markup=hide_markup)

    @bot.message_handler(func=lambda message: message.text == "Созвать собрание")
    def emergency_meeting(message):
        global voting_active
        voting_active = True
        for name in participants.keys():
            votes[name] = 0
        for name, ids in contestant_name.items():
            if message.chat.id == ids:
                initiator_name = name
        for user_id in contestant_name.values():
            print(user_id)
            bot.send_message(user_id,
                             f"\U0001F4AD <i>{initiator_name} ({contestant_color.get(initiator_name)})</i> созывает собрание! Все в <b>зал собраний!</b>",
                             parse_mode='HTML')
        show_participants()

    @bot.message_handler(func=lambda message: message.text == "Сообщить о трупе")
    def emergency_meeting_corp(message):
        global voting_active
        voting_active = True
        for name in participants.keys():
            votes[name] = 0
        for name, ids in contestant_name.items():
            if message.chat.id == ids:
                initiator_name = name
        for user_id in contestant_name.values():
            bot.send_message(user_id,
                             f"\U0001F4AD <i>{initiator_name} ({contestant_color.get(initiator_name)})</i> обнаружил труп! Все в <b>зал собраний!</b>",
                             parse_mode='HTML')
        show_participants()

    def show_participants():
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(telebot.types.KeyboardButton("Выбрать игрока"))
        markup_adm = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for user_id in contestant_name.values():
            bot.send_message(user_id,
                             "\U0001F4AD <b>Собрание начато</b>\n\nСейчас вы можете проголосовать (или воздержаться) за того, кого считаете предателем. Или просто кого хотите выкинуть в шлюз.",
                             reply_markup=markup, parse_mode='HTML')
        for admin_id in admins:
            markup_adm.add(telebot.types.KeyboardButton("adm: Продолжить игру"))
            bot.send_message(admin_id,
                             "<b>adm: Экипаж начал собрание</b>\n\nИдёт голосование...",
                             reply_markup=markup_adm, parse_mode='HTML')

    @bot.message_handler(func=lambda message: message.text == "Выбрать игрока" and voting_active)
    def show_all_participants(message):
        for name, color in contestant_color.items():
            participants_new.append(f"{name + f' ({color})'}")
        if voting_active:
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            for name, color in contestant_color.items():
                button_text = f"{name} ({color})"
                markup.add(telebot.types.KeyboardButton(button_text))
            bot.send_message(message.chat.id, "Выберите игрока за которого отдадите свой голос:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Голосование еще не начато или уже завершено.")

    @bot.message_handler(func=lambda message: message.text in participants_new and voting_active)
    def vote(message):
        global votes, voting_active
        voted_name = re.findall(r'(.+?)\s*\(', message.text)[0]
        votes[voted_name] += 1
        # markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        bot.send_message(message.chat.id, f"Вы проголосовали за '{voted_name}'!")
        hide_markup = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Спасибо за ваш голос!", reply_markup=hide_markup)

    def for_admins(admin_id, sabotage_type):
        global sabotage_disabled, game_over
        sabotage_disabled = False
        sabotage_active_adm = True
        sabotage_start_time_adm = t.time()
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        if sabotage_type == 'Двигатель выведен из строя':
            markup.add(telebot.types.KeyboardButton("Саботаж устранён"))
        bot.send_message(admin_id,
                         f"\U0001F913 <b>Для админа</b> \n\nОдин из предателей устроил саботаж ({sabotage_type}). \n\n<i>Таймер запущен.</i>",
                         parse_mode='HTML',
                         reply_markup=markup)
        if sabotage_type == 'Система вентиляции кислорода выведена из строя':
            bot.send_message(admin_id,
                             f"\U0001F6E1 <b>adm: Был запрошен код</b>\n\nСистема вентиляции кислорода вышла из строя, а значит экипажу требуется код.\n\nКод: {formatted_random_number}",
                             parse_mode='HTML')
        sabotage_message_adm = bot.send_message(admin_id,
                                                f"\U000023F3 adm: Оставшееся время для устранения саботажа: 3 мин.",
                                                reply_markup=None)
        while (sabotage_active_adm is True) and (not sabotage_disabled):
            time_elapsed = int(t.time() - sabotage_start_time_adm)
            if time_elapsed >= 180:
                markup = telebot.types.ReplyKeyboardRemove()
                bot.send_message(admin_id,
                                 "\U0000231B adm: <b>Время вышло</b>\n\n\U0001F4A9 Экипаж проиграл\n\nСпасибо за игру!\n\nЧтобы начать новую игру, нажмите <b>&#47;connect</b>",
                                 reply_markup=markup, parse_mode='HTML')
                game_over = True
                break
            else:
                bot.edit_message_text(
                    f"\U000023F3 adm: Оставшееся время для устранения саботажа: {180 - time_elapsed} сек.",
                    admin_id, sabotage_message_adm.message_id)
                t.sleep(1)

    def for_contestants(user_id, role, sabotage_type):
        global sabotage_disabled, game_over
        sabotage_disabled = False
        sabotage_active = True
        sabotage_start_time = t.time()
        hide_markup = telebot.types.ReplyKeyboardRemove()
        if role == 'Предатель':
            bot.send_message(user_id,
                             f"\U0001F60E <b>Один из наших устроил саботаж!</b> \n\n<i>{sabotage_type}.</i> \n\nУ экипажа есть время, чтобы починить неисправность.",
                             parse_mode='HTML', reply_markup=hide_markup)
            if sabotage_type == 'Система вентиляции кислорода выведена из строя':
                bot.send_message(user_id,
                                 f"\U0001F6E1 <b>Требуется код</b>\n\nЧтобы починить систему вентиляции кислорода экипажу необходимо ввести код.",
                                 parse_mode='HTML', reply_markup=hide_markup)
            sabotage_message = bot.send_message(user_id, f"Оставшееся время для устранения саботажа: 3 мин.")
        else:
            bot.send_message(user_id,
                             f"\U0001F92C <b>Один из предателей устроил саботаж!</b> \n\n<i>{sabotage_type}.</i> \n\nУ вас есть время, чтобы починить неисправность.",
                             parse_mode='HTML', reply_markup=hide_markup)
            if sabotage_type == 'Система вентиляции кислорода выведена из строя':
                bot.send_message(user_id,
                                 f"\U0001F6E1 <b>Требуется код</b>\n\nЧтобы починить систему вентиляции кислорода вам необходимо ввести код.",
                                 parse_mode='HTML', reply_markup=hide_markup)
            sabotage_message = bot.send_message(user_id, f"Оставшееся время для устранения саботажа: 3 мин.")

        while (sabotage_active is True) and (not sabotage_disabled):
            time_elapsed = int(t.time() - sabotage_start_time)
            if time_elapsed >= 180:
                markup = telebot.types.ReplyKeyboardRemove()
                bot.send_message(user_id,
                                 "\U0000231B <b>Время вышло</b>\n\n\U0001F4A9 Экипаж проиграл\n\nСпасибо за игру!\n\nЧтобы начать новую игру, нажмите <b>&#47;connect</b>",
                                 reply_markup=markup, parse_mode='HTML')
                game_over = True
                break
            else:
                bot.edit_message_text(
                    f"\U000023F3 Оставшееся время для устранения саботажа: {180 - time_elapsed} сек.",
                    user_id, sabotage_message.message_id)
                t.sleep(1)

    def run_sabotage(sabotage_type):
        global sabotage_disabled
        threads = []
        all_participants = {**participants, **contestant_name}
        print(f"Роли: {all_participants}")
        for first_name, role in participants.items():
            user_id = contestant_name.get(first_name)
            if user_id:
                thread = th.Thread(target=for_contestants, args=(user_id, role, sabotage_type))
                threads.append(thread)
                thread.start()
        for admin_id in admins:
            thread_adm = th.Thread(target=for_admins, args=[admin_id, sabotage_type])
            threads.append(thread_adm)
            thread_adm.start()

        for thread in threads:
            thread.join()

    def imposters_cooldown_timer():
        global imposters_cooldown, game_over
        imposters_cooldown = 60  # 1 минута
        message_sent = False
        if game_over:
            return
        while imposters_cooldown > 0 and not game_over:
            t.sleep(1)
            imposters_cooldown -= 1
            all_imposters = {contestant_name[first_name] for first_name, role in participants.items() if
                             role == 'Предатель'}
            for user_id in all_imposters:
                if not message_sent:
                    message = bot.send_message(user_id,
                                               f"\U000023F3 До возможности снова саботировать работу осталось: {imposters_cooldown} сек.")
                    message_sent = True
                else:
                    bot.edit_message_text(
                        f"\U000023F3 До возможности снова саботировать работу осталось: {imposters_cooldown} сек.",
                        user_id,
                        message.message_id)

    def start_imposters_cooldown_timer():
        global imposters_cooldown_thread
        if imposters_cooldown_thread and imposters_cooldown_thread.is_alive():
            imposters_cooldown_thread.cancel()
        imposters_cooldown_thread = th.Timer(0, imposters_cooldown_timer)
        imposters_cooldown_thread.start()

    @bot.message_handler(func=lambda message: message.text == "Саботаж системы вентиляции кислорода")
    def sabotage_O2(message):
        global imposters_cooldown
        if imposters_cooldown <= 0:
            run_sabotage("Система вентиляции кислорода выведена из строя")
            th.Thread(target=imposters_cooldown_timer).start()
        else:
            bot.send_message(message.chat.id,
                             "\U000023F3 Пока предателям недоступно нажатие кнопок саботажа. \n\n<i>Пожалуйста, подождите...</i>",
                             parse_mode='HTML')

    @bot.message_handler(func=lambda message: message.text == "Саботаж двигателя")
    def sabotage_engine(message):
        global imposters_cooldown
        if imposters_cooldown <= 0:
            run_sabotage("Двигатель выведен из строя")
            th.Thread(target=imposters_cooldown_timer).start()
        else:
            bot.send_message(message.chat.id,
                             "\U000023F3 Пока предателям недоступно нажатие кнопок саботажа. \n\n<i>Пожалуйста, подождите...</i>",
                             parse_mode='HTML')

    @bot.message_handler(
        func=lambda message: message.text == "Саботаж устранён" or message.text == str(formatted_random_number))
    def sabotage_fixed(message):
        global sabotage_disabled
        sabotage_disabled = True
        for admin_id in admins:
            bot.send_message(admin_id, "\U0001F6E0 <b>adm: Саботаж успешно устранён.</b> \n\nТаймеры остановлены.",
                             parse_mode='HTML')

        for first_name, role in participants.items():
            user_id = contestant_name.get(first_name)
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            if role == 'Предатель':
                markup.add(telebot.types.KeyboardButton("Саботаж системы вентиляции кислорода"))
                markup.add(telebot.types.KeyboardButton("Саботаж двигателя"))
                markup.add(telebot.types.KeyboardButton("Сообщить о трупе"))
                bot.send_message(user_id, "\U0001F6E0 <b>Экипажу удалось устранить поломку.</b>", parse_mode='HTML',
                                 reply_markup=markup)
            elif role == 'Экипаж':
                markup.add(telebot.types.KeyboardButton("Сообщить о трупе"))
                markup.add(telebot.types.KeyboardButton("Созвать собрание"))
                bot.send_message(user_id, "\U0001F6E0 <b>Вам удалось починить неисправность.</b>",
                                 parse_mode='HTML',
                                 reply_markup=markup)

    bot.polling()


if __name__ == '__main__':
    bot = telebot.TeleBot(TOKEN)
    main(bot)
