import logging
import telebot
from telebot import types
import requests

# Токен бота
API_TOKEN = '8005807698:AAGyPSIAkGksY9aNxuvPB9T88sL3vTZ8sfY'
bot = telebot.TeleBot(API_TOKEN)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция-заглушка для интеграции с нейросетью
def get_bot_response(user_text: str) -> str:
    """
    Здесь нужно вставить код для обращения к API вашей нейросети.
    Пример с использованием requests:
    response = requests.post(
        'https://your-neural-api.com/generate',
        headers={'Authorization': 'Bearer YOUR_API_KEY'},
        json={'text': user_text}
    )
    if response.status_code == 200:
        data = response.json()
        return data.get('reply', 'Нейросеть вернула пустой ответ')
    else:
        return 'Ошибка при запросе к нейросети'
    """
    # TODO: заменить на реальный вызов вашей НС
    return 'Здесь будет ответ нейросети'

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
        "У тебя открылось меню, в котором ты можешь взаимодействовать со мной, "
        "удачного пользования!"
    )
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

# Переход в режим чата
@bot.message_handler(func=lambda m: m.text == '💬 Чат')
def handle_chat(message):
    bot.send_message(message.chat.id, "Вы перешли в режим чата. Напишите мне что угодно, и я отвечу!")

# Общий обработчик: всё, что не кнопки
@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    user_text = message.text
    logger.info(f"Получено от {message.from_user.id}: {user_text}")
    bot.send_chat_action(message.chat.id, 'typing')

    # Получение ответа от НС
    reply = get_bot_response(user_text)

    # Отправка ответа пользователю
    bot.send_message(message.chat.id, reply)

if __name__ == '__main__':
    print("Бот запущен, ожидаю сообщений…")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
