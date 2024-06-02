import requests
import re
import psycopg2
import datetime
import telebot
from telebot import types
from TOKEN import API_KEY

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
  }

responce = requests.get("https://edg-parts.ru/search/VAG/cod of product?source=mycatalog", headers=headers)
bot = telebot.TeleBot(API_KEY)
@bot.message_handler(commands=['start'])
def Hello(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard= True)
    keyboard.add(types.KeyboardButton("Сколько сегодня стоит запчасть"))
    bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}", reply_markup=keyboard)

@bot.message_handler(content_types=['text'])
def request_of_weather(message):
    if message.text == "Сколько сегодня стоит запчасть":
        InlineKeyboard = types.InlineKeyboardMarkup()
        InlineKeyboard.add(types.InlineKeyboardButton("Решетка радиатора", callback_data='Решетка радиатора'))
        bot.send_message(message.chat.id, "Выбери,что хочешь узнать",reply_markup=InlineKeyboard)
@bot.callback_query_handler(func=lambda call: True)
def GetAnsw(call):
        if call.data == 'Решетка радиатора':
            responce = requests.get("https://edg-parts.ru/search/VAG/cod_of_product?source=mycatalog", headers=headers)
            first_parcing = re.findall(r'<span class="filterDropDownMenu__price__number">*.+₽', responce.text)
            price_parcing = re.findall(r'[0-9]+\s+[0-9]+\s₽',first_parcing[0])
            name_parsing = re.findall(r'<td class="resultDescription  verticalAlignCenter"  >\s+[А-Я]+[а-я]+.+', responce.text)
            second_name_parsing = re.findall(r'[А-Я]+.+', name_parsing[0])
            conn = psycopg2.connect(dbname='ipinfo', host='x.x.x.x', user='user', password='password')
            cur = conn.cursor()
            cur.execute(f'SELECT * FROM Запчасти WHERE Код = \'cod of product\' AND Стоимость = \'{price_parcing[0]}\';')
            result = cur.fetchall()
        if len(result) != 0:
            bot.send_message(call.message.chat.id, f'Цена не менялась с {result[0][0]},\n Стоимость по-прежнему: {result[0][3]}')
        else:
            cur.execute(f'INSERT INTO Запчасти (\"Время запроса\",Запчасть,Код,Стоимость) VALUES (\'{datetime.datetime.now()}\',\'{second_name_parsing[0]}\',\'57A853653BZD4\',\'{price_parcing[0]}\');')
            bot.send_message(call.message.chat.id, f'{second_name_parsing[0]} ,\nСтоимость:{price_parcing[0]}')
        conn.commit()
bot.polling(none_stop=True)
