import os
import telebot
from telebot import types
from threading import Timer
from datetime import datetime, timedelta
import pytz
import uuid

bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(bot_token)

commands = [
    telebot.types.BotCommand("start", "Запуск бота"),
    telebot.types.BotCommand("status", "Текущие напоминания"),
    telebot.types.BotCommand("delete", "Удалить напоминание")
]
bot.set_my_commands(commands)

reminders = {}
local_tz = pytz.timezone('Europe/Moscow')

def log(message):
    print(message)

@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}, это бот напоминалка, он будет напоминать тебе о всех важных событиях твоей жизни, отправляя сообщение через определенное тобой время.')
    bot.send_message(message.chat.id, 'Можем приступать :)\nНапиши напоминалку.')

@bot.message_handler(commands=['status'])
def status(message):
    try:
        if message.chat.id in reminders and reminders[message.chat.id]:
            reminders_sorted = sorted(
                reminders[message.chat.id], 
                key=lambda x: x['time'] if x['time'] is not None else local_tz.localize(datetime.max)
            )
            response = 'Текущие напоминания:\n\n'
            for i, reminder in enumerate(reminders_sorted):
                if reminder['time'] is not None:
                    response += f"{i + 1}. Время: {reminder['time'].strftime('%d.%m.%Y %H:%M')}\nСообщение: {reminder['text']}\n\n"
                else:
                    response += f"{i + 1}. (Время не установлено)\nСообщение: {reminder['text']}\n\n"
        else:
            response = 'Нет текущих напоминаний.'

        bot.send_message(message.chat.id, response)
    except Exception as e:
        bot.send_message(message.chat.id, f'Произошла ошибка при получении статуса: {str(e)}.')

@bot.message_handler(commands=['delete'])
def delete(message):
    try:
        if message.chat.id in reminders and reminders[message.chat.id]:
            send_reminders_to_delete(message)
        else:
            bot.send_message(message.chat.id, 'Нет текущих напоминаний для удаления.')
    except Exception as e:
        bot.send_message(message.chat.id, f'Произошла ошибка при удалении напоминания: {str(e)}.')

def send_reminders_to_delete(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
    button_cancel = types.KeyboardButton('Отмена')
    markup.add(button_cancel)
    reminders_sorted = sorted(
        reminders[message.chat.id], 
        key=lambda x: x['time'] if x['time'] is not None else local_tz.localize(datetime.max)
    )
    for i, reminder in enumerate(reminders_sorted):
        if reminder['time'] is not None:
            button = types.KeyboardButton(f"{i + 1}. Время: {reminder['time'].strftime('%d.%m.%Y %H:%M')}\nСообщение: {reminder['text']}")
        else:
            button = types.KeyboardButton(f"{i + 1}. (Время не установлено)\nСообщение: {reminder['text']} ({reminder['id']})")
        markup.add(button)
    bot.send_message(message.chat.id, 'Выберите напоминание для удаления или нажмите "Отмена" для выхода.', reply_markup=markup)
    bot.register_next_step_handler(message, handle_delete_selection)

def handle_delete_selection(message):
    chat_id = message.chat.id
    text = message.text.lower()

    if text == 'отмена':
        bot.send_message(chat_id, 'Удаление напоминания отменено.', reply_markup=types.ReplyKeyboardRemove())
        return

    try:
        reminder_id = text.split('(')[-1].strip(')')
        reminder_to_delete = next((r for r in reminders[chat_id] if r['id'] == reminder_id), None)
        if reminder_to_delete:
            reminders[chat_id].remove(reminder_to_delete)
            bot.send_message(chat_id, f'Напоминание: "{reminder_to_delete["text"]}" было удалено.', reply_markup=types.ReplyKeyboardRemove())
            if reminders[chat_id]:
                send_reminders_to_delete(message)
            else:
                bot.send_message(chat_id, 'Больше нет напоминаний для удаления.', reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.send_message(chat_id, 'Неверный выбор. Попробуйте снова или нажмите "Отмена" для выхода.', reply_markup=types.ReplyKeyboardRemove())
            send_reminders_to_delete(message)
    except ValueError:
        bot.send_message(chat_id, 'Неверный формат. Попробуйте снова или нажмите "Отмена" для выхода.', reply_markup=types.ReplyKeyboardRemove())
        send_reminders_to_delete(message)

@bot.message_handler(content_types=['text'])
def notice(message):
    try:
        if message.chat.id not in reminders:
            reminders[message.chat.id] = []

        reminder = {
            'id': str(uuid.uuid4()),  # Генерация уникального идентификатора
            'text': message.text,
            'time': None  # Время будет установлено позже
        }
        reminders[message.chat.id].append(reminder)

        markup = types.InlineKeyboardMarkup(row_width=3)
        button1 = types.InlineKeyboardButton('15 мин', callback_data=f'900-{reminder["id"]}')
        button2 = types.InlineKeyboardButton('30 мин', callback_data=f'1800-{reminder["id"]}')
        button3 = types.InlineKeyboardButton('45 мин', callback_data=f'2700-{reminder["id"]}')
        button4 = types.InlineKeyboardButton('1 час', callback_data=f'3600-{reminder["id"]}')
        button5 = types.InlineKeyboardButton('2 часа', callback_data=f'7200-{reminder["id"]}')
        button6 = types.InlineKeyboardButton('3 часа', callback_data=f'10800-{reminder["id"]}')
        button7 = types.InlineKeyboardButton('1 день', callback_data=f'86400-{reminder["id"]}')
        button8 = types.InlineKeyboardButton('2 дня', callback_data=f'172800-{reminder["id"]}')
        button9 = types.InlineKeyboardButton('3 дня', callback_data=f'259200-{reminder["id"]}')
        button10 = types.InlineKeyboardButton('Свой вариант', callback_data=f'custom-{reminder["id"]}')
        markup.add(button1, button2, button3, button4, button5, button6, button7, button8, button9, button10)

        button_cancel = types.InlineKeyboardButton('Отмена', callback_data=f'cancel-{reminder["id"]}')
        markup.add(button_cancel)

        bot.send_message(message.chat.id, 'Через сколько напомнить?', reply_markup=markup)
    except Exception as e:
        bot.send_message(message.chat.id, f'Произошла ошибка при создании напоминания: {str(e)}.')

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        chat_id = call.message.chat.id
        if '-' in call.data:
            action, reminder_id = call.data.split('-', 1)

            reminder = next((r for r in reminders[chat_id] if r['id'] == reminder_id), None)
            if reminder is None:
                bot.edit_message_text('Напоминание не найдено.', chat_id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup())
                return

            if action.isdigit():  # Это установка времени напоминания
                reminder_time = int(action)
                reminder_datetime = datetime.now(local_tz) + timedelta(seconds=reminder_time)
                reminder['time'] = reminder_datetime

                Timer(reminder_time, send_reminder, args=[chat_id, reminder_id]).start()
                log(f'Таймер установлен на {reminder_time} секунд для чата {chat_id} и напоминания {reminder_id}.')

                if reminder_time <= 2700:
                    response = f'Напомню через {reminder_time // 60} мин.'
                elif reminder_time == 3600:
                    response = f'Напомню через 1 час.'
                elif 3600 < reminder_time < 86400:
                    response = f'Напомню через {reminder_time // 3600} часа.'
                elif reminder_time == 86400:
                    response = f'Напомню через 1 день.'
                else:
                    days = reminder_time // 86400
                    response = f'Напомню через {days} дня.'

                bot.edit_message_text(response, chat_id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup())
            elif action == 'custom':
                markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
                button_cancel = types.KeyboardButton('Отмена')
                markup.add(button_cancel)
                bot.send_message(chat_id, 'Введите время напоминания в формате "ДД.ММ.ГГГГ ЧЧ:ММ".', reply_markup=markup)
                bot.register_next_step_handler(call.message, set_custom_time, reminder_id)
                bot.delete_message(chat_id, call.message.message_id)
            elif action == 'cancel':
                reminders[chat_id] = [r for r in reminders[chat_id] if r['id'] != reminder_id]
                bot.edit_message_text('Напоминание было отменено.', chat_id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup())
            else:
                bot.edit_message_text('Неизвестное действие.', chat_id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup())
    except Exception as e:
        bot.send_message(chat_id, f'Произошла ошибка при обработке запроса: {str(e)}.')

def set_custom_time(message, reminder_id):
    chat_id = message.chat.id
    text = message.text

    if text.lower() == 'отмена':
        bot.send_message(chat_id, 'Установка времени отменена.', reply_markup=types.ReplyKeyboardRemove())
        return

    try:
        reminder_time = datetime.strptime(text, '%d.%m.%Y %H:%M')
        reminder_time = local_tz.localize(reminder_time)

        if reminder_time <= datetime.now(local_tz):
            bot.send_message(chat_id, 'Введенное время уже прошло. Попробуйте снова или нажмите/напишите "Отмена".', reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(message, set_custom_time, reminder_id)
            return

        reminder = next((r for r in reminders[chat_id] if r['id'] == reminder_id), None)
        if reminder is None:
            bot.send_message(chat_id, 'Напоминание не найдено.', reply_markup=types.ReplyKeyboardRemove())
            return

        reminder['time'] = reminder_time
        reminder_seconds = (reminder_time - datetime.now(local_tz)).total_seconds()
        Timer(reminder_seconds, send_reminder, args=[chat_id, reminder_id]).start()
        log(f'Таймер установлен на {reminder_seconds} секунд для чата {chat_id} и напоминания {reminder_id}.')

        bot.send_message(chat_id, f'Напомню в {reminder_time.strftime("%d.%m.%Y %H:%M")}.', reply_markup=types.ReplyKeyboardRemove())
    except ValueError:
        bot.send_message(chat_id, 'Неправильный формат даты и времени. Попробуйте снова или нажмите/напишите "Отмена".', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, set_custom_time, reminder_id)

def send_reminder(chat_id, reminder_id):
    try:
        reminder = next((r for r in reminders[chat_id] if r['id'] == reminder_id), None)
        if reminder is not None:
            bot.send_message(chat_id, f'Напоминание: {reminder["text"]}')
            reminders[chat_id].remove(reminder)
    except Exception as e:
        bot.send_message(chat_id, f'Произошла ошибка при отправке напоминания: {str(e)}.')

log('Бот запущен.')
bot.polling(none_stop=True)