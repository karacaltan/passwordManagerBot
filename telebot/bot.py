__author__ = 'Altan Mehmet Karacan'

import telepot
from telepot.loop import MessageLoop
from api_key import API_KEY
import json
import os
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton


class PasswordManagerBot:
    def __init__(self):
        self.password_list = []
        self.file = __file__
        self.bot = telepot.Bot(API_KEY)

    def get_passwords(self):
        main_path = os.path.dirname(self.file)
        with open(main_path + '/passwords.json') as json_file:
            data = json.load(json_file)
        passwords = data['passwords']
        self.password_list = passwords

    def parse_password(self, query_data):
        for i in range(len(self.password_list)):
            for key, value in self.password_list[i].iteritems():
                if query_data == key:
                    return value

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if msg['text'] == '/start':
            start_text = "{} {} {} {} {} {}".format('Hello my name is ', self.bot.getMe()['first_name'],
                                                    'and i am a bot to manage your passwords.'
                                                    '\n\nYou can control me by sending these commands:\n\n',
                                                    '/newpassword - save your password\n',
                                                    '/getpassword - get your password\n',
                                                    '/setpassword - set your password\n')
            self.bot.sendMessage(chat_id, start_text)
        elif msg['text'] == '/getpassword':
            self.get_passwords()
            keys = []
            for i in range(len(self.password_list)):
                for key, value in self.password_list[i].iteritems():
                    keys.append(str(key))
            if keys:
                inline_keyboard = []
                for key in keys:
                    inline_keyboard_button = InlineKeyboardButton(text=key, callback_data=key)
                    inline_keyboard.append(inline_keyboard_button)
                keyboard = InlineKeyboardMarkup(inline_keyboard=[inline_keyboard, ])
                self.bot.sendMessage(chat_id, 'Which password do you need?', reply_markup=keyboard)
            else:
                self.bot.sendMessage(chat_id, 'Currently there are no passwords.')
        elif msg['text'] == '/setpassword':
            self.bot.sendMessage(chat_id, 'Which password do you want to change?')
        else:
            self.bot.sendMessage(chat_id, "I couldn't understand this command. Type /start to see all commands.")

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        password = self.parse_password(query_data)
        self.bot.answerCallbackQuery(query_id, text='Got it')
        response = "{} {} {} {}".format("The username is", password['username'],
                                        "and the password is", password['password'])
        self.bot.sendMessage(from_id, response)


if __name__ == '__main__':
    pw_manager = PasswordManagerBot()
    MessageLoop(pw_manager.bot, {'chat': pw_manager.on_chat_message,
                                 'callback_query': pw_manager.on_callback_query}).run_as_thread()
