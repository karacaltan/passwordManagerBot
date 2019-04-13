# passwordManagerBot
Telegram bot which manages your passwords. In Telegram you can find this bot as `@passwordManagerBot`.

### Usage
You can control the bot by chatting with it. The bot understands five commands. To start the conversation enter the command `/start`.
It is possible to create, change and delete a password. Please be aware, that this bot has been developed for **demonstration** purposes only.
All passwords are fictitious. So do not enter your **real** passwords!


### Forking

It is necessary to create a custom authorization token.
You can get one by chatting with the `@BotFather`. Save your token in a python file called `api_key.py` as a global variable.

    API_KEY = 'your api key'

It is recommended to use a virtual environment. First install virtualenv.

    pip install virtualenv

Create and activate the virtual environment

    python -m virtualenv env
    source env/bin/activate

Install dependencies

    pip install -r requirements.txt

Run `bot.py` and start Telegram.

### Reset
Deactivate and remove the virtual environment

    deactivate
    rm -rf env

### License

© Altan Mehmet Karacan

Licensed under the [MIT LICENSE](LICENSE).


