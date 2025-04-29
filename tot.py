import logging
import telebot
from telebot import types
import requests

from api_token import API_TOKEN

# Токен бота
bot = telebot.TeleBot(API_TOKEN)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

chat_history = {}  # chat_id: list of messages [{role: 'user'/'assistant', content: str}]

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
    markup.row('🗓 Планировщик', '📚 Учёба')
    markup.row('❤️ Здоровье', '😂 Мемы')
    return markup

@bot.message_handler(commands=['start'])
def handle_start(message):
    logger.info(f"/start от {message.from_user.id}")
    text = (
        "Привет, я твой цифровой помощник-ТОТ! "
        "удачного пользования!"
    )
    # bot.send_message(message.chat.id, text, reply_markup=main_menu())
    bot.send_chat_action(message.chat.id, text)

# Переход в режим чата
# @bot.message_handler(func=lambda m: m.text == '💬 Чат')
# def handle_chat(message):
#     bot.send_message(message.chat.id, "Вы перешли в режим чата. Напишите мне что угодно, и я отвечу!")


# Общий обработчик: всё, что не кнопки
@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    user_text = message.text
    logger.info(f"Получено от {chat_id}: {user_text}")
    bot.send_chat_action(chat_id, 'typing')

    # Инициализация истории
    if chat_id not in chat_history:
        chat_history[chat_id] = []

    # Добавляем сообщение пользователя в историю
    chat_history[chat_id].append({'role': 'user', 'content': user_text})

    # Отправляем всю историю в LM Studio
    reply = get_bot_response(chat_history[chat_id])  # ⬅️ Передаём всю историю

    # Сохраняем ответ нейросети в историю
    chat_history[chat_id].append({'role': 'assistant', 'content': reply})

    # Отправляем пользователю
    bot.send_message(chat_id, reply)
    print(chat_history)


if __name__ == '__main__':
    print("Бот запущен, ожидаю сообщений…")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
