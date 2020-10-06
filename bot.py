import telebot
import os
import schedule
import time
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from string import Template
from telebot import types
from telegram import replymarkup
import config
import mysql.connector
import logging

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  port = "3306",
  database = "mikes_db"
)


bot = telebot.TeleBot(config.TOKEN)

cursor = db.cursor()
#cursor.execute("CREATE TABLE users (first_name VARCHAR(255), last_name VARCHAR(255))")
#cursor.execute("ALTER TABLE users ADD COLUMN (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT UNIQUE)")


user_data = {}
#x = 17

class User:
    def __init__(self, first_name):
        self.first_name = first_name,
        self.last_name = ''
 
    

        keys = ['name','first_name','last_name', 'phone', 'vin', 'doit']

        for key in keys:
            self.key = None


# если /help, /start
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_message(message.chat.id,
                ("Добрый день, " + message.from_user.first_name + '!'"\n\nМеня зовут Василий.\n"
                  "Я виртуальный помощник MikesGarage.\n\n"
                  "Мои возможности, которые доступны на данный момент сейчас:\n"
                  "- Записаться в автомастерскую\n"
                  "- Узнавать статус ремонта\n"
                  "- Личный кабинет\n\n"
                  "Доступные команды:\n"
                  "/order_a_call - заказать звонок\n"
                  "/contacts - наши контакты\n"
                ))
    time.sleep(1)
    bot.send_message(message.chat.id,
                ("Прежде чем я смогу открыть полный доступ, необходимо будет зерегистрироваться в нашей системе.\n"
                "Не переживайте, все данные надежно защищены в mikes_cloud и никуда не передаются 💪"
                ))
    time.sleep(1)
    keyboardstart = types.InlineKeyboardMarkup()
    keyboardstart.row(
           telebot.types.InlineKeyboardButton(text="Да",callback_data="Yes"),
           telebot.types.InlineKeyboardButton(text="Нет",callback_data="No"),
       )
    bot.send_message(message.chat.id, 'Вы согласны пройти регистрацию?' ,reply_markup=keyboardstart)


@bot.callback_query_handler(func=lambda message: True)
def send_anytext(message):
    chat_id = message.message.chat.id
    if message.data == 'Yes':
        msg = bot.send_message(chat_id, 'Напишите ваше имя')
        bot.register_next_step_handler(msg, process_first_name_step)
    if message.data == 'No':
        msg = bot.send_message(chat_id, 'Нам очень жаль, но без регистрации вам доступно\n\n /contacts - наши контакты\n / - заказать звонок\n\n'
        'Нажмите Да 👆, если хотите получить все функции')

def process_first_name_step(message):
   try:
        user_id = message.from_user.id
        user_data[user_id] = User(message.text)

        msg = bot.send_message(message.chat.id, 'Напишите вашу фамилию')
        bot.register_next_step_handler(msg, process_last_name_step)

   except Exception as e:
        print(e)




def process_last_name_step(message):
    try:
        user_id = message.from_user.id
        user = user_data[user_id]
        user.last_name = message.text
        msg = bot.send_message(message.chat.id, 'Напишите ваш VIN')
        bot.register_next_step_handler(msg, process_vin_step)

    except Exception as e:
        print(e)
        
def process_vin_step(message):
    try:
        user_id = message.from_user.id
        user = user_data[user_id]
        user.user_vin = message.text

        msg = bot.send_message(message.chat.id, 'Что необходимо сделать?\n\nНапример: Заказать выхлоп')
        bot.register_next_step_handler(msg, process_what_cando)

    except Exception as e:
        bot.reply_to(message, 'oops!!')

def process_what_cando(message):
    try:
        user_id = message.from_user.id
        user = user_data[user_id]
        user.doit = message.text

        msg = bot.send_message(message.chat.id, 'Какой у вас номер телефона?')
        bot.register_next_step_handler(msg, process_phone_step)

    except Exception as e:
        bot.reply_to(message, 'oops!!')



def process_phone_step(message):
    try:
        user_id = message.from_user.id
        user = user_data[user_id]
        user.user_phone = message.text
        sql = "INSERT INTO users (user_id, first_name, last_name, user_phone, user_vin) \
                                  VALUES (%s, %s, %s)"
        val = (user_id ,user.first_name, user.last_name,user.user_phone, user.user_vin)
        cursor.execute(sql, val)
        db.commit()

        bot.send_message(message.chat.id, 'Спасибо за регистрацию!\nВ ближайшее время мы вам позвоним.\n\nТеперь вам доступен личный кабинет.')
        bot.send_message(config.chat_id, getRegData(user, 'Заявка от бота', bot.get_me().username),
                         parse_mode="Markdown")

    except Exception as e:
        print(e)


def getRegData(user, title, name):
    t = Template('$title *$name* \n Имя клиента: *$first_name* \n Фамилия клиента: *$last_name* \n VIN-номер:*$vin* \n Телефон: *$phone* \n Комментарии: *$doit*')

    return t.substitute({
        'title': title,
        'name': name,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'vin': user.user_vin,
        'phone': user.user_phone,
        'doit': user.doit,
    })


bot.polling()