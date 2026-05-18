from api import get_updates, send_message
from config import POLLING_TIMEOUT
from game.quest_system import generate_daily_quest
from game.npc_fsm import npc_react
from game.stats_tracker import update_stats, get_daily_summary
import time

# Хранилище состояний игроков
players = {}

# Клавиатура с кнопками
MAIN_KEYBOARD = {
    "keyboard": [
        [{"text": "📋 Взять квест"}, {"text": "🎁 Раздать листовку"}],
        [{"text": "😊 Улыбнуться"}, {"text": "😤 Надавить"}],
        [{"text": "📊 Статистика"}]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}


def get_or_init_player(chat_id):
    if chat_id not in players:
        players[chat_id] = {
            "npc_state": "НЕЙТРАЛЬНОЕ",  # ← Было "NEUTRAL"
            "stats": {"given": 0, "refusals": 0, "smiles": 0, "interactions": 0, "fatigue": 0, "pushes": 0},
            "quest_active": False
        }
    return players[chat_id]


def handle_message(update):
    if "message" not in update or "text" not in update["message"]:
        return

    chat_id = update["message"]["chat"]["id"]
    text = update["message"]["text"].strip()
    player = get_or_init_player(chat_id)

    # Команда /start с показом клавиатуры
    if text == "/start":
        send_message(
            chat_id,
            "👋 Добро пожаловать в «Симулятор раздачи листовок»!\n\n"
            "Используй кнопки внизу для игры:\n"
            "📋 Бери квесты\n"
            "🎁 Раздавай листовки\n"
            "😊 Улыбайся\n"
            "📊 Смотри статистику"
            "😤 Надавить",
            reply_markup=MAIN_KEYBOARD
        )

    # Кнопка "Взять квест"
    elif text == "📋 Взять квест":
        if not player["quest_active"]:
            player["quest_active"] = True
            quest_text = generate_daily_quest()
            send_message(chat_id, quest_text)
        else:
            send_message(chat_id, "📋 Задание уже активно. Выполни его или начни новый день через /next_day")

    # Кнопка "Раздать листовку"
    elif text == "🎁 Раздать листовку":
        action = "flyer"
        old_state = player["npc_state"]  # Запоминаем старое состояние
        reaction, new_state = npc_react(player["npc_state"], action)
        player["npc_state"] = new_state

        # Считаем успех: если реакция содержит "спасибо" или "возьму" (без учёта регистра)
        success_words = ["спасибо", "возьму", "давай", "интересно", "ладно", "удовольствием", "молодец"]
        success = any(word in reaction.lower() for word in success_words)

        update_stats(player["stats"], action, success)
        if not success and action == "flyer":
            update_stats(player["stats"], "refusal", success=False)

        send_message(
            chat_id,
            f"🎭 Реакция: {reaction}\n📈 Настрой прохожего: {new_state}",
            reply_markup=MAIN_KEYBOARD,
        )

    # Кнопка "Улыбнуться"
    elif text == "😊 Улыбнуться":
        action = "smile"
        reaction, new_state = npc_react(player["npc_state"], action)
        player["npc_state"] = new_state
        success = new_state != "AVOIDING"
        update_stats(player["stats"], action, success)
        send_message(
            chat_id,
            f"😊 Реакция: {reaction}\n📈 Настрой прохожего: {new_state}"
        )

    elif text == "😤 Надавить":
        action = "push"
        reaction, new_state = npc_react(player["npc_state"], action)
        player["npc_state"] = new_state
        success = new_state not in ["AVOIDING", "ANNOYED"]
        update_stats(player["stats"], action, success)
        send_message(
            chat_id,
            f"😤 Ты надавил: {reaction}\n📈 Настрой NPC: {new_state}",
            reply_markup=MAIN_KEYBOARD,
        )

    # Кнопка "Статистика"
    elif text == "📊 Статистика":
        summary = get_daily_summary(player["stats"])
        send_message(chat_id, summary)

    # Команда /next_day
    elif text == "/next_day":
        player["quest_active"] = False
        player["npc_state"] = "NEUTRAL"
        send_message(chat_id, "🌅 Новый день! Нажми 📋 Взять квест, чтобы получить задание.")

    # Все остальные сообщения — игнорируем или просим использовать кнопки
    else:
        send_message(
            chat_id,
            "⚠️ Пожалуйста, используй кнопки внизу для игры!\n"
            "Если кнопки пропали — напиши /start",
            reply_markup=MAIN_KEYBOARD,
        )


def run_bot():
    last_update_id = 0
    print("🤖 Бот запущен. Нажмите Ctrl+C для остановки.")
    while True:
        try:
            updates = get_updates(offset=last_update_id, timeout=POLLING_TIMEOUT)
            if updates.get("ok") and updates.get("result"):
                for update in updates["result"]:
                    last_update_id = update["update_id"] + 1
                    handle_message(update)
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
        time.sleep(1)