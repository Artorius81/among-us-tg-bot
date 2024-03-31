from collections import defaultdict

TOKEN = '6820769313:AAFhsHsXlDW1Euu0Q5jC16IF4-RdsaBPuj0'

game_started = 0
admins = {}
game_over = False
waiting_for_admin_password = set()

participants_new = {}
participants = {}

colors = ["Красный", "Синий", "Зеленый", "Желтый", "Фиолетовый", "Оранжевый", "Розовый", "Белый",
          "Голубой", "Коричневый", "Серый", "Черный", "Бирюзовый", "Фуксия", "Салатовый",
          "Лаймовый", "Индиго", "Пурпурный", "Сиреневый", "Персиковый"]
player_colors = {}

voting_active = False
votes = defaultdict(int)

first_name_to_id = {}
sabotage_disabled = False
imposters_cooldown_thread = None
imposters_cooldown = 0