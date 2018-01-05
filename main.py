from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton #библиотека для клавиатуры
from emoji import emojize
import glob
import logging
import random
import os
import re

import settings

#import Flask #for database
import sqlite3 #for database

from bs4 import BeautifulSoup
import urllib.request

from db import db_session, User
from weather import get_wather_for_city

url = 'http://anecdote.pro/Jokes-about-Chuck-Norris.html'
source = urllib.request.urlopen(url)
soup = BeautifulSoup(source, "html.parser")
j = []

items = soup.findAll(lambda tag: len(tag.name) == 1 and tag.name == 'p' and not tag.attrs)
for item in items:
    item2 = item.findNext(text=True)
    if re.search(r'Чак', item2):
        j.append(item2)

avatars = [':smiley_cat:', ':smiling_imp:', ':panda_face:', ':dog:']

jokes = ['What is the difference between a snowman and a snowwoman?Snowballs.']
jokes.append('My dog used to chase people on a bike a lot. It got so bad, finally I had to take his bike away.')
jokes.append('Patient: Oh doctor, I’m just so nervous. This is my first operation.Doctor: Don\'t worry. Mine too.')

logging.basicConfig(level=logging.DEBUG, filename="bot.log")#logging.DEBUG

def get_avatar(user_data):
    if user_data.get('avatar'):
        return user_data.get('avatar')
    else:
        #user_data['avatar'] = emojize(random.choice(avatars), use_aliases=True)
        user_data['avatar'] = random.choice(avatars)
        return user_data['avatar']

def get_keyboard():
    contact_button = KeyboardButton('Контактные данные', request_contact=True)
    location_button = KeyboardButton('Геолокация', request_location=True)
    reply_keyboard = [['Прислать котика', 'Сменить аватарку', 'Пошутить'],['Калькулятор', 'Погода'],[contact_button,location_button]]
    return reply_keyboard
    
def get_user(effective_user, user_data):
    if not user_data.get('user'):
        user = User.query.filter(User.telegram_id==effective_user.id).first()
        if not user:
            user = User(
                telegram_id=effective_user.id,
                first_name=effective_user.first_name,
                last_name=effective_user.last_name,
                avatar=get_avatar(user_data)
            )
            db_session.add(user)
            db_session.commit()
            user['user']=user
        return user
    else:
        return user_data['user']


def reply_to_start_command(bot, update, user_data):
    #first_name = update.effective_user.first_name
    #last_name = update.effective_user.last_name
    #avatar = get_avatar(user_data)
    
    user = get_user(update.effective_user, user_data)
    #print(user)
    reply_keyboard = get_keyboard() #создаем набор кнопок
    
    text = "Привет, {} {}! Я бот, который понимает команду /start".format(user.first_name, emojize(user.avatar, use_aliases=True))
    logging.info("Пользователь {} {} нажал {}".format(user.first_name, user.last_name, "/start"))
    update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)) #передаем кнопки в бота

def count_words(bot, update, args, user_data):
    #print(args)
    avatar = get_avatar(user_data)
    text = "{} количество слов {}".format(avatar, len(args))
    update.message.reply_text(len(args))
    
def chat_with_user(bot, update, user_data):
    #text = emojize(random.choice(avatars), use_aliases=True)
    #avatar = get_avatar(user_data)
    user = get_user(update.effective_user, user_data)
    text = "{} {}".format(update.message.text, emojize(user.avatar, use_aliases=True))
    update.message.reply_text(text)
    
def send_cat(bot, update, user_data):
    cat_list = glob.glob1("cats", "*.jp*g")
    #print(cat_list)
    cat_pic = os.path.join('cats', random.choice(cat_list))
    #print(cat_pic)
    chat_id = update.message.chat_id
    bot.send_photo(chat_id=chat_id, photo=open(cat_pic, 'rb'))

def tell_joke(bot, update, user_data):
    joke = random.choice(j)
    update.message.reply_text(joke)

def calculate1(bot, update, user_data):
    #print(update.message.text)
    if re.match('^([+,\-,*,/])$', update.message.text):
        user_data['op_arg'] = update.message.text
        #print(user_data['op_arg'])
    reply_keyboard = []
    for num in range(10):
        button = "{}".format(num)
        reply_keyboard.append(button)
    update.message.reply_text('Выбери цифру', reply_markup=ReplyKeyboardMarkup([reply_keyboard], resize_keyboard=True))
    
operations = {
    '+': lambda x, y: x + y,
    '-': lambda x, y: x - y,
    '*': lambda x, y: x * y,
    '/': lambda x, y: x / y
}    
    
def calculate2(bot, update, user_data):
    #print(update.message.text)
    if not user_data.get('first_arg'):
        user_data['first_arg'] = update.message.text
        #print(user_data['first_arg'])
        reply_keyboard = ['+', '-', '*', '/']
        update.message.reply_text('Выбери операцию', reply_markup=ReplyKeyboardMarkup([reply_keyboard], resize_keyboard=True))
    elif not user_data.get('second_arg'):
        user_data['second_arg'] = update.message.text
        #print("{} {} {}".format(user_data['first_arg'], user_data['op_arg'], user_data['second_arg']))
        sum = operations[user_data['op_arg']](int(user_data['first_arg']), int(user_data['second_arg']))
        update.message.reply_text('Summary {} {} {} = {}'.format(user_data['first_arg'], user_data['op_arg'], user_data['second_arg'], sum))
        user_data['first_arg'] = None
        user_data['second_arg'] = None
        user_data['op_arg'] = None
        reply_to_start_command(bot, update, user_data)
    
    
def change_avatar_step1(bot, update, user_data):
    reply_keyboard = []
    for index, ava in enumerate(avatars):
        button = "/avatar {} {}".format(index, ava)
        button = emojize(button, use_aliases=True)
        reply_keyboard.append(button)
    update.message.reply_text('Выбери аватарку', reply_markup=ReplyKeyboardMarkup([reply_keyboard], resize_keyboard=True))
    
def change_avatar_step2(bot, update, args, user_data):
    user = get_user(update.effective_user, user_data)
    #print(args)
    try:
        ava = avatars[int(args[0])]
        #print(emojize(ava, use_aliases=True))
        #user_data['avatar'] = emojize(ava, use_aliases=True)
        user.avatar = ava
        db_session.commit()
        #user_data['avatar'] = emojize(ava, use_aliases=True)
        update.message.reply_text('Аватарка изменена', reply_markup=ReplyKeyboardMarkup(get_keyboard(), resize_keyboard=True))
    except:
        update.message.reply_text('Неверная аватарка')
        
def get_contact(bot, update, user_data):
    user = get_user(update.effective_user, user_data)
    user.phone = update.message.phone_number
    db_session.commit()
    update.message.reply_text('Спасибо {}'.format(get_avatar(user_data)))
    
def my_location(bot, update, user_data):
    user = get_user(update.effective_user, user_data)
    print(update.message.location)
    update.message.reply_text('Спасибо {}'.format(get_avatar(user_data)))
    
def check_cat(bot, update):
    update.message.reply_text("Обрабатываю фото")
    photo_file = bot.getFile(update.message.photo[-1].file_id)
    filename = os.path.join('downloads', '{}.jpg'.format(photo_file.file_id))
    photo_file.download(filename)
    if img_has_cat(filename):
        update.message.reply_text("Добавляю кошку в библиотеку.")
        new_filename = os.path.join('cats', '{}.jpg'.format(photo_file.file_id))
        os.rename(filename, new_filename)
    else:
        os.remove(filename)
        update.message.reply_text("Тревога, кошка не обнаружена!")
        
def get_weather(bot, update):
    try:
        city = update.message.text.split(' ')[1]
    except:
        city = 'Vladivostok,ru'
    
    try:
        if update.message.text.split(' ')[2] == 'предсказание':
            forcast = True
    except:
        forcast = False
        
    weather = get_wather_for_city(city, forcast)
    if not weather:
        update.message.reply_text('Неверно указан город \"{}\". Нужный формат \"Vladivostok,ru\"'.format(city))
        return False
    
    if forcast:
        text = weather['city']['name']
        for hour in weather['list']:
            text = text + '{} temp:{}'.format(hour['dt_txt'], hour['main']['temp'])
    else:
        if weather:
            text = "{} {} degrees. ".format(city.split(',')[0], weather['main']['temp_max'])
    update.message.reply_text(text)
    
#def start_anketa(bot, update, user_data):
#    update.message.reply_text('afas', reply_markup=ReplyDeyboardRe)
#    return name
    
#def get_name(bot, pdate,user_data):

def start_bot():
    my_bot = Updater(settings.id_bot)
    
    dp = my_bot.dispatcher

    dp.add_handler(CommandHandler("start", reply_to_start_command, pass_user_data=True))
    dp.add_handler(CommandHandler("count_words", count_words, pass_args=True, pass_user_data=True))
    dp.add_handler(CommandHandler("joke", tell_joke, pass_user_data=True))
    dp.add_handler(CommandHandler("cat", send_cat, pass_user_data=True))
    
    dp.add_handler(RegexHandler("Калькулятор",calculate1, pass_user_data=True))
    dp.add_handler(RegexHandler("^([0-9])$", calculate2, pass_user_data=True))
    dp.add_handler(RegexHandler("^([+,\-,*,/])$", calculate1, pass_user_data=True))
    
    dp.add_handler(RegexHandler("^(Прислать котика)$", send_cat, pass_user_data=True))#обработка по регулярке (кнопки)
    dp.add_handler(RegexHandler("^(Пошутить)$", tell_joke, pass_user_data=True))
    dp.add_handler(RegexHandler("^(Сменить аватарку)$", change_avatar_step1, pass_user_data=True))
    dp.add_handler(RegexHandler("^(Погода)", get_weather))
    
    dp.add_handler(CommandHandler("avatar", change_avatar_step2, pass_args=True, pass_user_data=True))
    
    dp.add_handler(MessageHandler(Filters.text, chat_with_user, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.contact, get_contact, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.location, my_location, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.photo, check_cat))
    
    my_bot.start_polling()
    my_bot.idle()

if __name__ == "__main__":
    start_bot()
    
    #sqlalchemy