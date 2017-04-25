#vaivora_modules.settings
import json
import os

# import additional constants
from importlib import import_module as im
import vaivora_constants
for mod in vaivora_constants.modules:
    im(mod)

class Settings:
    server_dir              = "server_settings"

    settings                = dict()
    settings['talt']        = dict()
    settings['talt']['guild']   = 0
    settings['guild_level'] = 0
    settings['users']       = dict()
    settings['users']['auth']   = []
    settings['users']['member'] = []
    settings['prefix']      = []
    settings['channel']     = dict()
    settings['channel']['boss'] = None
    settings['channel']['management']   = None
    talt_temporary          = dict()
    talt_level              = []
    talt_level[0]           = 0
    talt_level[1]           = 0
    talt_level[2]           = 50
    talt_level[3]           = 125
    talt_level[4]           = 250
    talt_level[5]           = 450
    talt_level[6]           = 886
    talt_level[7]           = 1598
    talt_level[8]           = 2907
    talt_level[9]           = 4786
    talt_level[10]          = 7483
    talt_level[11]          = 11353
    talt_level[12]          = 16907
    talt_level[13]          = 24876
    talt_level[14]          = 36314
    talt_level[15]          = 52726
    talt_level[16]          = 160712
    talt_level[17]          = 345531
    talt_level[18]          = 742891
    talt_level[19]          = 1597216
    talt_level[20]          = 3434015

    def __init__(self, srv_id, srv_admin):
        self.server_id      = srv_id
        self.server_file    = server_dir + "/" + self.server_id + ".json"
        self.settings['users']['auth'].append(srv_admin)
        self.check_file()
        self.settings = self.read_file()

    def check_file(self):
        if not os.is_dir(server_dir):
            os.mkdir(server_dir)
        if not os.is_file(srv):
            self.init_file()
        else:
            try:
                self.read_file()
            except json.JSONDecodeError:
                self.init_file()

    def init_file(self):
        open(server_file, 'w').close()
        self.save_file()

    def read_file(self):
        return json.load(self.server_file)

    def save_file(self):
        json.dump(self.settings, self.server_file)

    def change_user(self, user, role=None):
        if not role:
            if user in settings['users']['auth']:
                settings['users']['auth'].remove(user)
            if user in settings['users']['member']:
                settings['users']['member'].remove(user)
        elif role == "Authorized":
            settings['users']['auth'].append(user)
            try:
                settings['talt'][user]
            except:
                settings['talt'][user] = 0
            if user in settings['users']['member']:
                settings['users']['member'].remove(user)
        else:
            settings['users']['member'].append(user)
            try:
                settings['talt'][user]



    def get_user(self, user):
        pass

    def add_talt(self, user, amount, unit):
        divisor = 1 if unit == "Talt" else 20
        talt_pt = amount/divisor
        if user in settings['users']['auth']:
            settings['talt']['guild']   += talt_pt
            settings['talt'][user]      += talt_pt


    def validate_talt(self, auth_user, users):
        pass

    def get_talt(self, user=None):
        pass

    def get_talt_for_nextlevel(self):
        pass
