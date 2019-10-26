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
    LOGGER (logging.LOGGER): general logger
    BOSS_LOGGER (logging.LOGGER): logger for cogs.boss
    COMMON_LOGGER (logging.LOGGER): logger for vaivora.common
    DB_LOGGER (logging.LOGGER): logger for vaivora.db
    EVENTS_LOGGER (logging.LOGGER): logger for cogs.events
    GEMS_LOGGER (logging.LOGGER): logger for cogs.gems
    MEME_LOGGER (logging.LOGGER): logger for cogs.meme
    SETTINGS_LOGGER (logging.LOGGER): logger for cogs.settings

"""
import logging

import yaml


# Multiple loggers, for each module
LOGGER = logging.getLogger('vaivora')
BOSS_LOGGER = logging.getLogger('vaivora.cogs.boss')
COMMON_LOGGER = logging.getLogger('vaivora.vaivora.common')
DB_LOGGER = logging.getLogger('vaivora.vaivora.db')
EVENTS_LOGGER = logging.getLogger('vaivora.cogs.events')
GEMS_LOGGER = logging.getLogger('vaivora.cogs.gems')
MEME_LOGGER = logging.getLogger('vaivora.cogs.meme')
SETTINGS_LOGGER = logging.getLogger('vaivora.cogs.settings')

LOGGERS = [
    LOGGER,
    BOSS_LOGGER,
    COMMON_LOGGER,
    DB_LOGGER,
    EVENTS_LOGGER,
    GEMS_LOGGER,
    MEME_LOGGER,
    SETTINGS_LOGGER,
    ]

for logger in LOGGERS:
    logger.setLevel(logging.DEBUG)

FH = logging.FileHandler('vaivora.log')
FH.setLevel(logging.DEBUG)

CH = logging.StreamHandler()
CH.setLevel(logging.WARNING)

FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
FH.setFormatter(FORMATTER)
CH.setFormatter(FORMATTER)

# All loggers will use the same FileHandler and StreamHandler
for logger in LOGGERS:
    logger.addHandler(FH)
    logger.addHandler(CH)


try:
    with open('emoji.yaml', 'r') as f:
        EMOJI = yaml.safe_load(f)
except FileNotFoundError:
    # Fallback on default
    LOGGER.info('Custom emoji not set. Loading default emoji.')
    with open('emoji.yaml.example', 'r') as f:
        EMOJI = yaml.safe_load(f)

with open('boss.yaml', 'r') as f:
    BOSS = yaml.safe_load(f)

ALL_BOSSES = []
for kind in BOSS['bosses']['all']:
    if kind == 'event':
        pass
    else:
        ALL_BOSSES.extend(BOSS['bosses'][kind])

with open('guild.yaml', 'r') as f:
    GUILD = yaml.safe_load(f)
