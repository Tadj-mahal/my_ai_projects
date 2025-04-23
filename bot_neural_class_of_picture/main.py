import os
import time
import telebot
import class_of_picture
from PIL import Image
from requests.exceptions import ReadTimeout, ConnectionError
import urllib3
from urllib3.exceptions import NewConnectionError
from transformers import AutoTokenizer, MarianMTModel
import translator
import google_picture_text_to_text

bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(bot_token)
folder_path = os.getenv('FOLDER_PATH')

@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}, пришли мне фото из галлереи или интернета, а я попробую угадать что на нем изображено.')

@bot.message_handler(content_types=['photo'])
def savephoto(message):
    photo = message.photo[-1]
    file_info = bot.get_file(photo.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    save_path = f'{folder_path}/{photo.file_id}.jpg' 
    with open(save_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    img = Image.open(save_path)
    img = img.convert('RGB')
    img = img.resize((512, 512), Image.LANCZOS)
    img.save(save_path)

    bot.reply_to(message, 'Выполняется анализ изображения...')

    output_en = google_picture_text_to_text.picture_to_text(save_path)

    output_ru = translator.translate(output_en)

    bot.send_message(message.chat.id, f'На картинке: {output_ru}')

def start_polling():
    while True:
        try:
            bot.polling(none_stop=True, timeout=15)
        except (ReadTimeout, ConnectionError, NewConnectionError, OSError) as e:
            print(f"Error occurred: {e}")
            time.sleep(5)

start_polling()