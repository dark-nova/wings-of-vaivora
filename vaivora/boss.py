import asyncio
import re

import vaivora.common
from vaivora.config import BOSS, ALL_BOSSES


CHANNEL_MAX = 4

REGEX_CHANNEL = re.compile(r'(ch?)*.?([1-4])$', re.IGNORECASE)
REGEX_MAP_FLOOR = re.compile('.*([0-9]).*')


class Error(Exception):
    """Adapted from https://docs.python.org/3/tutorial/errors.html"""
    pass


class InvalidBossError(Error):
    """An invalid boss was detected."""
    def __init__(self, boss):
        self.message = f'{boss} is an invalid boss'
        super().__init__(self.message)


class InvalidMapError(Error):
    """An invalid map was detected."""
    def __init__(self, a_map, boss):
        self.message = (
            f'{a_map} is an invalid map for {boss}; '
            'no map was assumed.')
        super().__init__(self.message) 


class InvalidChannelError(Error):
    """An invalid channel was detected."""
    def __init__(self, channel):
        self.message = (
            f'{channel} is not a number between 1 and {CHANNEL_MAX}; '
            'channel 1 was assumed.'
            )
        super().__init__(self.message)


class Boss:
    """Class structure for a boss.

    Attributes:
        boss (str): the name of the boss
        aliases (list): list of aliases for the boss
        map (str): an individual map; determined by `validate_map`
        maps (list): list of maps where the boss may spawn
        nearest_warps (list): a list of tuples (map: str, distance: int)
            where each map contains a warp statue
        channel (int): the channel of the boss map

    """

    def __init__(self, boss: str):
        self.boss = boss

    async def populate(self):
        if self.boss not in ALL_BOSSES:
            await self.validate_boss()

        self.aliases = BOSS_CONF['aliases'][boss]
        self.maps = BOSS_CONF['maps'][boss]
        self.nearest_warps = BOSS_CONF['nearest_warps'][boss]
        self.channel = 1

    async def validate_boss(self):
        """Validates whether `self.boss` is actually a boss.

        Raises:
            InvalidBossError: if not matched

        """
        for boss, aliases in BOSS_CONF['aliases'].items():
            if self.boss in aliases:
                # Synonyms are unique and exact match only
                return boss

        matches = [
            boss
            for boss
            in ALL_BOSSES
            if re.search(self.boss, boss, re.IGNORECASE)
            ]

        if len(matches) != 1:
            raise InvalidBossError(self.boss)

        self.boss = matches[0]

    async def validate_map(self):
        """Validates whether user input map belongs to the `self.boss`.

        Raises:
            InvalidMapError: if not matched

        """
        # Ignore user input if only one map exists
        if len(self.maps) == 1:
            self.map = self.maps[0]
        else:
            matches = [
                a_map
                for a_map
                in self.maps
                if re.search(self.map, a_map, re.IGNORECASE)
                ]

            if len(matches) != 1:
                raise InvalidMapError(self.map, self.boss)

            self.map = matches[0]

    async def validate_channel(self):
        """Validates a channel, as defined to be between 1 and
        CHANNEL_MAX, inclusive.

        """
        if self.channel.isdigit() and int(self.channel) in range(
            1, CHANNEL_MAX + 1
            ):
            self.channel = int(self.channel)
        else:
            match = REGEX_CHANNEL.match(self.channel)
            try:
                self.channel = int(match.group(2))
            except AttributeError:
                raise InvalidChannelError(self.channel)

    async def parse_map_or_channel(self, map_or_channel: str = None):
        """Processes for `status` subcommands. Assigns the attributes
        `self.map` and `self.channel` if no critical errors were
        produced.

        Args:
            map_or_channel (str, optional): the map xor channel in
                which the boss died; can be None from origin function

        Returns:
            str: an error message, if `map_or_channel` was invalid
            None: if everything was valid

        """
        # Map is fixed for these
        if self.boss in (BOSS_CONF['world'] + BOSS_CONF['event']):
            # Lazy map assignment, but will cause beneficial errors
            # if new World Bosses get assigned more maps
            self.map = None
            await self.validate_map()
            # Assume channel 1 if omitted or invalid
            if not map_or_channel:
                self.channel = 1
            else:
                self.channel = map_or_channel
                try:
                    await self.validate_channel()
                except InvalidChannelError as e:
                    self.channel = 1
                    return e
        # Channel is fixed to 1 for these
        else:
            # Don't assume a map, if nothing was provided
            # Command example: v!boss mirtis died 12:00
            if not map_or_channel:
                if len(self.maps) > 1:
                    self.map = None
                else:
                    self.map = self.maps[0]
            else:
                try:
                    self.map = map_or_channel
                    await self.validate_map()
                except InvalidMapError as e:
                    self.map = None
                    return e
