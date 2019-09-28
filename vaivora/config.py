"""Wings of Vaivora configuration module

vaivora.config handles one-time loads of the following files:
- emoji
- boss
- guild

The main config.yaml file is not handled by this module,
because only bot.py needs access to the file.

Attributes:
    EMOJI (dict): the emoji configuration; will load defaults
        if a user-created version is not found
    BOSS (dict): contains information about Tree of Savior bosses,
        to be used by vaivora.boss, vaivora.db, and cogs.boss
    GUILD (dict): contains information about Tree of Savior guilds,
        to be used by vaivora.db and cogs.settings

"""
import yaml


try:
    with open('emoji.yaml', 'r') as f:
        EMOJI = yaml.safe_load(f)
except FileNotFoundError:
    # Fallback on default
    with open('emoji.yaml.example', 'r') as f:
        EMOJI = yaml.safe_load(f)

with open('boss.yaml', 'r') as f:
    BOSS = yaml.safe_load(f)

ALL_BOSSES = []
for kind in BOSS['bosses']['all']:
    if kind == 'event':
        continue
    else:
        ALL_BOSSES.extend(BOSS['bosses'][kind])

with open('guild.yaml', 'r') as f:
    GUILD = yaml.safe_load(f)
