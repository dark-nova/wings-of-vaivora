#vaivora_modules.settings
import json
import os
import os.path

# import additional constants
from importlib import import_module as im
import vaivora_constants
for mod in vaivora_constants.modules:
    im(mod)
import vaivora_modules.secrets

class Settings:
    server_dir                          = "server_settings"

    settings                            = dict()
    settings['talt']                    = dict()
    settings['talt']['guild']           = 0
    settings['talt']['remainder']       = 0
    settings['quota']                   = dict()
    settings['periodic_quota']          = 0
    settings['guild_level']             = 0
    settings['users']                   = dict()
    settings['users']['auth']           = []
    settings['users']['member']         = []
    settings['users']['s-auth']         = []
    settings['group']                   = dict()
    settings['group']['auth']           = []
    settings['group']['member']         = []
    settings['prefix']                  = []
    settings['channel']                 = dict()
    settings['channel']['boss']         = []
    settings['channel']['management']   = []
    settings['region']                  = dict()
    settings['region']['default']       = ''
    settings['role']                    = dict()
    settings['role']['boss']            = []
    talt_temporary                      = dict()
    talt_level                          = []
    talt_level.append(0)
    talt_level.append(0)
    talt_level.append(50)
    talt_level.append(125)
    talt_level.append(250)
    talt_level.append(450)
    talt_level.append(886)
    talt_level.append(1598)
    talt_level.append(2907)
    talt_level.append(4786)
    talt_level.append(7483)
    talt_level.append(11353)
    talt_level.append(16907)
    talt_level.append(24876)
    talt_level.append(36314)
    talt_level.append(52726)
    talt_level.append(160712)
    talt_level.append(345531)
    talt_level.append(742891)
    talt_level.append(1597216)
    talt_level.append(3434015)
    role_level                          = []
    role_level.append("none")
    role_level.append("member")
    role_level.append("authorized")
    role_level.append("super authorized")

    def __init__(self, srv_id, srv_admin):
        self.server_id      = srv_id
        self.server_file    = self.server_dir + "/" + self.server_id + ".json"
        self.check_file()
        self.settings = self.read_file()
        self.change_role(srv_admin, "users", role="super authorized")
        self.change_role(vaivora_modules.secrets.discord_user_id, "users", role="super authorized")

    def check_file(self):
        if not os.path.isdir(self.server_dir):
            os.mkdir(self.server_dir)
        if not os.path.isfile(self.server_file):
            self.init_file()
        else:
            try:
                self.read_file()
            except json.JSONDecodeError:
                self.init_file()

    def init_file(self):
        open(self.server_file, 'w').close()
        self.save_file()

    def read_file(self):
        with open(self.server_file, 'r') as sf:
            return json.load(sf)

    def save_file(self):
        with open(self.server_file, 'w') as sf:
            json.dump(self.settings, sf)

    def change_role(self, user, utype, role=None):
        if not role:
            if user in self.settings[utype]['auth']:
                self.settings[utype]['auth'].remove(user)
            if user in self.settings[utype]['member']:
                self.settings[utype]['member'].remove(user)
            return True
        # special case: boss
        if role == "boss":
            return self.set_boss(user)

        if role == "super authorized":
            if not user in self.settings[utype]['auth']:
                self.settings[utype]['auth'].append(user)
            if not user in self.settings[utype]['member']:
                self.settings[utype]['member'].append(user)
            if not user in self.settings[utype]['s-auth']:
                self.settings[utype]['s-auth'].append(user) 
        elif role == "authorized":
            # users should not be allowed to modify super authorized
            if user in self.settings['s-auth']:
                return False
            if not user in self.settings[utype]['auth']:
                self.settings[utype]['auth'].append(user)
            if not user in self.settings[utype]['member']:
                self.settings[utype]['member'].append(user)
        else:
            # users should not be allowed to modify super authorized
            if user in self.settings['s-auth']:
                return False
            if not user in self.settings[utype]['member']:
                self.settings[utype]['member'].append(user)
            if user in self.settings[utype]['auth']:
                self.settings[utype]['auth'].remove(user)
        if utype == "users":
            try:
                self.settings['talt'][user]
            except:
                self.settings['talt'][user] = 0
        self.save_file()
        return True

    def get_role(self, role="member"):
        role_call = []
        role_call.extend(self.settings["users"][role])
        role_call.extend(self.settings["group"][role])
        return role_call

    def get_role_user(self, user):
        if user in self.settings['users']['s-auth']:
            return "super authorized"
        elif user in self.settings['users']['auth']:
            return "authorized"
        elif user in self.settings['users']['member']:
            return "member"
        else:
            return None

    def get_role_group(self, roles):
        highest = "none"
        for role in roles:
            # groups cannot be super authorized
            if role in self.settings['group']['auth']:
                return "authorized"
            elif role in self.settings['group']['member']:
                highest = "member"
        return highest

    # def set_guild_talt(self, guild_level, points):
    #     if guild_level > len(talt_level) or guild_level < 1 or \
    #       points < 0 or points > talt_level[guild_level] or points % 20 != 0:
    #         return False
    #     self.settings['guild_level'] = guild_level
    #     self.settings['talt']['guild']  = talt_level[guild_level] + points/20
    #     self.save_file()
    #     return True

    def validate_points(self, points):
        return points < 0 or points % 20 != 0

    def set_remainder_talt(self, guild_level, points):
        if guild_level > len(self.talt_level) or guild_level < 1 or \
          points > self.talt_level[guild_level] or self.validate_points(points):
            return False
        self.settings['guild_level'] = guild_level
        current_talt    = self.talt_level[guild_level] + points/20
        if current_talt < self.settings['talt']['guild']:
            return False
        self.settings['talt']['remainder']  = current_talt - self.settings['talt']['guild']
        self.settings['talt']['guild']  = current_talt
        self.save_file()
        return True

    def set_quota_talt(self, user, amount):
        if not auth_user in settings['users']['auth'] or amount <= 0:
            return False
        self.settings['periodic_quota'] = amount
        self.save_file()
        return True

    def get_quota_talt(self):
        return self.settings['periodic_quota']

    def get_quota_talt_user(self, user, targets=None):
        if not auth_user in settings['users']['auth'] and targets:
            return False
        if not targets:
            return [self.settings['quota'][user]]
        else:
            return [self.settings['quota'][target] for target in targets]

    def update_guild_talt(self, talt):
        self.settings['talt']['guild']  += talt
        while self.settings['talt']['guild'] > self.talt_level[self.settings['guild_level']]:
            self.settings['guild_level'] += 1
        self.save_file()
        return True

    def add_talt(self, user, amount, unit, target=None):
        amount  = int(amount)
        if not user in self.settings['users']['s-auth'] and \
          not user in self.settings['users']['auth'] and \
          not user in self.settings['users']['member']:
            return False
        if unit != "Talt":
            divisor = 20
            if not self.validate_points(amount):
                return False
        else:
            divisor = 1
        talt_pt = amount/divisor
        if user in self.settings['users']['auth'] or user in self.settings['users']['s-auth']:
            if not target:
                self.update_guild_talt(talt_pt)
                self.settings['talt'][user]     += talt_pt
            else:
                self.update_guild_talt(talt_pt)
                self.settings['talt'][target]   += talt_pt
        else: #elif user in settings['users']['member']:
            self.talt_temporary[user]           = talt_pt
        self.save_file()
        return True

    def validate_talt(self, auth_user, users=None):
        if not auth_user in settings['users']['auth']:
            return False
        elif not users:
            for user, talt_pt in self.talt_temporary.values():
                self.settings['talt'][user] += talt_pt
                self.update_guild_talt(talt_pt)
        else:
            for user in users:
                self.settings['talt'][user] += self.talt_temporary[user]
                self.update_guild_talt(self.talt_temporary[user])
        self.save_file()
        return True

    def get_talt(self, user=None):
        if not user:
            return str(int(self.settings['talt']['guild']))
        else:
            try:
                return str(int(self.settings['talt'][user]))
            except:
                return 0

    def get_talt_for_nextlevel(self):
        if self.settings['guild_level'] == 20:
            return str(0)
        return str(int(self.talt_level[self.settings['guild_level']+1] - self.settings['talt']['guild']))

    def verify_channel(self, ch_type):
        return ch_type == "boss" or ch_type == "management"
        
    def set_channel(self, ch_type, channel, region=''):
        if self.verify_channel(ch_type):
            self.settings['channel'][ch_type].append(channel)
            self.save_file()
            return True
        else:
            return False

    def get_guild_level(self):
        return str(self.settings['guild_level'])

    def get_channel(self, ch_type):
        if self.verify_channel(ch_type):
            return self.settings['channel'][ch_type]
        else:
            return []

    def rm_channel(self, ch_type, channel):
        if self.verify_channel(ch_type):
            self.settings['channel'][ch_type].remove(channel)
            self.save_file()
            return True
        else:
            return False

    def get_prefix(self):
        return self.settings['prefix']

    def set_prefix(self, prefix):
        if prefix in self.settings['prefix']:
            return False
        self.settings['prefix'].append(prefix)
        self.save_file()
        return True

    def rm_prefix(self, prefix):
        try:
            self.settings['prefix'].remove(prefix)
            self.save_file()
            return True
        except:
            return False

    def set_boss(self, user):
        try:
            if user in self.settings['role']['boss']:
                return False
            self.settings['role']['boss'].append(user)
            self.save_file()
            return True
        except:
            return False

    def rm_boss(self, user):
        try:
            self.settings['role']['boss'].remove(user)
            self.save_file()
            return True
        except:
            return False

#### Examples
# $settings 
# $settings set role auth @mention...
# $settings get talt @mention @mention...
# $settings get talt
# $settings get role member
# $settings set channel boss #channel
# $settings rm channel boss
# $settings validate talt @mention...
# $settings set talt 1000 [talt, points] [user]