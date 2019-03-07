from vaivora.disclaimer import disclaimer

BOSS_ALERT = '{} The following bosses will spawn within 15 minutes:\n\n'

MSG_HELP = """
Here are commands. Valid prefixes are `$` (dollar sign) and `Vaivora,<space>`,
e.g. `$boss` or `Vaivora, help`

`$boss` commands
```
$boss [args ...]
$boss help

* Use "$boss help" for more information.

Examples:
    $boss all list
    $boss mineloader died 13:00 forest
    $boss ml died 1:00p "forest of prayer"

* More examples in "$boss help"
```
More info: <https://github.com/dark-nova/wings-of-vaivora/blob/master/docs/BOSS.md>

`$settings` commands
```
$settings [args ...]
$settings help

* Use "$settings help" for more information.

Examples:
    $settings set role auth @Leaders
    $settings set role member @Members
```
More info: <https://github.com/dark-nova/wings-of-vaivora/blob/master/docs/SETTINGS.md>

`$gems` commands
```
$settings [args ...]
$settings help

* Use "$gems help" for more information.

Examples:
    $gems exp 1x1 1x2
    $gems gem2lv 1 0 2
```
More info: <https://github.com/dark-nova/wings-of-vaivora/blob/master/docs/GEMS.md>

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

ROLE_SETTINGS = "settings"

HELP = 'help'

FAIL_CANT_DM = '**{}** is not available in Direct Messages.'
FAIL_TOO_FEW_ARGS = '{} Too few or many arguments for `{}`.\n\nUsage: `{}`'
