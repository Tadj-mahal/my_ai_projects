import os
import time
import telebot
import firstneural
from PIL import Image
from requests.exceptions import ReadTimeout, ConnectionError
import urllib3
from urllib3.exceptions import NewConnectionError


bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(bot_token)
folder_path = os.getenv('FOLDER_PATH')

@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}, мне известно, что меня создавал один рыжий пацанчик, который несильно разбирался в программировании, и это его первый ботик и первая нейросеть встроенная в этого бота. Возможны баги ошибки и всякое такое, так что надеюсь на понимание)')
    bot.send_message(message.chat.id, 'Отправь мне фото черной цифры на белом фоне. Шаблон для фото ниже, скачай его и напиши там цифру, потом отправь мне.')
    bot.send_photo(message.chat.id, photo = open(f'{folder_path}/mainphoto.jpg', 'rb'))

@bot.message_handler(content_types=['photo'])
def savephoto(message):
    photo = message.photo[-1]
    file_info = bot.get_file(photo.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    save_path = f'{folder_path}/UsersPhotos/{photo.file_id}.jpg'
    with open(save_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    img = Image.open(save_path)
    img = img.convert('RGB')
    img = img.resize((28, 28), Image.LANCZOS)
    img.save(save_path)

    bot.reply_to(message, 'Выполняется поиск цифры на картинке...')

    num_output = firstneural.numai(save_path)

    bot.send_message(message.chat.id, f'На картинке число {num_output}')

def start_polling():
    while True:
        try:
            bot.polling(none_stop=True, timeout=15)
        except (ReadTimeout, ConnectionError, NewConnectionError, OSError) as e:
            print(f"Error occurred: {e}")
            time.sleep(5)

start_polling()