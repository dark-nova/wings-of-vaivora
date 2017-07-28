#vaivora_modules.settings
import json
import re
import os
import os.path
from itertools import chain

# import additional constants
from importlib import import_module as im
import vaivora_constants
for mod in vaivora_constants.modules:
    im(mod)
import vaivora_modules
for mod in vaivora_modules.modules:
    im(mod)

# BGN CONST

module_name     =   "settings"

command         =   []
example         =   "e.g."

mode_valid      =   "validate"
mode_invalid    =   "invalidate"

mode_promote    =   "promote"
mode_demote     =   "demote"

# BGN REGEX

rgx_help        =   re.compile(r'help', re.IGNORECASE)
rgx_setting     =   re.compile(r'(add|(un)?set|get)', re.IGNORECASE)
rgx_set_add     =   re.compile(r'add', re.IGNORECASE)
rgx_set_unset   =   re.compile(r'unset', re.IGNORECASE)
rgx_set_get     =   re.compile(r'get', re.IGNORECASE)
# rgx_set_set is unnecessary: process of elimination
rgx_rolechange  =   re.compile(r'(pro|de)mote', re.IGNORECASE)
rgx_promote     =   re.compile(r'pro', re.IGNORECASE) # only need to compare pro vs de
# rgx_demote is unnecessary: process of elimination
rgx_validation  =   re.compile(r'((in)?validate|(un)?verify)', re.IGNORECASE)
rgx_invalid     =   re.compile(r'[ui]n', re.IGNORECASE) # only need to check if un/in exists
# rgx_valid is unnecessary: process of elimination
rgx_roles       =   re.compile(r'(auth(orized)?|meme?ber|boss)', re.IGNORECASE)
rgx_ro_auth     =   re.compile(r'auth(orized)?', re.IGNORECASE)
rgx_ro_boss     =   re.compile(r'boss', re.IGNORECASE)
# rgx_ro_member is unnecessary: proccess of elimination
rgx_channel     =   re.compile(r'(m(ana)?ge?m(en)?t|boss)', re.IGNORECASE)
rgx_ch_boss     =   rgx_ro_boss # preserve uniformity
# rgx_ch_management is unnecessary: process of elimination

# END REGEX


arg_prefix      =   "[prefix]"
arg_prefix_alt  =   "\"$\", \"Vaivora, \""
arg_module      =   "[module]"
arg_cmd         =   module_name
arg_defcmd      =   "$" + module_name
arg_mention     =   "[@mention]"
arg_chan        =   "[#channel]"

arg_settings    =   "[settings]"

# options for argument 1
arg_opt_set     =   "[setting]" 
arg_opt_val     =   "[validation]"
arg_opt_rol     =   "[role change]"
arg_opt_all     =   ', '.join((arg_opt_set, arg_opt_val, arg_opt_rol, ))
arg_opt_opts    =   arg_settings + ":(" + arg_opt_all + ")"

# individual categories to describe for argument 1
#                   [settings]:[setting]
arg_cat_set     =   arg_settings + ":" + arg_opt_set
#                   [settings]:[validation]
arg_cat_val     =   arg_settings + ":" + arg_opt_val
#                   [settings]:[role change]
arg_cat_rol     =   arg_settings + ":" + arg_opt_rol

# options for each category, aggregate
#                   [setting]:(set, unset, get, add)
arg_set_cat     =   arg_opt_set + ":(set, unset, get, add)"
#                   [validation]:(verify|validate, unverify|invalidate)
arg_val_cat     =   arg_opt_val + ":(verify|validate, unverify|invalidate)"
#                   [role change]:(promote, demote)
arg_rol_cat     =   arg_opt_rol + ":(promote, demote)"

# options for each category, separate
#                   [setting]:set
arg_set_optA    =   arg_opt_set + ":set"
#                   [setting]:unset
arg_set_optB    =   arg_opt_set + ":unset"
#                   [setting]:get
arg_set_optC    =   arg_opt_set + ":get"
#                   [setting]:add
arg_set_optD    =   arg_opt_set + ":add"
#                   [validation]:(verify|validate)
arg_val_optA    =   arg_opt_val + ":(verify|validate)"
#                   [validation]:(unverify|invalidate)
arg_val_optB    =   arg_opt_val + ":(unverify|invalidate)"
#                   [role change]:promote
arg_rol_optA    =   arg_opt_rol + ":promote"
#                   [role change]:promote
arg_rol_optB    =   arg_opt_rol + ":demote"


# options for [setting], argument 2
arg_set_talt    =   "[talt]"
arg_set_role    =   "[role]"
arg_set_chan    =   "[channel]"
#                   [setting]:([talt], [role], [channel])
arg_set_all     =   arg_opt_set + ":(" + \
                    ', '.join((arg_set_talt, arg_set_role, arg_set_chan, )) + ")"

# options for [setting]:[talt]
arg_set_taltA   =   arg_set_talt + ":value"
arg_set_taltB   =   arg_set_talt + ":[unit]"

# options for [setting]:[role]
arg_set_role    =   arg_set_role + ":(authorized, member)"
arg_set_roleA   =   arg_set_role + ":authorized"
arg_set_roleB   =   arg_set_role + ":member"
arg_set_roleC   =   arg_set_role + ":boss"

# options for [setting]:[channel]
arg_set_chan    =   arg_set_chan + ":(management, boss)"
arg_set_chanA   =   arg_set_chan + ":management"
arg_set_chanB   =   arg_set_chan + ":boss"


# auxiliary arguments
arg_help        =   "help"
arg_arg         =   "Argument"
#                   $boss
arg_pre_cmd     =   arg_prefix + arg_cmd

# Do not adjust \
cmd_fragment    =   "```diff\n" + "- " + "[" + arg_defcmd + "] commands" + " -" + "\n" + \
                    "+ Usage" + "```"
command.append(cmd_fragment)

usage           =  "```ini\n"
# Do not adjust /
#                   $settings           [setting]           [talt: value]           [talt: unit]            [@mention]
usage           +=  arg_pre_cmd + " " + arg_opt_set + " " + arg_set_taltA   + " " + arg_set_taltB   + " " + arg_mention + "\n"
#                   $settings           [setting]           [role]                  [@mention]
usage           +=  arg_pre_cmd + " " + arg_opt_set + " " + arg_set_role    + " " + arg_mention + "\n"
#                   $settings           [setting]           [channel]               [#channel]
usage           +=  arg_pre_cmd + " " + arg_opt_set + " " + arg_set_chan    + " " + arg_chan    + "\n"
#                   $settings           [validation]
usage           +=  arg_pre_cmd + " " + arg_opt_val + "\n"
#                   $settings           [target: all]       [@mention]
usage           +=  arg_pre_cmd + " " + arg_opt_rol + " " + arg_mention + "\n"
# Do not adjust \
#                   $module             help
usage           +=  arg_pre_cmd + " " + arg_help + "\n"
usage           +=  "```"

cmd_fragment    =  usage
command.append(cmd_fragment)

acknowledge     =   "Thank you! Your command has been acknowledged and recorded.\n"
msg_help        =   "Please run `" + arg_defcmd + " help` for syntax.\n"
# Do not adjust /

# examples
cmd_fragment    =   "```diff\n" + "+ Examples\n" + "```"
command.append(cmd_fragment)

examples        =   "[$settings add talt 12]\n; adds 12 Talt to yourself\n" + \
                    "[$settings set talt 12]\n; sets your contribution to 12 Talt. Not the same as above.\n" + \
                    "[$settings add talt 240 points]\n; equivalent to first command\n" + \
                    "[$settings add talt 12 @mention]\n; adds 12 Talt to mentioned target(s)\n" + \
                    "[$settings set channel management #channel]\n; sets the channel(s) as management\n" + \
                    "[$settings set role authorized @mention]\n; changes the mentioned target(s) to \"authorized\"\n" + \
                    "[$settings promote @mention]\n; increases the mentioned target(s)'s role by one level, i.e. none -> member -> authorized\n" + \
                    "[$settings validate @mention]\n; validates the mentioned target(s)'s Talt contribution(s); omit mention to apply to all\n"

cmd_fragment    =  "```ini\n" + examples
cmd_fragment    += "```"
command.append(cmd_fragment)


# immutable
arg_info        =   list()
arg_info.append("```ini\n")
arg_info.append("Prefix=\"" +   arg_prefix +    "\": " + arg_prefix_alt + "\n" + \
                "; default: [$] or [Vaivora, ]\n" + \
                "This server may have others. Run [$settings get prefix] to check.\n")
arg_info.append("\n---\n\n")
arg_info.append("Module=\"" +   arg_module +    "\": '" + arg_cmd + "'\n" + \
                "; required\n" + \
                "(always) [" + arg_cmd + "]; goes after prefix. e.g. [$" + arg_cmd + "], [Vaivora, " + arg_cmd + "]\n")
arg_info.append("\n---\n\n")

# setting
arg_info.append("Argument=\"" + arg_set_cat + "\n" + \
                "Opt=\"" + arg_set_optA + "\":\n" + \
                "    Sets the attribute.\n" + \
                "Opt=\"" + arg_set_optB + "\":\n" + \
                "    Removes the attribute.\n" + \
                "Opt=\"" + arg_set_optC + "\":\n" + \
                "    Retrieves the attribute.\n" + \
                "Opt=\"" + arg_set_optD + "\":\n" + \
                "    [Talt-only] Adds the value of Talt.\n" + \
                "Some commands only take specific options, so check first.\n")
arg_info.append("\n---\n\n")

# role change
arg_info.append("Argument=\"" + arg_rol_cat + "\n" + \
                "Opt=\"" + arg_rol_optA + "\":\n" + \
                "    Raises the roles by one level. i.e. none to member, and member to authorized\n" + \
                "Opt=\"" + arg_rol_optB + "\":\n" + \
                "    Lowers the roles by one level. i.e. member to none, and authorized to member\n" + \
                "You must be of \"Authorized\" level.\n" + \
                "Mentions are required.\n")
arg_info.append("\n---\n\n")
arg_info.append("```")

# validation
arg_info.append("Argument=\"" + arg_val_cat + "\n" + \
                "Opt=\"" + arg_val_optA + "\":\n" + \
                "    Approves temporary records to be saved.\n" + \
                "Opt=\"" + arg_val_optB + "\":\n" + \
                "    Nulls temporary records.\n" + \
                "You must be of \"Authorized\" level.\n" + \
                "Mentions are optional. If absent, [validation] will apply to all.\n")
arg_info.append("\n---\n\n")
arg_info.append("```")


cmd_fragment    =   ''.join(arg_info)
command.append(cmd_fragment)

arg_info        =   list()
arg_info.append("```ini\n")


# setting: talt
arg_info.append("Argument=\"" + arg_set_talt + "\n" + \
                "Opt=\"" + arg_set_taltA + "\":\n" + \
                "    The amount to use.\n" + \
                "Opt=\"" + arg_set_taltB + "\":\n" + \
                "    The unit to use. Either \"talt\" or \"points\".\n" + \
                "; optional\n" + \
                "You must be of \"Member\" or higher level. If you are not \"Authorized\", your entries will be temporarily recorded.\n" + \
                "You will need to request an \"Authorized\" member for [validation].\n" + \
                "Mentions are optional. If absent, [talt] will apply to yourself.\n")
arg_info.append("\n---\n\n")


cmd_fragment    =   ''.join(arg_info)
command.append(cmd_fragment)

arg_info        =   list()
arg_info.append("```ini\n")


# setting: channel
arg_info.append("Argument=\"" + arg_set_chan + "\n" + \
                "Opt=\"" + arg_set_chanA + "\":\n" + \
                "    \"Management\" channel: once set, [settings] commands will cease to work in channels not marked \"Management\".\n" + \
                "Opt=\"" + arg_set_chanB + "\":\n" + \
                "    \"Boss\" channel: once set, [boss] commands will cease to work in channels not marked \"Boss\".\n" + \
                "You must be of \"Authorized\" level.\n" + \
                "Channel mentions are required.\n")
arg_info.append("\n---\n\n")


cmd_fragment    =   ''.join(arg_info)
command.append(cmd_fragment)

arg_info        =   list()
arg_info.append("```ini\n")


# setting: role
arg_info.append("Argument=\"" + arg_set_role + "\n" + \
                "Opt=\"" + arg_set_roleA + "\":\n" + \
                "    \"Member\" level member: can use Talt functions.\n" + \
                "Opt=\"" + arg_set_roleB + "\":\n" + \
                "    \"Authorized\" level member: can use all of [settings].\n" + \
                "Opt=\"" + arg_set_roleC + "\":\n" + \
                "    \"Boss\" level member: special role. Works with the [boss] module/command to mention all members of this role for boss alerts.\n" + \
                "You must be of \"Authorized\" level.\n" + \
                "Note: to change a user to \"None\" (lowest) role, you must use \"unset\".\n" + \
                "All server admins are \"Super Authorized\" by default. This cannot be changed. All permissions stem from server admins.\n" + \
                "Mentions are required.\n")
arg_info.append("\n---\n\n")

# help
arg_info.append("Argument=\"" + arg_help + "\"\n" + \
                "Prints this series of messages.\n")
arg_info.append("```")

cmd_fragment    =   ''.join(arg_info)
command.append(cmd_fragment)

# END CONST

class Settings:
    server_dir                          = "server_settings"

    settings                            = dict()
    settings['welcomed']                = False
    #settings['subscribed']              = True
    settings['vaivora-version']         = ''
    settings['talt']                    = dict()
    settings['talt']['guild']           = 0
    settings['talt']['remainder']       = 0
    settings['quota']                   = dict()
    settings['periodic_quota']          = 0
    settings['guild_level']             = 0
    settings['users']                   = dict()
    settings['users']['authorized']     = []
    settings['users']['member']         = []
    settings['users']['s-authorized']   = []
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

    def __init__(self, srv_id, srv_admin=None):
        if srv_admin:
            self.server_id      = srv_id
            self.server_file    = self.server_dir + "/" + self.server_id + ".json"
            self.check_file()
            self.settings = self.read_file()
            self.change_role(srv_admin, "users", role="super authorized")
            self.change_role(vaivora_modules.secrets.discord_user_id, "users", role="super authorized")
        else:
            self.server_id      = srv_id
            self.server_file    = self.server_dir + "/" + self.server_id + ".json"
            self.check_file()
            self.settings = self.read_file()

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

    def promote_demote(self, mode, users, groups):
        for user in users:
            self.get_highest_role_id(user)

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
        return self.role_level[self.get_role_user_id(user)]

    def get_role_user_id(self, user):
        if user in self.settings['users']['s-authorized']:
            return 3
        elif user in self.settings['users']['authorized']:
            return 2
        elif user in self.settings['users']['member']:
            return 1
        else:
            return 0

    def get_role_group(self, roles):
        highest = "none"
        for role in roles:
            # groups cannot be super authorized
            if role in self.settings['group']['authorized']:
                return "authorized"
            elif role in self.settings['group']['member']:
                highest = "member"
        return highest

    def get_highest_role(self, user, roles):
        return self.role_level[self.get_highest_role_id(user, roles)]

    def get_highest_role_id(self, user, roles):
        usr_role    =   self.role_level.index(self.get_role_user(user))
        grp_role    =   self.role_level.index(self.get_role_group(roles))
        return usr_role if usr_role > grp_role else grp_role

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
        if guild_level >= len(self.talt_level) or guild_level < 1 or \
          points/20 > self.talt_level[guild_level+1] or not self.validate_points(points):
            return False
        self.settings['guild_level'] = guild_level
        current_talt    = self.talt_level[guild_level] + points/20
        if current_talt < self.settings['talt']['guild']:
            return False
        self.settings['talt']['remainder']  = current_talt - self.settings['talt']['guild']
        self.settings['talt']['guild']  = current_talt
        self.save_file()
        self.rebase_guild_talt()
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
            if key == "guild":
                continue
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
                    self.settings['talt'][user]     +=  talt_pt
                except:
                    self.settings['talt'][user]     =   talt_pt
            else:
                self.update_guild_talt(talt_pt)
                try:
                    self.settings['talt'][target]   +=  talt_pt
                except:
                    self.settings['talt'][target]   =   talt_pt
        else: #elif user in settings['users']['member']:
            self.talt_temporary[user]           = talt_pt
        self.save_file()
        return True

    def validate_talt(self, auth_user, mode, user=None):
        if not auth_user in self.settings['users']['authorized'] and \
           not auth_user in self.settings['users']['s-authorized']:
            return False
        elif not user:
            if mode == mode_valid:
                for user, talt_pt in self.talt_temporary.items():
                    self.settings['talt'][user] += talt_pt
                    self.talt_temporary[user]   = 0
                    self.update_guild_talt(talt_pt)
            else:
                self.talt_temporary = dict()
        else:
            if mode == mode_valid:
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

    def was_welcomed(self):
        try:
            return self.settings['welcomed']
        except:
            self.settings['welcomed']   = False
            self.save_file()
            return False

    def greet(self, current_version):
        self.settings['welcomed']   =   True
        try:
            base_version    =   self.settings['vaivora-version']
        except:
            base_version    =   "[m]1.0"
        if not base_version:
            base_version    =   "[m]1.0"
        revs    =   vaivora_modules.version.check_revisions(base_version)
        if revs:
            self.settings['vaivora-version']    =   vaivora_modules.version.get_current_version()
        self.save_file()
        return revs

    # def subscribed(self):
    #     return self.settings['subscribed']

    # def set_subscription(self, flag):
    #     self.settings['subscribed'] =   flag
    #     self.save_file()
    #     return True

# @func:    process_command(str, list) : list
# @arg:
#       server_id : str
#           id of the server of the originating message
#       msg_channel : str
#           id of the channel of the originating message
#       settings_cmd : str
#           the command used, somewhat equivalent to arg_list[0] in $boss
#       cmd_user : str
#           the one who called the command
#       usr_roles : list(str)
#           the roles associated with the cmd_user
#       users : list(str)
#           list of users to be processed; can be None
#       groups : list(str)
#           list of roles to be processed; can be None 
# @return:
#       an appropriate message for success or fail of command
def process_command(server_id, msg_channel, settings_cmd, cmd_user, usr_roles, users, groups):
    fail    =   []
    cmd_srv =   Settings(server_id)
    mode    =   ""
    usr_rol =   cmd_srv.get_highest_role(cmd_user, usr_roles)

    # $boss help
    if rgx_help.match(settings_cmd):
        return command

    # setting (general)
    if rgx_setting.match(settings_cmd):
        return process_setting(server_id, msg_channel, settings_cmd, cmd_user, usr_rol, users, groups)

    # role change
    elif rgx_rolechange and usr_rol != "authorized" or usr_role != "super authorized":
        return ["Your command failed because your user level is too low. User level: `" + usr_rol + "`\n"]
    elif rgx_rolechange.match(settings_cmd) and rgx_promote.search(settings_cmd):
        return process_roles(server_id, msg_channel, mode=mode_promote, users, groups)
    elif rgx_rolechange.match(settings_cmd):
        return process_roles(server_id, msg_channel, mode=mode_demote, users, groups)

    # validation - handle after all commands are checked
    elif rgx_validation.match(settings_cmd) and rgx_invalid.search(settings_cmd):
        mode    =   mode_invalid
    elif rgx_validation.match(settings_cmd):
        mode    =   mode_valid 

    # did not match any settings or role change or validation
    else:
        return ["Your `$settings` command was not recognized. Please re-enter.\n" + msg_help]

    # check validation
    if rgx_validation.match(settings_cmd):
        if users or groups:
            # process one at a time
            for mention in chain(users, groups):
                if not cmd_srv.validate_talt(cmd_user, mode, user=mention):
                    fail.append(mention)
        else:
            if not cmd_srv.validate_talt(cmd_user, mode):
                return ["Your command failed because your user level is too low. User level: `" + usr_rol + "`\n"]
            else:
                return [acknowledge + "\n" + "Records have been " + mode + "d.\n"]
    if fail:
        return ["Your command partially or completely failed. " + \
                "Some of your mentions could not be processed:", "```diff\n- " + '\n- '.join(fail) + "```\n"]
    else:
        return [acknowledge + "\n" + "Records for the specified users and/or groups have been " + mode + "d.\n"]


# @func:    process_setting(str, list) : list
# @arg:
#       server_id : str
#           id of the server of the originating message
#       msg_channel : str
#           id of the channel of the originating message
#       arg_list : list
#           list of arguments supplied for the command
# @return:
#       an appropriate message for success or fail of command
def process_setting(server_id, msg_channel, arg_list):
    pass



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