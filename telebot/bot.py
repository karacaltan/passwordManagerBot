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
        self.main_path = os.path.dirname(self.file)
        self.state = ''
        self.query_data = ''
        self.new_password = False
        self.succeed = False
        self.site_name = ''
        self.username = ''
        self.password = ''
        self.password_set = False

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if self.state == 'SETPASSWORD' and self.password_set:
            self.bot.sendMessage(chat_id, 'Alright your password has been changed!')
            self.set_password((msg[content_type]))
            self.state = ''
            self.password_set = False
        elif self.state == 'NEWPASSWORD':
            if self.exist(msg['text']) and not self.new_password:
                self.bot.sendMessage(chat_id, 'This site already exist. Try another one.')
            elif self.new_password:
                self.username = msg['text']
                self.bot.sendMessage(chat_id, 'And finally the password.')
                self.new_password = False
                self.succeed = True
            elif not self.new_password and not self.succeed:
                self.site_name = msg['text']
                self.bot.sendMessage(chat_id, 'Now type in the username.')
                self.new_password = True
            elif self.succeed and not self.new_password:
                self.password = msg['text']
                self.add_password()
                self.bot.sendMessage(chat_id, 'Cool! I have added your password!')
                self.state = ''
                self.succeed = False
        else:
            if msg['text'] == '/start':
                start_text = "{} {} {} {} {} {} {}".format('Hello my name is ', self.bot.getMe()['first_name'],
                                                           'and i am a bot to manage your passwords.' 
                                                           '\n\nYou can control me by sending these commands:\n\n',
                                                           '/newpassword - save your password\n',
                                                           '/getpassword - get your password\n',
                                                           '/setpassword - set your password\n',
                                                           '/deletepassword - delete your password\n')
                self.bot.sendMessage(chat_id, start_text)
            elif msg['text'] == '/getpassword':
                self.get_passwords()
                keyboard = self.get_keyboard()
                if keyboard is not None:
                    self.state = 'GETPASSWORD'
                    self.bot.sendMessage(chat_id, 'Which password do you need?', reply_markup=keyboard)
                else:
                    self.bot.sendMessage(chat_id, 'Currently there are no passwords.')
            elif msg['text'] == '/setpassword':
                self.get_passwords()
                keyboard = self.get_keyboard()
                if keyboard is not None:
                    self.state = 'SETPASSWORD'
                    self.bot.sendMessage(chat_id, 'Which password do you want to change?', reply_markup=keyboard)
                else:
                    self.bot.sendMessage(chat_id, 'Currently there are no passwords.')
            elif msg['text'] == '/newpassword':
                self.state = 'NEWPASSWORD'
                self.bot.sendMessage(chat_id, 'First type in the name of the site')
            elif msg['text'] == '/deletepassword':
                self.get_passwords()
                keyboard = self.get_keyboard()
                if keyboard is not None:
                    self.state = 'DELETEPASSWORD'
                    self.bot.sendMessage(chat_id, 'Which password do you want to delete?', reply_markup=keyboard)
                else:
                    self.bot.sendMessage(chat_id, 'Currently there are no passwords.')
            else:
                self.bot.sendMessage(chat_id, "I couldn't understand this command. Type /start to see all commands.")

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        password = self.parse_password(query_data)
        self.bot.answerCallbackQuery(query_id, text='Got it')
        if self.state == 'GETPASSWORD':
            response = "{} {} {} {} {} {}".format('Your username for', query_data, 'is', password['username'],
                                                  'and the password is', password['password'])
            self.bot.sendMessage(from_id, response)
        elif self.state == 'DELETEPASSWORD':
            self.query_data = query_data
            new_dict = self.delete_dict()
            self.write_to_file(new_dict)
            self.state = ''
            self.bot.sendMessage(from_id, "{} {} {}".format('Alright, the password for',
                                                            self.query_data, 'will be deleted'))
        elif self.state == 'SETPASSWORD':
            self.password_set = True
            self.bot.sendMessage(from_id, 'Please type in the new password')
            self.query_data = str(query_data)

    def get_passwords(self):
        try:
            with open(self.main_path + '/passwords.json') as json_file:
                data = json.load(json_file)
            passwords = data['passwords']
            self.password_list = passwords
        except IOError as error:
            print("{} {}".format("Couldn't open file", error))

    def parse_password(self, query_data):
        for i in range(len(self.password_list)):
            for key, value in self.password_list[i].iteritems():
                if query_data == key:
                    return value

    def write_to_file(self, dictionary):
        try:
            with open(self.main_path + '/passwords.json', 'w') as json_file:
                json.dump(dictionary, json_file)
        except IOError as error:
            print("{} {}".format("Couldn't write to file", error))

    def exist(self, site):
        exist = False
        self.get_passwords()
        for i in range(len(self.password_list)):
            if site in self.password_list[i]:
                exist = True
        return exist

    def add_password(self):
        passwords = {}
        site = {}
        site.update({self.site_name: {"username": self.username, "password": self.password}})
        self.get_passwords()
        self.password_list.append(site)
        passwords.update({"passwords": self.password_list})
        self.write_to_file(passwords)

    def get_keyboard(self):
        keys = []
        keyboard = None
        for i in range(len(self.password_list)):
            for key, value in self.password_list[i].iteritems():
                keys.append(str(key))
        if keys:
            inline_keyboard = []
            for key in keys:
                inline_keyboard_button = InlineKeyboardButton(text=key, callback_data=key)
                inline_keyboard.append(inline_keyboard_button)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[inline_keyboard, ])
        return keyboard

    def set_password(self, new_password):
        d = {}
        self.get_passwords()
        for i in range(len(self.password_list)):
            for key, value in self.password_list[i].items():
                if self.query_data == key:
                    self.password_list[i][key]['password'] = new_password
        d.update({"passwords": self.password_list})
        self.write_to_file(d)

    def delete_dict(self):
        self.get_passwords()
        password_list = []
        d = {}
        for i in range(len(self.password_list)):
            for key in self.password_list[i].iterkeys():
                if key != self.query_data:
                    password_list.append(self.password_list[i])
        self.password_list = password_list
        d.update({"passwords": self.password_list})
        return d


if __name__ == '__main__':
    pw_manager = PasswordManagerBot()
    MessageLoop(pw_manager.bot, {'chat': pw_manager.on_chat_message,
                                 'callback_query': pw_manager.on_callback_query}).run_as_thread()
