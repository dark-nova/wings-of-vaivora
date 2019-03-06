import re

MODULE_NAME = 'settings'
COMMAND = '$' + MODULE_NAME

HELP = []
HELP.append(
"""
```
Usage:
    $settings <setting> talt <talt-value> [<talt-unit>] ([<@mention>] | guild)
    $settings <setting> <obj> (<role> [<@mention>] | <channel> [<#channel>])
    $settings help

Examples:
    $settings add talt 12
        Means: Add 12 Talt to your guild record.

    $settings set talt 12
        Means: Sets your guild record of Talt to 12. Not the same as adding.

    $settings add talt 240 points
        Means: The same as `$settings add talt 12`, with optional unit.

    $settings add talt 12 @person
        Means: Add 12 Talt to @person's guild record.
        You must be "Authorized" to do this.

    $settings set channel settings #settings
        Means: Sets this channel to "Settings".
        Note: this disables Settings in all channels not marked as "Settings".

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

    <obj>
        This is the object to modify. For users, "roles". For channels, "channels".

    <channel>
        This can be "settings" or "boss". Sets channels (and restricts others).
        Options:
            "settings": Adds a channel to allow all settings commands. 'get'ters will still be unrestricted.
            "boss": Adds a channel to accept boss record manipulation.
        Once a channel is set (and none were, before), many commands are no longer read outside the allowed channels.
```
""")

HELP.append(
"""
```
Options (continued):
    <contribution>
        This can be "points", "talt", or "contributions".
        Options:
            "points": shown in the guild UI in-game
            "talt": defined to be the item; 1 talt = 20 points
            "contributions": the same as "points"
        Allows manipulation of Talt guild records.

    <contribution-value>
        A number. The amount to use for `talt`. 20 points = 1 talt

    guild
        A special subcommand target for <setting> `talt`. Cannot use "add" or "remove".
        <setting> "get" prints how many points (and Talt) the guild has.
        <setting> "set" allows you to set the current points.
        Missing points (unlisted contributions) will be stored in a hidden variable, for consistency.

    <@mention>
        (optional) A Discord member or role.
        Preferably, you should use the mention format for this. You may use ID's if necessary.
        If omitted in the <setting> command, the command user will be assumed.

    [<#channel>]
        (optional) A Discord channel.
        You must use the channel link format for this.
        Both you and Wings of Vaivora must be able to see the channel.
        If omitted in the <setting> command, the current channel will be assumed.

    help
        Prints this page.


* Discord roles are different from Wings of Vaivora's Roles.
```
""")

ACKNOWLEDGED = "Thank you! Your command has been acknowledged and recorded.\n"

MSG_HELP = "Please run `" + COMMAND + " help` for syntax."

TABLE_CHANNEL = 'channel'

SETTING_SET = 'set'

SUCCESS = 'Your {} records have been updated to `{}`.'
SUCCESS_CHANNELS = 'Here are channels of {} type:\n\n{}'
SUCCESS_ROLES = 'Here are users of {} role type:\n\n{}'
SUCCESS_PURGED = 'Your channel records were purged successfully.'
SUCCESS_ROLES_UP = 'Your {} roles have been successfully updated.'
SUCCESS_ROLES_RM = 'You have successfully removed mentions from the {} role.'
SUCCESS_CONTRIBUTIONS = 'Guild records have been successfully updated.\n{}'
SUCCESS_GET_CONTRIBS = 'Here are the guild\'s contribution records:\n'
SUCCESS_SET_GUILD = 'Guild records have been successfully updated.'
SUCCESS_GET_GUILD = 'This guild is currently level {} with {} points.\n```{} {}```'
SUCCESS_CHANNELS_RM = 'You have successfully removed channels from the {} type.'

PARTIAL_SUCCESS = '\nIn addition, some of your {} records did not fully process. Errors:\n\n{}'

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
FAIL_SET_GUILD = 'Something went wrong. Your guild points were not updated.'

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

ROLE_BOSS = 'boss'
ROLE_NONE = 'none'
ROLE_MEMBER = 'member'
ROLE_AUTH = 'authorized'
ROLE_SUPER_AUTH = 's-authorized'

### DO NOT CHANGE/TRANSLATE THIS SECTION ABOVE ###
