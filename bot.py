import telebot
import os
import schedule
import time
import requests
from telebot import apihelper
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from string import Template
from telebot import types
import config
import proxyconfig


bot = telebot.TeleBot(config.TOKEN)
proxy = telebot.TeleBot(proxyconfig.apihelper.proxy)

user_dict = {}
x = 17

class User:
    def __init__(self, city):
        self.city = city

        keys = ['fullname', 'phone', 'vin', 'doit']

        for key in keys:
            self.key = None


# если /help, /start
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    keyboardstart = types.InlineKeyboardMarkup()
    button_registration = types.InlineKeyboardButton(text="Записаться в сервис ⚡️", callback_data="zapis")
    button_write_to_us = types.InlineKeyboardButton(text="Заказать звонок 📱️", callback_data="recall")
    keyboardstart.add(button_registration)
    keyboardstart.add(button_write_to_us)
    bot.send_message(message.chat.id, "Здравствуйте, "
                     + message.from_user.first_name + '\n'
                     + "Я виртуальный помощник MikesGarage" + '\n\n'
                     + "Я могу:\n\n"
                     + "- Записаться в сервис\n"
                     + "- Заказать обратный звонок\n\n"
                     + "/start - начать сначала\n"
                     , reply_markup=keyboardstart)


@bot.callback_query_handler(func=lambda message: True)
def send_anytext(message):
    chat_id = message.message.chat.id
    if message.data == 'zapis':
        msg = bot.send_message(chat_id, 'Как вас зовут?', parse_mode='HTML')
    bot.register_next_step_handler(msg, process_fullname_step)


def process_fullname_step(message):
   try:
        chat_id = message.chat.id
        user_dict[chat_id] = User(message.text)
        user = user_dict[chat_id]
        user.fullname = message.text
        if not user.fullname.isalpha():
            msg = bot.reply_to(message, 'Я не смог распознать такое имя\nВведите свое имя правильно')
            bot.register_next_step_handler(msg, process_fullname_step)
            return
        msg = bot.send_message(chat_id, 'Напишите ваш VIN')
        bot.register_next_step_handler(msg, process_vin_step)
        
   except Exception as e:
        bot.reply_to(message, 'ooops!!')
        
def process_vin_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.vin = message.text
        
        if len(user.vin) < 17:
            for x in range(0, len(user.vin), 17):
                msg = bot.reply_to(message, 'VIN номер состоит из 17 символов\nПопробуйте еще раз')
                bot.register_next_step_handler(msg, process_vin_step)
        else:
            msg = bot.send_message(chat_id, 'Опишиту вашу проблему.\nЕсли вы не знаете что с вашем автомобилем, напишите - диагностика.\nМы проверим ваш автомобиль и отремонтируем')
            bot.register_next_step_handler(msg, process_what_cando)

    except Exception as e:
        bot.reply_to(message, 'oops!!')

def process_what_cando(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.doit = message.text
        msg = bot.send_message(chat_id, 'Какой у вас номер телефона?')
        bot.register_next_step_handler(msg, process_phone_step)
    except Exception as e:
        bot.reply_to(message, 'oops!!')


def process_phone_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.phone = message.text
        bot.send_message(chat_id, 'В ближайшее время мы вам позвоним.\nОжидайте звонка.')
        bot.send_message(config.chat_id, getRegData(user, 'Заявка от бота', bot.get_me().username),
                         parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, 'ooops!!')


def getRegData(user, title, name):
    t = Template('$title *$name* \n Имя клиента: *$fullname* \n VIN-номер:*$vin* \n Телефон: *$phone* \n Комментарии: *$doit*')

    return t.substitute({
        'title': title,
        'name': name,
        'fullname': user.fullname,
        'vin': user.vin,
        'phone': user.phone,
        'doit': user.doit,
    })


bot.polling()
