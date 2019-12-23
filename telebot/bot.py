__author__ = 'Altan Mehmet Karacan'

import telepot
from telepot.loop import MessageLoop
from telebot.api_key import API_KEY
import json
import os
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.user import User
import time


class PasswordManagerBot:
    def __init__(self):
        self.bot = telepot.Bot(API_KEY)
        self.current_user = None
        self.users = []

    def on_chat_message_(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        self.current_user = User(chat_id)
        user_exist = self.check_user(self.current_user.id)
        if user_exist:
            self.current_user = self.get_current_user(self.current_user.id)
        if msg['text'] == '/start':
            start_text = "{} {} {} {} {} {} {}".format('Hello my name is ', self.bot.getMe()['first_name'],
                                                       'and i am a bot to manage your passwords.'
                                                       '\n\nYou can control me by sending these commands:\n\n',
                                                       '/newpassword - save your password\n',
                                                       '/getpassword - get your password\n',
                                                       '/setpassword - set your password\n',
                                                       '/deletepassword - delete your password\n')
            if not self.users:
                self.users.append(self.current_user)
            else:
                for user in self.users:
                    if not user.id == self.current_user.id:
                        self.users.append(self.current_user)
            self.bot.sendMessage(self.current_user.id, start_text)
        elif msg['text'] == '/newpassword' and user_exist:
            self.create_password_list()
            self.current_user.state = 'NEWPASSWORD'
            self.bot.sendMessage(chat_id, 'First enter the name of the site')
        elif user_exist and self.current_user.state == 'NEWPASSWORD':
            if self.check_site(msg['text']) and not self.current_user.new_password_state:
                self.bot.sendMessage(self.current_user.id, 'This site already exist. Try another one.')
            elif not self.current_user.new_password_state and not self.current_user.succeed:
                self.current_user.site_name = msg['text']
                self.bot.sendMessage(self.current_user.id, 'Now enter the username.')
                self.current_user.new_password_state = True
            elif self.current_user.new_password_state:
                self.current_user.site_username = msg['text']
                self.bot.sendMessage(self.current_user.id, 'And finally the password.')
                self.current_user.new_password_state = False
                self.current_user.succeed = True
            elif self.current_user.succeed and not self.current_user.new_password_state:
                self.current_user.site_password = msg['text']
                self.add_password()
                self.bot.sendMessage(self.current_user.id, 'Cool! I have added your password!')
                self.current_user.state = ''
                self.current_user.succeed = False
        elif user_exist and msg['text'] == '/getpassword':
            keyboard = self.get_keyboard()
            if keyboard is not None:
                self.current_user.state = 'GETPASSWORD'
                self.bot.sendMessage(self.current_user.id, 'Which password do you need?', reply_markup=keyboard)
            else:
                self.bot.sendMessage(self.current_user.id, 'Currently there are no passwords.')
        elif user_exist and msg['text'] == '/setpassword':
            self.get_passwords()
            keyboard = self.get_keyboard()
            if keyboard is not None:
                self.current_user.state = 'SETPASSWORD'
                self.bot.sendMessage(self.current_user.id, 'Which password do you want to change?',
                                     reply_markup=keyboard)
            else:
                self.bot.sendMessage(self.current_user.id, 'Currently there are no passwords.')
        elif self.current_user.state == 'SETPASSWORD' and self.current_user.password_set:
            self.bot.sendMessage(self.current_user.id, 'Alright your password has been changed!')
            self.set_password((msg[content_type]))
            self.current_user.state = ''
            self.current_user.password_set = False
        elif user_exist and msg['text'] == '/deletepassword':
            keyboard = self.get_keyboard()
            if keyboard is not None:
                self.current_user.state = 'DELETEPASSWORD'
                self.bot.sendMessage(self.current_user.id,
                                     'Which password do you want to delete?', reply_markup=keyboard)
            else:
                self.bot.sendMessage(self.current_user.id, 'Currently there are no passwords.')
        else:
            self.bot.sendMessage(self.current_user.id,
                                 "I couldn't understand this command. Use /start to see all commands.")

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        self.current_user.query_data = query_data
        password = self.parse_password()
        self.bot.answerCallbackQuery(query_id, text='Got it')
        if self.current_user.state == 'GETPASSWORD':
            response = "{} {} {} {} {} {}".format('Your username for', query_data, 'is', password['username'],
                                                  'and the password is', password['password'])
            self.bot.sendMessage(from_id, response)
        elif self.current_user.state == 'SETPASSWORD':
            self.current_user.password_set = True
            self.bot.sendMessage(from_id, 'Please enter the new password')
        elif self.current_user.state == 'DELETEPASSWORD':
            new_dict = self.delete_site()
            self.write_to_file(new_dict)
            self.current_user.state = ''
            self.bot.sendMessage(self.current_user.id, "{} {} {}".format('Alright, the password for',
                                                                         self.current_user.query_data,
                                                                         'will be deleted'))

    def check_user(self, user_id):
        exist = False
        for user in self.users:
            if user.id == user_id:
                exist = True
        return exist

    def get_current_user(self, user_id):
        for user in self.users:
            if user.id == user_id:
                return user

    def create_password_list(self):
        default_passwords = {"passwords": []}
        if not os.path.exists(self.current_user.path):
            os.makedirs(self.current_user.path)
            self.write_to_file(default_passwords)

    def write_to_file(self, dictionary):
        try:
            with open(self.current_user.path + '/passwords.json', 'w') as json_file:
                json.dump(dictionary, json_file)
        except IOError as error:
            print("{} {}".format("Couldn't write to file", error))

    def get_passwords(self):
        try:
            passwords_path = "{}{}".format(self.current_user.path, '/passwords.json')
            with open(passwords_path) as json_file:
                data = json.load(json_file)
            passwords = data['passwords']
            self.current_user.password_list = passwords
        except IOError as error:
            print("{} {}".format("Couldn't open file", error))

    def check_site(self, site):
        exist = False
        for i in range(len(self.current_user.password_list)):
            if site in self.current_user.password_list[i]:
                exist = True
        return exist

    def add_password(self):
        passwords = {}
        site = {}
        site.update({self.current_user.site_name: {"username": self.current_user.site_username,
                                                   "password": self.current_user.site_password}})
        self.current_user.password_list.append(site)
        passwords.update({"passwords": self.current_user.password_list})
        self.write_to_file(passwords)

    def get_keyboard(self):
        keys = []
        keyboard = None
        for i in range(len(self.current_user.password_list)):
            for key, value in self.current_user.password_list[i].items():
                keys.append(str(key))
        if keys:
            inline_keyboard = []
            for key in keys:
                inline_keyboard_button = InlineKeyboardButton(text=key, callback_data=key)
                inline_keyboard.append(inline_keyboard_button)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[inline_keyboard, ])
        return keyboard

    def parse_password(self):
        for i in range(len(self.current_user.password_list)):
            for key, value in self.current_user.password_list[i].items():
                if self.current_user.query_data == key:
                    return value

    def set_password(self, new_password):
        d = {}
        for i in range(len(self.current_user.password_list)):
            for key, value in self.current_user.password_list[i].items():
                if self.current_user.query_data == key:
                    self.current_user.password_list[i][key]['password'] = new_password
        d.update({"passwords": self.current_user.password_list})
        self.write_to_file(d)

    def delete_site(self):
        password_list = []
        d = {}
        for i in range(len(self.current_user.password_list)):
            for key in self.current_user.password_list[i].keys():
                if key != self.current_user.query_data:
                    password_list.append(self.current_user.password_list[i])
        self.current_user.password_list = password_list
        d.update({"passwords": self.current_user.password_list})
        return d


if __name__ == '__main__':
    pw_manager = PasswordManagerBot()
    MessageLoop(pw_manager.bot, {'chat': pw_manager.on_chat_message_,
                                 'callback_query': pw_manager.on_callback_query}).run_as_thread()
    # Keep the program running.
    while 1:
        time.sleep(10)
