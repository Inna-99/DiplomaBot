import gettext

import telebot
from telebot.types import Message

import config
from utils import messages
from utils.db import DataBase

bot = telebot.TeleBot(config.TOKEN)


def translate(func):
    def wrapper(call):
        chat_id = (
            call.chat.id if isinstance(call, Message) else call.message.chat.id
        )
        lang = (db.select_language(chat_id) or
                config.DEFAULT_LANGUAGE)
        lang = gettext.translation('messages', localedir='locale',
                                   languages=[lang])
        lang.install()
        func(call, lang.gettext)
    return wrapper


@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    btn_en = telebot.types.InlineKeyboardButton(text='English',
                                                callback_data='en')
    btn_ru = telebot.types.InlineKeyboardButton(text='Русский',
                                                callback_data='ru')
    btn_zh = telebot.types.InlineKeyboardButton(text='中國人',
                                                callback_data='zh')
    keyboard.add(btn_ru, btn_en, btn_zh)
    bot.send_message(message.chat.id, messages.START_MESSAGE,
                     parse_mode='HTML',
                     reply_markup=keyboard)


@bot.message_handler(commands=['help'])
@translate
def send_welcome(message, locale):
    _ = locale
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    for index, question in enumerate(messages.QUESTIONS_AND_ANSWERS.keys()):
        keyboard.add(
            telebot.types.InlineKeyboardButton(text=_(question),
                                               callback_data=str(index))
        )

    bot.send_message(message.chat.id,
                     _(messages.HELP_MESSAGE),
                     parse_mode='HTML',
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in ('en', 'ru', 'zh'))
def callback_worker_en(call):
    def func(call, locale):
        _ = locale
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        for index, question in enumerate(messages.QUESTIONS_AND_ANSWERS.keys()):
            if lang in messages.QUESTIONS_AND_ANSWERS[question]['lang']:
                keyboard.add(
                    telebot.types.InlineKeyboardButton(
                        text=_(question),
                        callback_data=str(index))
                )

        bot.send_message(call.message.chat.id,
                         _(messages.LANGUAGE_MESSAGE),
                         parse_mode='HTML')
        bot.send_message(call.message.chat.id,
                         _(messages.HELP_MESSAGE),
                         parse_mode='HTML',
                         reply_markup=keyboard)
    lang = call.data
    db.insert_language(call.message.chat.id, lang)

    translate(func)(call)


@bot.callback_query_handler(
    func=lambda call:
    call.data in map(str, range(0, len(messages.QUESTIONS_AND_ANSWERS.keys())))
)
@translate
def callback_worker_answer(call, locale):
    _ = locale
    message = list(messages.QUESTIONS_AND_ANSWERS.items())[int(call.data)]
    bot.send_message(call.message.chat.id,
                     "<b>" + _(message[0]) + "</b>\n\n"
                     + _(message[1]["message"]),
                     parse_mode='HTML')


db = DataBase()
try:
    bot.polling()
except KeyboardInterrupt:
    db.close()
