import os


class User:
    def __init__(self, chat_id):
        self.id = chat_id
        self.password_list = []
        self.state = ''
        self.query_data = ''
        self.new_password_state = False
        self.succeed = False
        self.site_name = ''
        self.site_username = ''
        self.site_password = ''
        self.password_set = False
        self.file = __file__
        self.main_path = os.path.dirname(self.file)
        self.path = "{}{}{}".format(self.main_path, '/users/', self.id)
