from disclaimer import disclaimer

BOSS_ALERT = '{} The following bosses will spawn within 15 minutes:\n\n'

MSG_HELP = """
Here are commands. Valid prefixes are `$` (dollar sign) and `Vaivora,<space>`,
e.g. `$boss` or `Vaivora, help`

`$boss` commands
More info: <https://github.com/dark-nova/wings-of-vaivora/blob/master/docs/BOSS.md>

`$settings` commands
More info: <https://github.com/dark-nova/wings-of-vaivora/blob/master/docs/SETTINGS.md>

`$gems` commands
More info: <https://github.com/dark-nova/wings-of-vaivora/blob/master/docs/GEMS.md>

`$offset` commands
More info: <https://github.com/dark-nova/wings-of-vaivora/blob/master/docs/OFFSET.md>

General
```
$help: prints this page in Direct Message
```
"""

WELCOME = """
Thank you for inviting me to your server!
I am a representative bot for the Wings of Vaivora, here to help you record your journey.
Please read the following before continuing.
""" + disclaimer + """
Anyone may contribute to this bot's development: https://github.com/dark-nova/wings-of-vaivora
"""

FAIL_CANT_DM = '**{}** is not available in Direct Messages.'
FAIL_TOO_FEW_ARGS = '{} Too few or many arguments for `{}`.\n\nUsage: `{}`'
