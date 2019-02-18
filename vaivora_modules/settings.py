import re
import os
import os.path
import json
import asyncio
import aiosqlite
import typing
from itertools import chain

import vaivora_modules.db
from vaivora_modules.secrets import discord_user_id
import constants.settings
#from constants.settings import en_us as lang_settings

# BGN CONST

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

# END CONST

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
    vdb = vaivora_modules.db.Database(guild_id)
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
    vdb = vaivora_modules.db.Database(guild_id)
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
    vdb = vaivora_modules.db.Database(guild_id)
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
    vdb = vaivora_modules.db.Database(guild_id)
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
