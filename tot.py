import logging
import telebot
from telebot import types
import requests


from api_token import API_TOKEN

from db_models import init_db, save_message, get_history

# Токен бота
bot = telebot.TeleBot(API_TOKEN)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


user_modes = {}  # Словарь для хранения режимов пользователей

CHAT_MODES = {
    '💬 Чат': 'chat_default',
    '⌚ Планировщик': 'chat_planner',
    '📚 Учёба': 'chat_study',
    '❤️ Здоровье': 'chat_health',
    '😂 Мемы': 'chat_memes',
}

PROMPTS = {
    'chat_default': 'Ты дружелюбный ассистент.',
    'chat_planner': 'Помогай планировать день пользователя.',
    'chat_study': 'Помогай с обучением, объясняй понятия просто.',
    'chat_health': 'Даёшь советы по здоровому образу жизни.',
    'chat_memes': 'Отвечай с юмором, вставляй мемы и шути.',
}



# Функция-заглушка для интеграции с нейросетью
def get_bot_response(messages_history: list) -> str:
    try:
        response = requests.post(
            'http://localhost:1234/v1/chat/completions',
            headers={'Content-Type': 'application/json'},
            json={
                'model': 'meta-llama-3.1-8b-instruct',
                'messages': messages_history,
                'temperature': 0.7,
                'max_tokens': 800
            },
            timeout=60
        )
    except Exception as e:
        print(str(e))
        return 'LM studio not running' if "отверг запрос" in str(e) else str(e)
    
    return response.json()['choices'][0]['message']['content']


# Формирование главного меню
def main_menu():    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('💬 Чат')
    markup.row('⌚ Планировщик', '📚 Учёба')
    markup.row('❤️ Здоровье', '😂 Мемы')
    return markup

@bot.message_handler(commands=['start'])
def handle_start(message):
    logger.info(f"/start от {message.from_user.id}")
    text = (
        "Привет, я твой цифровой помощник-ТОТ! "
        "удачного пользования!"
    )
    bot.send_message(message.chat.id, text, reply_markup=main_menu())
    # bot.send_chat_action(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text in CHAT_MODES)
def handle_mode_change(message):
    user_id = message.from_user.id
    mode_name = message.text
    table = CHAT_MODES[mode_name]
    
    user_modes[user_id] = table

    # Запоминаем системный промпт, если есть
    prompt = PROMPTS.get(table)
    if prompt:
        save_message(table, user_id, 'system', prompt)

    bot.send_message(
        message.chat.id,
        f"🔄 Режим переключён на: {mode_name}\nТеперь ответы будут в контексте этого режима."
    )

# Общий обработчик: всё, что не кнопки
@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_text = message.text

    table = user_modes.get(user_id, 'chat_default')

    bot.send_chat_action(chat_id, 'typing')
    save_message(table, user_id, 'user', user_text)

    history = get_history(table, user_id)
    reply = get_bot_response(history)

    save_message(table, user_id, 'assistant', reply)
    bot.send_message(chat_id, reply)


if __name__ == '__main__':
    init_db()  # Инициализация базы данных
    print("Бот запущен, ожидаю сообщений…")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
