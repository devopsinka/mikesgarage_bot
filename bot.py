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
  #database = "mikes_db"
)
######Создаем БД#######
#cursor = db.cursor()
#cursor.execute("CREATE DATABASE mikes_db")

bot = telebot.TeleBot(config.TOKEN)
#proxy = telebot.TeleBot(proxyconfig.apihelper.proxy)

user_data = {}
x = 17

class User:
    def __init__(self, fullname):
        self.fullname = fullname,
        self.surename = ''
        self.phone = ''
        self.vin = ''
    

        keys = ['name','fullname','surename', 'phone', 'vin', 'doit']

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
                  "/call_fire - срочный вызов мастера\n"
                  "/contacts - наши контакты\n"
                  "/callme - заказать звонок\n"
                  "/status - узнать статус ремонта\n"
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
        bot.register_next_step_handler(msg, process_fullname_step)
    if message.data == 'No':
        msg = bot.send_message(chat_id, 'Нам очень жаль, но без регистрации вам доступно\n\n /contacts, /callme')

def process_fullname_step(message):
   try:
        chat_id = message.chat.id
        user_data[chat_id] = User(message.text)
        user = user_data[chat_id]
        user.name = message.text
        
        if not user.name.isalpha():
            msg = bot.reply_to(message, 'Я не смог распознать такое имя\nВведите свое имя правильно')
            bot.register_next_step_handler(msg, process_fullname_step)
            return
        msg = bot.send_message(chat_id, 'Напишите вашу фамилию')
        bot.register_next_step_handler(msg, process_surename_step)

   except Exception as e:
        bot.reply_to(message, 'ooops!!')

def process_surename_step(message):
    try:
        chat_id = message.chat.id
        user = user_data[chat_id]
        user_id = message.from_user.id
        user_data[user_id] = User(message.text)
        user.surename = message.text
        if not user.surename.isalpha():
            msg = bot.reply_to(message, 'Я не смог распознать вашу фамилию\nВведите фамилию правильно')
            bot.register_next_step_handler(msg, process_surename_step)
            return
        msg = bot.send_message(chat_id, 'Напишите ваш VIN номер')
        bot.register_next_step_handler(msg, process_vin_step)

    except Exception as e:
        bot.reply_to(message, 'ooops!!')
        
def process_vin_step(message):
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id
        user = user_data[chat_id]
        user.vin = message.text
        if len(user.vin) < 17:
            for x in range(0, len(user.vin), 17):
                msg = bot.reply_to(message, 'VIN номер состоит из 17 символов\nПопробуйте еще раз')
                bot.register_next_step_handler(msg, process_vin_step)
        else:
            msg = bot.send_message(chat_id, 'Что необходимо сделать?\nНапример: Заказать выхлоп')
            bot.register_next_step_handler(msg, process_what_cando)

    except Exception as e:
        bot.reply_to(message, 'oops!!')

def process_what_cando(message):
    try:
        chat_id = message.chat.id
        user = user_data[chat_id]
        user.doit = message.text
        msg = bot.send_message(chat_id, 'Какой у вас номер телефона?')
        bot.register_next_step_handler(msg, process_phone_step)

    except Exception as e:
        bot.reply_to(message, 'oops!!')



def process_phone_step(message):
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id
        user = user_data[chat_id]
        user.phone = message.text
        bot.send_message(chat_id, 'Спасибо за регистрацию!\nВ ближайшее время мы вам позвоним.\n\nТеперь вам доступен личный кабинет.')
        mike_placeholders = "INSERT INTO users (fullname, phone, vin, user_id) \
                                  VALUES (%s, %s, %s) "
        records_list = (user.fullname, user.phone, user.vin, user_id )

        #cursor.execute(sql, sum(val))     
        for values in records_list:
            cursor.execute(mike_placeholders, values)


        db.commit()
        bot.send_message(config.chat_id, getRegData(user, 'Заявка от бота', bot.get_me().username),
                         parse_mode="Markdown")

    except Exception as e:
        print(e)


def getRegData(user, title, name):
    t = Template('$title *$name* \n Имя клиента: *$fullname* \n Фамилия клиента: *$surename* \n VIN-номер:*$vin* \n Телефон: *$phone* \n Комментарии: *$doit*')

    return t.substitute({
        'title': title,
        'name': name,
        'fullname': user.name,
        'surename': user.surename,
        'vin': user.vin,
        'phone': user.phone,
        'doit': user.doit,
    })


bot.polling()