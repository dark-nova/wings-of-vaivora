import re

MODULE_NAME = 'settings'
COMMAND = '$' + MODULE_NAME

HELP = []
HELP.append(
"""
```
Usage:
    $settings <setting> talt <talt-value> [<talt-unit>] ([<@mention>] | guild)
    $settings <setting> (<role> [<@mention>] | <channel> [<#channel>])
    $settings <validate> [<@mention>]
    $settings <role-change> <@mention>
    $settings help

Examples:
    $settings add talt 12
        Means: Add 12 Talt to your guild record.
        Note: If not "Authorized" or "Member", this is only temporary. It must be validated.

    $settings set talt 12
        Means: Sets your guild record of Talt to 12. Not the same as adding.

    $settings add talt 240 points
        Means: The same as `$settings add talt 12`, with optional unit.

    $settings add talt 12 @person
        Means: Add 12 Talt to @person's guild record.
        You must be "Authorized" to do this.

    $settings set channel management #management
        Means: Sets this channel to "Management".
        Note: this disables Management in all channels not marked as "Management".

    $settings set role authorized @person
        Means: Sets @person to be "Authorized".
        You must be "Authorized" to do this.
        Note: guild owners are considered "Super-Authorized" and must set this up first.

```
""")

HELP.append(
"""
```
Options:
    <setting>
        This can be "add", "set", "remove", or "get". Manipulates records.
        Options:
            "add" can only be used for Talt-related subcommands. Increments relative to user's base.
            "set" can be used for all associated subcommands. Sets Talt, Role, and Channel.
            "remove" can be used for all associated subcommands. Removes Talt contribution, Roles from users mentioned, etc.
            "get" can be used for all associated subcommands. Retrieves Talt contribution, highest Role from users mentioned, etc.
        Note: "Super-Authorized" will only be shown as "Authorized".

* Discord roles are different from Wings of Vaivora's Roles.
```
""")

HELP.append(
"""
```
Options (continued):
    talt
        This <subcommand> can only be "talt". Allows manipulation of Talt guild records.

    <talt-value>
        A number. The amount to use for `talt`. 20 points = 1 talt

    [<talt-unit>]
        (optional) Sets the unit to use. 20 points = 1 Talt. By default, Talt will be used if omitted.
        Options:
            "points": shown in-game
            "talt": the default
        Note: the Guild UI in-game always uses points.

    guild
        A special subcommand target for <setting> `talt`. Cannot use "add" or "remove".
        <setting> "get" prints how many points (and Talt) the guild has.
        <setting> "set" allows you to set the current points.
        Missing points (unlisted contributions) will be stored in a hidden variable, for consistency.

    <@mention>
        (optional for <validate>) A Discord member. You must use the mention format for this.

    [<#channel>]
        (optional) A Discord channel. You must use the channel link format for this.
        Both you and Wings of Vaivora must be able to see the channel.
        If omitted in the <setting> command, the current channel will be assumed.

    help
        Prints this page.
```
""")

ACKNOWLEDGED = "Thank you! Your command has been acknowledged and recorded.\n"

MSG_HELP = "Please run `" + COMMAND + " help` for syntax."

CMD_ARG_SETTING = '<setting>'
CMD_ARG_VALIDATION = '<validation>'
CMD_ARG_ROLECHANGE = '<role-change>'
CMD_ARG_SUBCMD = '<subcommand>'

CMD_ARG_SETTING_TALT = '<talt>'
CMD_ARG_SETTING_TALT_UNIT = 'Talt'
CMD_ARG_SETTING_TALT_POINTS = 'Points'
CMD_ARG_SETTING_PREFIX = '<prefix>' # to preserve consistency; not yet implemented
CMD_ARG_SETTING_CHANNEL = '<channel>'
CMD_ARG_SETTING_ROLE = '<role>'
CMD_ARG_SETTING_REGION = '<region>' # not yet implemented

TABLE_PREFIX = 'prefix' # to preserve consistency; not yet implemented
TABLE_CHANNEL = 'channel'
TABLE_ROLE = 'role'
TABLE_REGION = 'region' # not yet implemented

VALIDATION_VAL = 'validate'
VALIDATION_INV = 'invalidate'

ROLES_PROMOTE = 'promote'
ROLES_DEMOTE = 'demote'

SETTING_ADD = 'add'
SETTING_SET = 'set'
SETTING_GET = 'get'
SETTING_REMOVE = 'remove'

TARGET_TALT = '<talt>'
TARGET_ROLE = '<role>'
TARGET_CHANNEL = '<channel>'

REC_PERMANENTLY = 'permanently'
REC_TEMPORARILY = 'temporarily'

REGEX_SETTING_ADD = re.compile(r'(add?|plus)', re.IGNORECASE)
REGEX_SETTING_SET = re.compile(r'^set', re.IGNORECASE)
REGEX_SETTING_GET = re.compile(r'(^get|retr(ieve)?)', re.IGNORECASE)
REGEX_SETTING_REMOVE = re.compile(r'(re?m(ove)?|de?l(ete)?)', re.IGNORECASE)

REGEX_VALIDATION_VALIDATE = re.compile(r'(valid.*|confirm)', re.IGNORECASE)
REGEX_VALIDATION_INVALIDATE = re.compile(r'^in.+', re.IGNORECASE)

REGEX_ROLES_PROMOTE = re.compile(r'^pro.*', re.IGNORECASE)
REGEX_ROLES_DEMOTE = re.compile(r'^de.*', re.IGNORECASE)

REGEX_SETTING_TARGET_TALT = re.compile(r'[ts]alt', re.IGNORECASE)
REGEX_SETTING_TARGET_ROLE = re.compile(r'^rol.?', re.IGNORECASE)
REGEX_SETTING_TARGET_CHANNEL = re.compile(r'ch(an(nel)?)*', re.IGNORECASE)

REGEX_CONTRIBUTION_POINTS = re.compile(r'(pt|point)s?', re.IGNORECASE)

SUCCESS = 'Your {} records have been updated to `{}`.'
SUCCESS_CHANNELS = 'Here are channels of {} type:\n\n{}'
SUCCESS_ROLES = 'Here are users of {} role type:\n\n{}'
SUCCESS_PURGED = 'Your channel records were purged successfully.'
SUCCESS_ROLES_UP = 'Your {} roles have been successfully updated.'
SUCCESS_CONTRIBUTIONS = 'Guild records have been successfully updated.\n{}'
SUCCESS_GET_CONTRIBS = 'Here are the guild\'s contribution records:\n'

PARTIAL_SUCCESS = 'Your {} records did not fully process. Errors:\n\n{}'

FAIL_NO_CHANNELS = 'No channels were found associated with the {} type.'
FAIL_NO_ROLES = 'No users were found associated with the {} role type.'
FAIL_NOT_AUTH = 'You are not authorized to do this!'
FAIL_PURGED = 'Your channel records could not be purged.'
FAIL_NO_MENTIONS = 'No mentions were added.'
FAIL_NO_USER_BOSS = "Members can't be set as the boss role!"
FAIL_TOO_MANY_MENTIONS = 'You mentioned too many users!'
FAIL_INVALID_MENTION = 'You typed an invalid mention!'
FAIL_INVALID_POINTS = 'You entered an invalid amount of points! Check unit or value (divisible by 20).'
FAIL_CONTRIBUTIONS = 'Your contributions could not be recorded.'
FAIL_NO_CONTRIBS = 'No contributions were found.'

FAIL_NOT_PARSED = 'Your command could not be parsed.'
FAIL_COULD_NOT = FAIL_NOT_PARSED + '\nCould not {} {}\'s {} record.'

NOTICE_ROLE = 'All users not mentioned here have not been assigned a Vaivora role.'

USAGE_SET_CHANNELS = '$settings set channel <type> <#channel> [<#channel> ...]'

### DO NOT CHANGE/TRANSLATE THIS SECTION BELOW ###

# Guild Levels     1        2        3        4        5
G_LEVEL =    [0,   0,       0,      50,     125,     250,
# Guild Levels     6        7        8        9       10
                 450,     886,    1598,    2907,    4786,
# Guild Levels    11       12       13       14       15
                7483,   11353,   16907,   24876,   52726,
# Guild Levels    16       17       18       19       20
              160712,  345531,  742891, 1597216, 3434015]

TALT = 'talt'
TALT_GUILD = 'guild'
TALT_REMAINDER = 'remainder'

TALT_QUOTA = 'quota'
TALT_QUOTA_PERIODIC = 'periodic_quota'

GUILD_LEVEL = 'guild_level'

ROLE_BOSS = 'boss'
ROLE_NONE = 'none'
ROLE_MEMBER = 'member'
ROLE_AUTH = 'authorized'
ROLE_SUPER_AUTH = 's-authorized'

# Roles by value      0            1          2                3
ROLE_LEVEL = [ROLE_NONE, ROLE_MEMBER, ROLE_AUTH, ROLE_SUPER_AUTH]

UTYPE_USERS = 'users'
UTYPE_GROUP = 'group'

CHANNEL_BOSS = 'boss'
CHANNEL_MGMT = 'management'

VAIVORA_VER = 'vaivora-version' # legacy
WELCOMED = 'welcomed'

DB_LOCK = 'lock'

OPT_DEFAULT = 'default'

SERVER_DIR = 'server_settings'
FILE_PATH = '{}/{}.json'

FMT_SETTING_FAIL = '| {}: {}; {}: {}; {}: {}; {}: {}'

### DO NOT CHANGE/TRANSLATE THIS SECTION ABOVE ###
