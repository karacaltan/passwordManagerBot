import telepot
from telepot.loop import MessageLoop
from api_key import API_KEY
import json
bot = telepot.Bot(API_KEY)


def handle_message(msg):
    author_id = get_user(msg)
    msg = json.dumps(msg)
    msg_json = json.loads(msg)
    get_text = msg_json['text']
    bot.sendMessage(author_id, "{} {}".format('Thank you, I got your message:', get_text))


def get_user(message):
    message = json.dumps(message)
    message_json = json.loads(message)
    author_id = message_json['chat']['id']
    return author_id


MessageLoop(bot, handle_message).run_as_thread()
