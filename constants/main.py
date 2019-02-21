from vaivora.disclaimer import disclaimer

BOSS_ALERT = '{} The following bosses will spawn within 15 minutes:\n\n'

MSG_HELP = """
Here are commands. Valid prefixes are `$` (dollar sign) and `Vaivora,<space>`,
e.g. `$boss` or `Vaivora, help`

```
"Changelogs" commands
    $unsubscribe
    $subscribe

* These functions are currently disabled.
```
```
"Boss" commands
    $boss [args ...]
    $boss help

* Use "$boss help" for more information.

Examples:
    $boss all list
    $boss mineloader died 13:00 forest
    $boss ml died 1:00p "forest of prayer"

* More examples in "$boss help"
```
```
"Settings" commands
    $settings [args ...]
    $settings help

* Use "$settings help" for more information.

Examples:
    $settings set role auth @Leaders
    $settings set role member @Members
```
```
General
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

ROLE_BOSS = "boss"
ROLE_SETTINGS = "settings"
