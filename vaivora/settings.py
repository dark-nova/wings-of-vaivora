import re
import os
import os.path
import json
import asyncio
import aiosqlite
import typing
from itertools import chain

import vaivora.db
from vaivora.secrets import discord_user_id
import constants.settings
#from constants.settings import en_us as lang_settings


def help():
    """
    :func:`help` returns help for this module.

    Returns:
        a list of detailed help messages
    """
    return constants.settings.HELP


async def get_users(guild_id: int, kind: str):
    """
    :func:`get_authorized` returns a list of authorized users.

    Args:
        guild_id (int): the id of the guild to check
        kind (str): the kind of user to get

    Returns:
        list: all users that are of `kind`
        None: if no users were found
    """
    vdb = vaivora.db.Database(guild_id)
    return await vdb.get_users(kind)


async def purge(guild_id: int):
    """
    :func:`purge` is a last-resort subcommand that
    resets the channels table.

    Args:
        guild_id (int): the id of the guild to purge tables

    Returns:
        True if successful; False otherwise
    """
    vdb = vaivora.db.Database(guild_id)
    return await vdb.purge()


async def get_channel(guild_id: int, kind):
    """
    :func:`get_channel` gets a list of channels
    of an associated `kind`.

    Args:
        guild_id (int): the id of the guild to check
        kind (str): the kind of channel to get

    Returns:
        list: all channel id's of `kind`
        None: if no channels were found
    """
    vdb = vaivora.db.Database(guild_id)
    return await vdb.get_channel(kind)


async def set_channel(guild_id: int, kind,
                      channels: typing.Optional[list] = [],
                      channel: typing.Optional[str] = ''):
    """
    :func:`set_channel` sets channel(s) to a given `kind`.

    Args:
        guild_id (int): the id of the guild to check
        kind
        channels (list): (optional) the channels to set

    Returns:
        list: of None if succesful; id's of failed entries otherwise
    """
    vdb = vaivora.db.Database(guild_id)
    errs = []

    if channels:
        for _channel in channels:
            try:
                await vdb.set_channel(kind, _channel)
            except:
                errs.append(_channel)
    else:
        try:
            await vdb.set_channel(kind, channel)
        except:
            return [channel]

    return errs
