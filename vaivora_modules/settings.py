#vaivora_modules.settings
import json
import re
import os
import os.path
from itertools import chain

# import additional constants
from importlib import import_module as im
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

mode_talt       =   "Talt"
mode_channel    =   "Channel"
mode_role       =   "Role"

unit_talt       =   "Talt"
unit_point      =   "Points"

valid_ch        =   "`management`, `boss`"

role_boss       =   "boss"
role_none       =   "none"
role_member     =   "member"
role_auth       =   "authorized"
role_sauth      =   "super authorized"

msg_records     =   "Here are the records you have requested:\n"
msg_perms       =   "Your command failed because your user level is too low. User level: `"
msg_fails       =   "Your command could not be completely parsed.\n"

role_idx        =    dict()
role_idx[role_none]     =   0
role_idx[role_member]   =   1
role_idx[role_boss]     =   1
role_idx[role_auth]     =   2
role_idx[role_sauth]    =   3

channel_boss    =   "boss"
channel_mgmt    =   "management"

# BGN REGEX

rgx_help        =   re.compile(r'help', re.IGNORECASE)
rgx_setting     =   re.compile(r'(add|(un)?set|get)', re.IGNORECASE)
rgx_kw_all      =   re.compile(r'all', re.IGNORECASE)
rgx_set_add     =   re.compile(r'add', re.IGNORECASE)
rgx_set_unset   =   re.compile(r'unset', re.IGNORECASE)
rgx_set_get     =   re.compile(r'get', re.IGNORECASE)
rgx_set_talt    =   re.compile(r'[1-9][0-9]*')
rgx_set_unit    =   re.compile(r'(talt|point)s?', re.IGNORECASE)
rgx_set_unit_t  =   re.compile(r'talts?', re.IGNORECASE)
rgx_set_unit_p  =   re.compile(r'p(oin)?ts?', re.IGNORECASE)
rgx_set_chan    =   re.compile(r'ch(an(nel)*)?', re.IGNORECASE)
rgx_set_role    =   re.compile(r'role', re.IGNORECASE)
rgx_set_set     =   re.compile(r'set', re.IGNORECASE)
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
rgx_set_guild   =   re.compile(r'guild', re.IGNORECASE)
rgx_gd_levels   =   re.compile(r'[12]?[0-9]')
rgx_gd_points   =   re.compile(r'[1-3]?[0-9]{1,6}')
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
    settings['users'][role_auth]        = []
    settings['users'][role_member]      = []
    settings['users']['s-authorized']   = []
    settings['group']                   = dict()
    settings['group'][role_auth]        = []
    settings['group'][role_member]      = []
    settings['group']['s-authorized']   = [] # compatability. do not use
    settings['gname']                   = dict()
    settings['gname'][role_auth]        = []
    settings['gname'][role_member]      = []
    settings['gname']['s-authorized']   = [] # compatability. do not use
    settings['prefix']                  = []
    settings['channel']                 = dict()
    settings['channel'][channel_boss]   = []
    settings['channel'][channel_mgmt]   = []
    settings['region']                  = dict()
    settings['region']['default']       = ''
    settings['role']                    = dict()
    settings['role'][role_boss]         = []
    talt_temporary                      = dict()
    talt_temporary_actual               = dict()
    settings['lock']                    = False
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
    role_level.append(role_none)
    role_level.append(role_member)
    role_level.append(role_auth)
    role_level.append(role_sauth)

    def __init__(self, srv_id, srv_admin=None):
        if srv_admin:
            self.server_id      = srv_id
            self.server_file    = self.server_dir + "/" + self.server_id + ".json"
            self.check_file()
            self.set_role(srv_admin, "users", role=role_sauth)
            self.set_role(vaivora_modules.secrets.discord_user_id, "users", role=role_sauth)
            self.toggle_lock(False)
        else:
            self.server_id      = srv_id
            self.server_file    = self.server_dir + "/" + self.server_id + ".json"
            self.check_file()

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
            self.settings = json.load(sf)

    def save_file(self):
        with open(self.server_file, 'w') as sf:
            json.dump(self.settings, sf)

    def set_role(self, user, utype, role=None):
        # unset
        if not role or role == role_none:
            if user in self.settings[utype]['s-authorized']:
                return False
            if user in self.settings[utype][role_auth]:
                self.settings[utype][role_auth].remove(user)
            if user in self.settings[utype][role_member]:
                self.settings[utype][role_member].remove(user)
            return True

        # special case: boss
        if role == role_boss:
            return self.set_boss(user, utype)

        # this should NEVER be called by users!
        if utype == "users" and role == role_sauth:
            if not user in self.settings[utype][role_auth]:
                self.settings[utype][role_auth].append(user)
            if not user in self.settings[utype][role_member]:
                self.settings[utype][role_member].append(user)
            if not user in self.settings[utype]['s-authorized']:
                self.settings[utype]['s-authorized'].append(user)

        # only super authorized should be able to change this from the start, to relegate permissions
        elif role == role_auth:
            # users should not be allowed to modify super authorized
            if utype == "users" and user in self.settings[utype]['s-authorized']:
                return False
            if not user in self.settings[utype][role_auth]:
                self.settings[utype][role_auth].append(user)
            if not user in self.settings[utype][role_member]:
                self.settings[utype][role_member].append(user)

        # role member
        else:
            # users should not be allowed to modify super authorized
            if user == "users" and user in self.settings[utype]['s-authorized']:
                return False
            if not user in self.settings[utype][role_member]:
                self.settings[utype][role_member].append(user)
            if user in self.settings[utype][role_auth]:
                self.settings[utype][role_auth].remove(user)

        # optionally add a talt count to them as well if it doesn't exist already
        if utype == "users":
            try:
                self.settings['talt'][user]
            except:
                self.settings['talt'][user] = 0
        self.save_file()
        return True

    def is_role_boss(self, user):
        return user in self.settings['role'][role_boss]

    def promote_demote(self, mode, users, groups):
        failed  =   []
        for utype, user in chain(users, groups):
            tg_role     =   self.get_role_user_id(user)
            # cannot promote (super) authorized or demote none
            if tg_role <= 2 and mode == mode_promote or \
               tg_role == 0 and mode == mode_demote:
                failed.append((user, "of role " + self.role_level[tg_role] + ", cannot " + mode, "@" if utype == "users" else "&"))
            # member to authorized
            elif tg_role == 2 and mode == mode_demote:
                self.settings[utype][role_auth].remove(user)
            elif tg_role == 1 and mode == mode_promote:
                self.settings[utype][role_auth].append(user)
            elif tg_role == 1 and mode == mode_demote:
                self.settings[utype][role_member].remove(user)
            elif tg_role == 0 and mode == mode_promote:
                self.settings[utype][role_member].append(user)
        self.save_file()
        return failed

    def get_role(self, role=role_member):
        role_call = []
        if role == "boss":
            return self.settings['role'][role]

        role_call.extend(self.settings["group"][role])
        role_call.extend(self.settings["users"][role])
        return role_call

    def get_role_user(self, user):
        return self.role_level[self.get_role_user_id(user)]

    def get_role_user_id(self, user):
        if user in self.settings['users']['s-authorized']:
            return 3
        elif user in self.settings['users'][role_auth]:
            return 2
        elif user in self.settings['users'][role_member]:
            return 1
        else:
            return 0

    def get_role_group(self, roles):
        return self.role_level[self.get_role_group_id(roles)]

    def get_role_group_id(self, roles):
        highest = 0
        for role in roles:
            # groups cannot be super authorized
            if role in self.settings['group'][role_auth]:
                return 2
            elif role in self.settings['group'][role_member]:
                highest = 1
        return highest

    def get_highest_role(self, user, roles):
        return self.role_level[self.get_highest_role_id(user, roles)]

    def get_highest_role_id(self, user, roles):
        usr_role    =   self.get_role_user_id(user)
        grp_role    =   self.get_role_group_id(roles)
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
           points/20 > self.talt_level[guild_level+1] or not self.validate_points(points) or \
           points/20 == self.settings['talt']['guild']:
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
        if not auth_user in self.settings['users'][role_auth] or amount <= 0:
            return False
        self.settings['periodic_quota'] = amount
        self.save_file()
        return True

    def get_quota_talt(self):
        return self.settings['periodic_quota']

    def get_quota_talt_user(self, user, targets=None):
        if not auth_user in self.settings['users'][role_auth] and targets:
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
        talt = 0
        for key, value in self.settings['talt'].items():
            if key == "guild":
                continue
            talt += int(value)
        self.update_guild_talt(talt)
        return True

    def add_talt(self, user, amount, unit, target=None):
        amount  = int(amount)
        # if not user in self.settings['users']['s-authorized'] and \
        #   not user in self.settings['users'][role_auth] and \
        #   not user in self.settings['users'][role_member]:
        #     return False
        if unit != "Talt":
            divisor = 20
            if not self.validate_points(amount):
                return False
        else:
            divisor = 1
        talt_pt = amount/divisor
        if user in self.settings['users'][role_auth] or user in self.settings['users']['s-authorized']:
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
        else: #elif user in settings['users'][role_member]:
            self.talt_temporary[user]           = talt_pt
        self.save_file()
        return True

    def validate_talt(self, auth_user, mode, user=None):
        if not auth_user in self.settings['users'][role_auth] and \
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
        #   not user in self.settings['users'][role_auth] and \
        #   not user in self.settings['users'][role_member]:
        #     return False
        if unit != unit_talt:
            divisor = 20
            if not self.validate_points(amount):
                return False
        else:
            divisor = 1
        talt_pt = amount/divisor
        if user in self.settings['users'][role_auth] or user in self.settings['users']['s-authorized']:
            if not target:
                self.update_guild_talt(talt_pt)
                self.settings['talt'][user]     = talt_pt
            else:
                self.update_guild_talt(talt_pt)
                self.settings['talt'][target]   = talt_pt
        else: #elif user in settings['users'][role_member]:
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

    ### obsolete function
    # def verify_channel(self, ch_type):
    #     return ch_type == "boss" or ch_type == "management"

    ### verify_channel is obsolete
    def set_channel(self, ch_type, channel, region=''):
        # if self.verify_channel(ch_type):
        self.settings['channel'][ch_type].append(channel)
        self.save_file()
        return True
        # else:
        #     return False

    def get_guild_level(self):
        return str(self.settings['guild_level'])

    def get_channel(self, ch_type):
        # if self.verify_channel(ch_type):
        return self.settings['channel'][ch_type]
        # else:
        #     return []

    def unset_channel(self, channel):
        try:
            self.settings['channel'][channel_mgmt].remove(channel)
            self.save_file()
        except:
            pass
        try:
            self.settings['channel'][channel_boss].remove(channel)
            self.save_file()
        except:
            pass
        return True


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

    def set_boss(self, user, utype):
        if utype == "users":
            user    += "@"
        try:
            if user in self.settings['role'][role_boss]:
                return False
            self.settings['role'][role_boss].append(user)
            self.save_file()
            return True
        except:
            return False

    def rm_boss(self, user):
        try:
            self.settings['role'][role_boss].remove(user)
            self.save_file()
            return True
        except:
            try:
                user    +=  "@"
                self.settings['role'][role_boss].remove(user)
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
        """
        :func:`greet` checks how many revisions the server owner has not received, of changelogs.

        Args:
            self
            current_version (str): latest Wings of Vaivora version

        Returns:
            int: number of revisions since last received changelog
        """

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

    def toggle_lock(self, mode=None):
        if not mode and not mode is False:
            self.settings['lock']   =   not self.settings['lock']
        else:
            self.settings['lock']   =   mode
        self.save_file()
        return True

    def locked(self):
        return self.settings['lock']


    def is_ch_type(self, msg_channel, ch_type):
        """
        :func:`is_ch_type` checks if the channel is a certain type, thus whether the command may execute.

        Args:
            self
            msg_channel (str): id of the channel of the originating message
            ch_type (str): the channel type ('boss' or 'management')

        Returns:
            bool:
                True if msg_channel is a valid channel, or no valid channels have been set;
                False otherwise (if msg_channel is not a valid channel)

        """
        ch_list         =   self.get_channel(ch_type)
        if not ch_list or msg_channel in ch_list:
            return True
        else:
            return False


    def process_command(self, msg_channel, settings_cmd, cmd_user, usr_roles, users, groups, channels, xargs=None):
        """
        :func:`process_command` processes the command sent to the settings module.
        It may call child functions like :func:`process_setting` for further processing.

        Args:
            msg_channel (str): id of the channel of the originating message
            settings_cmd (str): the command used, somewhat equivalent to arg_list[0] in $boss
            cmd_user (str): the one who called the command
            usr_roles (list(str)): the list of roles from the user
            users: (list(str)) list of users to be processed; can be None
            groups: (list(str)) list of roles to be processed; can be None

        Returns:
            list: an appropriate message for success or fail of command; varies in content (see below)

                ``set``, ``add``, ``unset`` return a list. This is from calling :func:`process_setting`.
                The list of `set` generally can be:

                    Command succeeded and returns:

                        list: ``len == 1``

                            str: message detailing success

                    ``fail``: Command failed and returns:

                        tuple ``len == 2``

                            list: ``len >= 1``

                                str: discord.py id

                            str: message detailing failure

                ``get`` typically returns a tuple of str, list (as ``fail``).
                The list of `get` depends:

                    ``get talt``, ``get role [@mention]``, ``get channel [#channel]``: different from :func:`process_setting`

                        list

                            list ``len >= 1``

                                tuple ``len==2``

                                    str: discord.py id

                                    str: message related to query and ID

                            str: message (success)

                    ``get role [role]``, ``get channel [channel]``: different from :func:`process_setting`

                        list

                            tuple ``len == 2``

                                list

                                    str: discord.py id

                                str: message related to query and ID

                            str: message (success)

                ``promote``, ``demote``, ``validate``, ``invalidate``:

                    the same as ``set``, ``add``, ``unset``; except not retrieved through :func:`process_setting`.

        """
        fail            =   []
        mode            =   ""
        user_role_id    =   self.get_highest_role_id(cmd_user, usr_roles)
        user_role       =   self.role_level[user_role_id]
        users           =   [('users', u) for u in users]
        groups          =   [('group', g) for g in groups]

        # settings are locked
        if self.locked():
            return [""]

        # settings help
        if rgx_help.match(settings_cmd):
            return command

        # setting (general)
        # failed due to role level: 0 or None
        if rgx_setting.match(settings_cmd) and user_role_id == 0:
            return [msg_perms + user_role + "`\n"]
        
        # special case: set guild level
        elif len(xargs) == 3 and rgx_set_guild.match(xargs[0]) and rgx_set_set.match(settings_cmd) and \
             rgx_gd_levels.match(xargs[1]) and rgx_gd_points.match(xargs[2]):
            self.toggle_lock(True)
            # succeeded
            if self.set_remainder_talt(xargs[1], xargs[2]):
                return [acknowledge + "\n" + "Guild is now set to level " + self.get_guild_level() + ", " + self.get_talt() + " Talt.\n"]
            else:
                return [msg_perms + user_role + "`\n"]

        # general setting
        elif rgx_setting.match(settings_cmd):
            self.toggle_lock(True)
            return list(self.process_setting(msg_channel, settings_cmd, cmd_user, user_role_id, users, groups, channels, xargs=xargs))

        # role change
        # failed due to role level: below 2
        elif rgx_rolechange and user_role_id < 2:
            return [msg_perms + user_role + "`\n"]
        # promote
        elif rgx_rolechange.match(settings_cmd) and rgx_promote.search(settings_cmd):
            self.toggle_lock(True)
            fail    =   self.promote_demote(mode_promote, users, groups, channels)
        # demote
        elif rgx_rolechange.match(settings_cmd):
            self.toggle_lock(True)
            fail    =   self.promote_demote(mode_demote, users, groups, channels)

        # validation - handle after all commands are checked
        # invalidate
        elif rgx_validation.match(settings_cmd) and rgx_invalid.search(settings_cmd):
            mode    =   mode_invalid
        # validate
        elif rgx_validation.match(settings_cmd):
            mode    =   mode_valid

        # did not match any settings or role change or validation
        else:
            return ["Your `$settings` command was not recognized. Please re-enter.\n" + msg_help]

        # check validation
        if rgx_validation.match(settings_cmd):
            self.toggle_lock(True)
            # selective validation
            if users:
                # process one at a time
                for kind, mention in users:
                    if not self.validate_talt(cmd_user, mode, user=mention):
                        fail.append((mention, "could not be" + mode + "d\n", "@"))
            # total validation
            else:
                # total validation succeeded
                if not self.validate_talt(cmd_user, mode):
                    return [msg_perms + user_role + "`\n"]
                # total validation failed
                else:
                    return [acknowledge + "\n" + "Records have been " + mode + "d.\n"]

        # rolechange or validation failed
        if fail:
            return [fail, "Your command partially or completely failed. " + \
                    "Your user may be too low. User level: `" + user_role + "`\n" + \
                    "Some of your mentions could not be processed:"]

        # validation succeeded
        elif rgx_validation.match(settings_cmd):
            return [acknowledge + "\n" + "Records for the specified users and/or groups have been " + mode + "d.\n"]

        # rolechange succeeded
        else: #elif rgx_rolechange.match(settings_cmd)
            return [acknowledge + "\n" + "Your role changes (`" + mode + "`) have been noted.\n"]


    def process_setting(self, msg_channel, settings_cmd, cmd_user, user_role_id, users, groups, channels, xargs):
        """
        :func:`process_command` processes the command sent to the settings module.
        It may call child functions like :func:`process_setting` for further processing.

        Args:
            msg_channel (str): id of the channel of the originating message
            settings_cmd (str): the command used, somewhat equivalent to arg_list[0] in $boss
            cmd_user (str): the one who called the command
            usr_roles (list(str)): the list of roles from the user
            users: (list(str)) list of users to be processed; can be None
            groups: (list(str)) list of roles to be processed; can be None

        Returns:
            list: an appropriate message for success or fail of command; varies in content (see below)

                ``set``, ``add``, ``unset`` return a list. This is from calling :func:`process_setting`.
                The list of `set` generally can be:

                    Command succeeded and returns:

                        list: ``len == 1``

                            str: message detailing success

                    ``fail``: Command failed and returns:

                        tuple ``len == 2``

                            list: ``len >= 1``

                                str: discord.py id

                            str: message detailing failure

                ``get`` typically returns a tuple of str, list (as ``fail``).
                The list of `get` depends:

                    ``get talt``, ``get role [@mention]``, ``get channel [#channel]``:

                        tuple

                            list ``len >= 1``

                                tuple ``len==2``

                                    str: discord.py id

                                    str: message related to query and ID

                            str: message (success)

                    ``get role [role]``, ``get channel [channel]``:

                        tuple

                            tuple ``len == 2``

                                list

                                    str: discord.py id

                                str: message related to query and ID

                            str: message (success)
        """

        if not xargs:
            return ("You did not supply the right arguments to `settings`. Please re-check syntax.\n" + msg_help,)

        fail        =   []
        ret_msg     =   ""
        target      =   None
        warning     =   ""
        user_role   =   self.role_level[user_role_id]


        # set get add unset
        #               0  1
        # $settings add talt 10 mention
        if rgx_set_add.match(settings_cmd) and not rgx_set_talt.match(xargs[1]):
            return ("You tried using `setting`:`add` but it only works for `settings`:`talt` module. Please re-check syntax.\n" + msg_help,)

        # $setting [setting] talt [number] [unit]
        if rgx_set_unit_t.match(xargs[0]):
            if not self.is_ch_type(msg_channel, channel_mgmt):
                return # silently deny changes
            if rgx_set_unset.match(settings_cmd):
                return ("You tried using `setting`:`unset` but it does not work for `settings`:`talt` module. Please re-check syntax.\n" + msg_help,)
            if groups:
                warning +=  "Warning: you can't use use `settings`:`talt` module with groups/roles. Ignoring.\n"
            target  =   mode_talt
            unit    =   unit_talt

            # special case: get talt all
            if len(xargs) == 2 and rgx_kw_all.match(xargs[1]) and rgx_set_get.match(settings_cmd):
                if users:
                    warning +=  "Warning: you can't use `settings`:`talt` `all` with users. Ignoring.\n"
                return (self.get_all_talt(), warning + "This guild thanks the following for contributing: ")

            # special case: get talt (guild)
            if len(xargs) == 1 and rgx_set_get.match(settings_cmd) and not users:
                gtalt   =   self.get_talt()
                gtaltlv =   self.get_talt_for_nextlevel()
                gpt     =   str(int(gtalt)*20)
                gptlv   =   str(int(gtaltlv)*20)
                return (warning + "This guild is level " + self.get_guild_level() + \
                        ", has a total of " + gtalt + " Talt (" + gpt + " points), and needs " + \
                        gtaltlv + " Talt (" + gptlv + " points) for the next level.\n",)

            if len(xargs) >= 2 and not rgx_set_talt.match(xargs[1]):
                return ("You did not supply the right arguments to `settings`. Please re-check syntax.\n" + msg_help,)

            # general cases
            if len(xargs) == 3 and rgx_set_unit.match(xargs[2]) and not rgx_set_unit_t.match(xargs[2]):
                unit    =   unit_point
            # ignore invalid input for unit
            elif len(xargs) == 3 and not rgx_set_unit.match(xargs[2]):
                warning +=  "Warning: invalid unit used. Using default unit `talt`.\n"

        # $settings [setting] [channel] [#channel]
        elif rgx_set_chan.match(xargs[0]) and len(xargs) > 1:
            # invalid channel type
            if not rgx_channel.match(xargs[1]):
                return ("You used an incorrect option for `setting`:`channel`. Valid options are: " + valid_ch + ".\n" + msg_help,)

            # valid channel types
            elif rgx_ch_boss.match(xargs[1]):
                ch_mode =   channel_boss
            else:
                ch_mode =   channel_mgmt

            # extra arguments; warn and ignore
            if rgx_set_get.match(settings_cmd) and len(xargs) > 2:
                warning +=  "Warning: extraneous arguments supplied to `settings`:`channel` module. Ignoring.\n"
            else:
                ch_list =   channels

            target  =   mode_channel

        # $settings [setting] role [role] [@mention]
        elif rgx_set_role.match(xargs[0]):
            if not self.is_ch_type(msg_channel, channel_mgmt):
                return ("",) # silently deny changes (wrong channel)
            target  =   mode_role

        # any incorrect combination of arguments
        else:
            if not self.is_ch_type(msg_channel, channel_mgmt):
                return ("",) # silently deny changes (wrong channel)
            return ("You did not supply the right arguments to `settings`. Please re-check syntax.\n" + msg_help,)

        # `talt`
        # actual `xargs` begin from index 1 on: index 0 is 'talt'
        if target == mode_talt:
            if rgx_set_add.match(settings_cmd):
                f   =   self.add_talt
            elif rgx_set_get.match(settings_cmd):
                f   =   self.get_talt
            else: #elif rgx_set_set.match(settings_cmd):
                f   =   self.set_talt

            # $settings [f] [number] [@mention...]
            if user_role_id > 1 and users:
                # process one at a time
                for kind, mention in users:
                    if f == self.get_talt:
                        # not actually fail but works with the return
                        fail.append((mention+'@', "contributed " + f(mention) + " Talt.\n"))
                    elif not f(cmd_user, int(xargs[1]), unit, mention):
                        fail.append(mention+'@')
                if fail and f == self.get_talt:
                    ret_msg +=  acknowledge + msg_records
                elif fail:
                    ret_msg +=  "Your Talt contributions could not be recorded. " + msg_perms + user_role + "`\n"
                else:
                    return (acknowledge + "Your Talt contributions were successfully recorded.\n",)
            # $settings [f] [number] [@mention...] # but too low on user level
            elif users:
                return (warning + msg_perms + user_role + "`\n",)
            # $settings [f] [number] # self; only needs member+
            elif not f(cmd_user, int(xargs[1]), unit):
                return (warning + "You entered an invalid amounnt of points. Points are multiples of 20.\n",)
            # $settings [f] [number] # self; RESULTS of above
            else:
                return (acknowledge + "Your Talt contributions were successfully recorded.\n",)

        # `channel`
        elif target == mode_channel:
            if rgx_set_set.match(settings_cmd):
                f   =   self.set_channel
                kw  =   "set"
            elif rgx_set_get.match(settings_cmd):
                if not self.is_ch_type(msg_channel, channel_mgmt):
                    return ("",) # silently deny changes
                f   =   self.get_channel
            else:
                if not self.is_ch_type(msg_channel, channel_mgmt):
                    return ("",) # silently deny changes
                f   =   self.unset_channel
                kw  =   "unset"

            if f == self.get_channel:
                # not actually fail but works with the return
                fail.append((f(ch_mode), "is marked as a `" + ch_mode + "` channel.\n", "#"))
                ret_msg +=  acknowledge + msg_records

            else:
                for ch in ch_list:
                    if not f(ch_mode, ch):
                        fail.append((ch, "could not be " + kw + " as `" + ch_mode + "`.\n", "#"))
                    else:
                        ret_msg +=  acknowledge + "Your channel changes have been recorded.\n"

        # `role`
        else:
            if rgx_set_set.match(settings_cmd):
                f   =   self.set_role
            elif rgx_set_get.match(settings_cmd):
                f   =   self.get_role
                g   =   self.get_role_user
                h   =   self.get_role_group
            # special case
            elif rgx_set_unset.match(settings_cmd) and rgx_ro_boss.match(xargs[1]):
                f   =   self.rm_boss
            else:
                # make sure to distinguish using arguments
                # this is "unset"
                f   =   self.set_role

            # $settings get role [@mention]
            if f == self.get_role and (users or groups):
                # extra arguments; warn and ignore
                if len(xargs) > 2:
                    warning +=  "Warning: extraneous arguments supplied to `settings`:`role` module. Ignoring.\n"

                for kind, mention in chain(users, groups):
                    # not actually fail but works with the return
                    #   tuple
                    #       str: discord.py id
                    #       str: message
                    if kind == 'users' and self.is_role_boss(mention):
                        fail.append((mention, "is the role level of `" + g(mention) + "`. Additionally, also of `boss` role.\n", "@"))
                    elif kind == 'users':
                        fail.append((mention, "is the role level of `" + g(mention) + "`.\n", "@"))
                    elif self.is_role_boss(mention):
                        fail.append((mention, "is the role level of `" + h(mention) + "`. Additionally, also of `boss` role.\n", "&"))
                    else:
                        fail.append((mention, "is the role level of `" + h(mention) + "`.\n", "&"))

                ret_msg +=  acknowledge + msg_records

            # $settings get role [roles ...]
            elif f == self.get_role:
                # the role to_check
                to_check    =   ""
                # roles that have been checked
                checked     =   []

                # ignore xargs[0] because that's the role used for comparison
                for xarg in xargs[1:]:
                    if not rgx_roles.match(xarg):
                        continue
                    elif rgx_ro_boss.match(xarg):
                        to_check    =   role_boss
                    elif rgx_ro_auth.match(xarg):
                        to_check    =   role_auth
                    else:
                        to_check    =   role_member
                    if to_check in checked:
                        to_check    =   ""
                        continue
                    #           list         str
                    fail.append((f(to_check), "is of role level `" + to_check + "`.\n"))
                    checked.append(to_check)
                    to_check    =   ""

                ret_msg +=  acknowledge + msg_records

            # $settings [setting] role [role] [@mention]
            else: # elif f == self.set_role
                # set
                if rgx_set_set.match(settings_cmd):
                    # extra arguments; warn and ignore
                    if len(xargs) > 2:
                        warning +=  "Warning: extraneous arguments supplied to `settings`:`role` module. Ignoring.\n"

                    if not rgx_roles.match(xargs[1]):
                        return (warning + xargs[1] + " is not a valid role. Please re-check syntax.\n" + msg_help,)
                    elif rgx_ro_boss.match(xargs[1]):
                        set_role    =   role_boss
                    elif rgx_ro_auth.match(xargs[1]):
                        set_role    =   role_auth
                    else:
                        set_role    =   role_member
                # unset
                else:
                    set_role    =   role_none

                # you shall not pass
                if user_role_id <= role_idx[set_role]:
                    return (warning + "You are not permitted to change roles of levels above you.\n",)

                for kind, mention in chain(users, groups):
                    if f == self.rm_boss:
                        if not f(mention):
                            fail.append((mention, "'s `boss` role could not be unset.\n", "@" if kind == 'users' else "&"))
                        else:
                            ret_msg = warning + acknowledge + "Your role changes have been noted.\n"
                    elif not f(mention, kind, set_role):
                        fail.append((mention, "'s role could not be " + ("un" if set_role == role_none else "") + "set.\n", "@" if kind == 'users' else "&"))
                    else:
                        ret_msg = warning + acknowledge + "Your role changes have been noted.\n"

        # "get" setting does not really fail; this is a convenience (may want to rename the variable later)
        if fail and rgx_set_get.match(settings_cmd):
            ret_msg =   warning + ret_msg
            return (fail, ret_msg)

        # all other setting commands
        elif fail:
            return (fail, msg_fails)

        # "set", etc succeeded
        else:
            return (ret_msg,)

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