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
    settings['users']['authorized']     = []
    settings['users']['member']         = []
    settings['users']['s-authorized']   = [] # compatability. do not use
    settings['group']                   = dict()
    settings['group']['authorized']     = []
    settings['group']['member']         = []
    settings['group']['s-authorized']   = [] # compatability. do not use
    settings['gname']                   = dict()
    settings['gname']['authorized']     = []
    settings['gname']['member']         = []
    settings['gname']['s-authorized']   = [] # compatability. do not use
    settings['prefix']                  = []
    settings['channel']                 = dict()
    settings['channel']['boss']         = []
    settings['channel']['management']   = []
    settings['region']                  = dict()
    settings['region']['default']       = ''
    settings['role']                    = dict()
    settings['role']['boss']            = []
    talt_temporary                      = dict()
    talt_temporary_actual               = dict()
    talt_level                          = []
    talt_level.append(0)
    talt_level.append(0)            # 1
    talt_level.append(50)           # 2
    talt_level.append(125)          # 3
    talt_level.append(250)          # 4
    talt_level.append(450)          # 5
    talt_level.append(886)          # 6
    talt_level.append(1598)         # 7
    talt_level.append(2907)         # 8
    talt_level.append(4786)         # 9
    talt_level.append(7483)         # 10
    talt_level.append(11353)        # 11
    talt_level.append(16907)        # 12
    talt_level.append(24876)        # 13
    talt_level.append(36313)        # 14
    talt_level.append(52726)        # 15
    talt_level.append(160712)       # 16
    talt_level.append(345531)       # 17
    talt_level.append(742891)       # 18
    talt_level.append(1597216)      # 19
    talt_level.append(3434015)      # 20
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
            if user in self.settings[utype]['authorized']:
                self.settings[utype]['authorized'].remove(user)
            if user in self.settings[utype]['member']:
                self.settings[utype]['member'].remove(user)
            return True
        # special case: boss
        if role == "boss":
            return self.set_boss(user)

        if utype == "users" and role == "super authorized":
            if not user in self.settings[utype]['authorized']:
                self.settings[utype]['authorized'].append(user)
            if not user in self.settings[utype]['member']:
                self.settings[utype]['member'].append(user)
            if not user in self.settings[utype]['s-authorized']:
                self.settings[utype]['s-authorized'].append(user)
        elif role == "authorized":
            # users should not be allowed to modify super authorized
            if utype == "users" and user in self.settings[utype]['s-authorized']:
                return False
            if not user in self.settings[utype]['authorized']:
                self.settings[utype]['authorized'].append(user)
            if not user in self.settings[utype]['member']:
                self.settings[utype]['member'].append(user)
        else:
            # users should not be allowed to modify super authorized
            if user == "users" and user in self.settings[utype]['s-authorized']:
                return False
            if not user in self.settings[utype]['member']:
                self.settings[utype]['member'].append(user)
            if user in self.settings[utype]['authorized']:
                self.settings[utype]['authorized'].remove(user)
        if utype == "users":
            try:
                self.settings['talt'][user]
            except:
                self.settings['talt'][user] = 0
        self.save_file()
        return True

    def get_role(self, role="member"):
        if role == "boss":
            utype = "role"
        else:
            utype = "users"
        role_call = []
        role_call.extend(self.settings[utype][role])
        #role_call.extend(self.settings["group"][role])
        return role_call

    def get_role_user(self, user):
        if user in self.settings['users']['s-authorized']:
            return "super authorized"
        elif user in self.settings['users']['authorized']:
            return "authorized"
        elif user in self.settings['users']['member']:
            return "member"
        else:
            return None

    def get_role_group(self, roles):
        highest = "none"
        for role in roles:
            # groups cannot be super authorized
            if role in self.settings['group']['authorized']:
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
        return points > 0 and points % 20 == 0

    def set_remainder_talt(self, guild_level, points):
        guild_level = int(guild_level)
        points = int(points)
        if guild_level > len(self.talt_level) or guild_level < 1 or \
          points/20 > self.talt_level[guild_level+1] or not self.validate_points(points):
            print('what now')
            return False
        self.settings['guild_level'] = guild_level
        current_talt    = self.talt_level[guild_level] + points/20
        if current_talt < self.settings['talt']['guild']:
            return False
        self.settings['talt']['remainder']  = current_talt - self.settings['talt']['guild']
        self.settings['talt']['guild']  = current_talt
        self.rebase_guild_talt()
        self.save_file()
        return True

    def set_quota_talt(self, user, amount):
        if not auth_user in self.settings['users']['authorized'] or amount <= 0:
            return False
        self.settings['periodic_quota'] = amount
        self.save_file()
        return True

    def get_quota_talt(self):
        return self.settings['periodic_quota']

    def get_quota_talt_user(self, user, targets=None):
        if not auth_user in self.settings['users']['authorized'] and targets:
            return False
        if not targets:
            return [self.settings['quota'][user]]
        else:
            return [self.settings['quota'][target] for target in targets]

    def update_guild_talt(self, talt):
        self.settings['talt']['guild']  += talt
        while self.settings['talt']['guild'] >= self.talt_level[self.settings['guild_level']]:
            self.settings['guild_level'] += 1
        self.settings['guild_level'] -= 1
        self.save_file()
        return True

    def rebase_guild_talt(self):
        # reset
        self.settings['talt']['guild']  = 0
        self.settings['guild_level']    = 0
        self.save_file()
        talt = 0
        for key, value in self.settings['talt'].items():
            talt += value
        self.update_guild_talt(talt)
        return True

    def add_talt(self, user, amount, unit, target=None):
        amount  = int(amount)
        # if not user in self.settings['users']['s-authorized'] and \
        #   not user in self.settings['users']['authorized'] and \
        #   not user in self.settings['users']['member']:
        #     return False
        if unit != "Talt":
            divisor = 20
            if not self.validate_points(amount):
                return False
        else:
            divisor = 1
        talt_pt = amount/divisor
        if user in self.settings['users']['authorized'] or user in self.settings['users']['s-authorized']:
            if not target:
                self.update_guild_talt(talt_pt)
                try:
                    self.settings['talt'][user]     += talt_pt
                except:
                    self.settings['talt'][user]     = talt_pt
            else:
                self.update_guild_talt(talt_pt)
                try:
                    self.settings['talt'][target]   += talt_pt
                except:
                    self.settings['talt'][target]   = talt_pt
        else: #elif user in settings['users']['member']:
            self.talt_temporary[user]           = talt_pt
        self.save_file()
        return True

    def validate_talt(self, auth_user, mode, user=None):
        if not auth_user in self.settings['users']['authorized'] and \
           not auth_user in self.settings['users']['s-authorized']:
            return False
        elif not user:
            if mode == "validate":
                for user, talt_pt in self.talt_temporary.items():
                    self.settings['talt'][user] += talt_pt
                    self.talt_temporary[user]   = 0
                    self.update_guild_talt(talt_pt)
            else:
                self.talt_temporary = dict()
        else:
            if mode == "validate":
                self.settings['talt'][user] += self.talt_temporary[user]
                self.update_guild_talt(self.talt_temporary[user])
            talt_temporary[user] = 0
        self.save_file()
        return True

    def get_talt(self, user=None):
        if not user:
            return str(int(self.settings['talt']['guild']))
        else:
            try:
                return str(int(self.settings['talt'][user]))
            except:
                return str(0)

    def get_temp_talt(self):
        return self.talt_temporary

    def set_talt(self, user, amount, unit, target=None):
        amount  = int(amount)
        # if not user in self.settings['users']['s-authorized'] and \
        #   not user in self.settings['users']['authorized'] and \
        #   not user in self.settings['users']['member']:
        #     return False
        if unit != "Talt":
            divisor = 20
            if not self.validate_points(amount):
                return False
        else:
            divisor = 1
        talt_pt = amount/divisor
        if user in self.settings['users']['authorized'] or user in self.settings['users']['s-authorized']:
            if not target:
                self.update_guild_talt(talt_pt)
                self.settings['talt'][user]     = talt_pt
            else:
                self.update_guild_talt(talt_pt)
                self.settings['talt'][target]   = talt_pt
        else: #elif user in settings['users']['member']:
            self.talt_temporary_actual[user]    = talt_pt
        self.rebase_guild_talt()
        self.save_file()
        return True

    def reset_talt(self, user):
        self.settings['talt'][user] = 0
        self.rebase_guild_talt()
        return True

    def get_all_talt(self):
        return self.settings['talt']

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