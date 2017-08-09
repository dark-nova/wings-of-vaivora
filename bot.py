#!/usr/bin/env python
import discord
import logging
import sqlite3
import asyncio
import random
import shlex
#from queue import Queue as q
from hashlib import blake2b
import json
import re
import os
from datetime import datetime, timedelta
from operator import itemgetter

# import additional constants
from importlib import import_module as im
import vaivora_constants
for mod in vaivora_constants.modules:
    im(mod)

import vaivora_modules
for mod in vaivora_modules.modules:
    im(mod)

# basic declarations and initializations
client              = discord.Client()
vdbs                = dict()
vdst                = dict()

command_boss        = "boss"
command_settings    = "settings"

rgx_help            = re.compile(r'help', re.IGNORECASE)
rgx_boss            = re.compile(r'\$boss .+', re.IGNORECASE)

to_sanitize         = re.compile(r"""[^a-z0-9 .:$"',-><#]""", re.IGNORECASE)

def splitDblQuotesSpaces(command):
    lex = shlex.shlex(command)
    lex.quotes = '"'
    lex.commenters = ""
    lex.whitespace_split = True
    return list(lex)

first_run           = 0

# @func:    on_ready()
# @return:
#       None
@client.event
async def on_ready():
    global first_run
    print("Logging in...")
    print('Successsfully logged in as: ' + client.user.name + '#' + \
          client.user.id + '. Ready!')
    await client.change_presence(game=discord.Game(name="with startup. Please wait a moment..."), status=discord.Status.idle)
    first_run   +=  len(client.servers)
    nservs  =   str(first_run)
    await client.change_presence(game=discord.Game(name=("with files. Processing " + nservs + " guilds...")), status=discord.Status.dnd)
    for server in client.servers:
        await asyncio.sleep(1)
        if server.unavailable:
            first_run   -=  1
            continue
        vdbs[server.id]     = vaivora_modules.db.Database(server.id)
        o_id                = server.owner.id
        vdst[server.id]     = vaivora_modules.settings.Settings(server.id, o_id)
        await greet(server.id, server.owner)
        first_run   -=  1
    await asyncio.sleep(2)
    first_run   =   0
    await client.change_presence(game=discord.Game(name=("in " + nservs + " guilds # [$help] or [Vaivora, help] for info")), status=discord.Status.online)
    return


# @func:    greet(str, discord.Member) : void
# @arg:
#       server_id : str
#           the server's id
#       server_owner : discord.Member
#           the server's owner    
@client.event
async def greet(server_id, server_owner):
    do_not_msg  = await get_unsubscribed()
    if server_owner.id in do_not_msg:
        return

    iters   =   0         
    nrevs   =   vdst[server_id].greet(vaivora_modules.version.get_current_version())
    if nrevs != 0:
        for vaivora_log in vaivora_modules.version.get_changelogs(nrevs):
            iters += 1
            print(server_id, server_owner, ": receiving", iters, "logs out of", nrevs*-1)
            try:
                await client.send_message(server_owner, vaivora_log)
            except: # cannot send messages, ignore
                ### TODO: handle deletion
                continue



# @func:    on_server_available(discord.Server) : bool
# @arg:
#       server : discord.Server
#           the Discord server joining
# @return:
#       True if ready, False otherwise
@client.event
async def on_server_join(server):
    already           = False
    vaivora_version   = vaivora_modules.version.get_current_version()
    if server.unavailable:
        return False
    vdbs[server.id]     = vaivora_modules.db.Database(server.id)
    o_id                = server.owner.id
    vdst[server.id]     = vaivora_modules.settings.Settings(server.id, o_id)
    await greet(server.id, server.owner)
    return True


# @func:    on_message(Discord.message) : bool
#     begin code for message processing
# @arg:
#     message: Discord.message; includes message among sender (Discord.user) and server (Discord.server)
# @return:
#     True if succeeded, False otherwise
@client.event
async def on_message(message):
    if message.author == client.user:
        return True # do not respond to self

    # if first_run and not message.channel:
    #     await client.send_message(message.author, \
    #                               "Still processing " + str(first_run) + " servers.\n")
    #     return False
    if first_run:
        # await client.send_message(message.channel, message.author.mention + " " + \
        #                           "Still processing " + str(first_run) + " servers.\n")
        return False

    # direct message processing
    if not message.channel or not message.channel.name:
        # boss help
        if rgx_boss.match(message.content):
            if rgx_help.search(message.content):
                return await sanitize_cmd(message, command_boss)
        # general
        elif vaivora_constants.regex.dm.command.prefix.match(message.content):
            # subscribe
            if vaivora_constants.regex.dm.command.cmd_unsub.search(message.content):
                if await check_subscription(message.author, mode="unsubscribe"):
                    await client.send_message(message.author, \
                                              "Your subscription preference for changelogs has been updated: `unsubscribed`.\n")
                else:
                    await client.send_message(message.author, "You are already unsubscribed.\n")
                return True
            # unsubscribe
            elif vaivora_constants.regex.dm.command.cmd_sub.search(message.content):
                if await check_subscription(message.author):
                    await client.send_message(message.author, \
                                              "Your subscription preference for changelogs has been updated: `subscribed`.\n") 
                else:
                    await client.send_message(message.author, "You are already subscribed.\n")
                return True
            # help
            elif vaivora_constants.regex.dm.command.cmd_help.search(message.content):
                return await client.send_message(message.author, 
                                                 vaivora_constants.values.words.message.helpmsg)
        return True
    # debug
    # if "$debug" in message.content:
    #     return await client.send_message(message.author, "server: " + message.server.name + ", id: " + message.server.id + "\n")
    # help message handling
    if vaivora_constants.regex.dm.command.prefix.match(message.content):
        if vaivora_constants.regex.dm.command.cmd_help.match(message.content):
            return await client.send_message(message.channel, message.author.mention + " " + \
                                             vaivora_constants.values.words.message.helpmsg)

    mgmt_ch = vdst[message.server.id].get_channel('management')
    boss_ch = vdst[message.server.id].get_channel('boss')
    # settings handling
    if vaivora_constants.regex.settings.command.prefix.match(message.content):
        if mgmt_ch and not message.channel.mention in mgmt_ch:
            return False
        else:
            return await settings_cmd(message)
    # fun commands handling
    if vaivora_constants.fun.ohoho.search(message.content):
        await client.send_message(message.channel, "https://youtu.be/XzBCBIVC7Qg?t=12s")
        return True
    elif vaivora_constants.fun.meme.match(message.content):
        await client.send_message(message.channel, message.author.mention + " " + "http://i.imgur.com/kW3o6eC.png")
        return True
    elif vaivora_constants.fun.stab2.match(message.content) or vaivora_constants.fun.stab3.match(message.content) or \
      vaivora_constants.fun.stab4.match(message.content) or vaivora_constants.fun.stab5.match(message.content):
        random.seed()
        if int(random.random() * 100) % 17 != 0:
            return True
        try:
            await client.add_reaction(message, "🗡")
            await client.add_reaction(message, "⚔")
            for emoji in message.server.emojis:
                if emoji.name == "Manamana":
                    await client.add_reaction(message, emoji)
                    return True
        except:
            return True
        return True
    # boss commands handling
    if rgx_boss.match(message.content):
        if boss_ch and not message.channel.mention in boss_ch:
            return False
        elif boss_ch:
            return await sanitize_cmd(message, command_boss)
        elif not boss_ch and "timer" in message.channel.name or "boss" in message.channel.name:
            return await sanitize_cmd(message, command_boss)
    #await client.process_commands(message)


# @func:    check_subscription(discord.User, str) : bool
# @arg:
#       user:
#           the user requesting change
#       mode:
#           (default: subscribe)
#           the requested change to subscription to updates
# @return:
#       True if succeeded, False otherwise
async def check_subscription(user, mode="subscribe"):
    file_unsub  = []
    file_sub    = []
    status      = True
    vaivora_version   = vaivora_modules.version.get_current_version()
    try:
        status_hit  = False
        with open(vaivora_constants.values.filenames.unsubbed, 'r') as unsubbed:
            for line in unsubbed:
                if vaivora_constants.regex.dm.command.empty_line.match(line):
                    continue
                if user.id in line and mode == "subscribe":
                    status_hit  = True
                    continue
                elif user.id in line and mode == "unsubscribe":
                    status = False
                    status_hit  = True
                file_unsub.append(line)
        if not status_hit and mode == "unsubscribe":
            file_unsub.append(user.id)
        with open(vaivora_constants.values.filenames.unsubbed, 'w+') as unsubbed:
            if len(file_unsub) == 0:
                pass
            elif len(file_unsub) > 1:
                unsubbed.write('\n'.join(file_unsub[:-1]))
            if len(file_unsub) >= 1:
                unsubbed.write(file_unsub[-1] + "\n")
    except:
        with open(vaivora_constants.values.filenames.unsubbed, 'w+') as f:
            if mode == "unsubscribe":
                f.write(user.id + "\n")
    try:
        status_hit  = False
        with open(vaivora_constants.values.filenames.subbed, 'r') as subbed:
            for line in subbed:
                if vaivora_constants.regex.dm.command.empty_line.match(line):
                    continue
                if user.id in line and mode == "subscribe":
                    status = False
                    status_hit  = True
                elif user.id in line and mode == "unsubscribe":
                    status_hit  = True
                    continue
                file_sub.append(line)
        if not status_hit and mode == "subscribe":
            file_sub.append(user.id)
        with open(vaivora_constants.values.filenames.subbed, 'w+') as subbed:
            if vaivora_constants.regex.dm.command.empty_line.match(line):
                pass
            elif len(file_sub) > 1:
                subbed.write((':' + vaivora_version + '\n').join(file_sub[:-1]))
            if len(file_sub) >= 1:
                subbed.write(file_sub[-1] + ":" + vaivora_version + "\n")
    except:
        with open(vaivora_constants.values.filenames.subbed, 'w+') as f:
            if mode == "subscribe":
                f.write(user.id + ":" + vaivora_version + "\n")
    return status


# @func:    get_unsubscribed() : list
# @return:
#       list of unsubscribed users
async def get_unsubscribed():
    unsubbed    = []
    try:
        with open(vaivora_constants.values.filenames.unsubbed, 'r') as f:
            for line in f:
                unsubbed.append(line.rstrip('\n'))
        return unsubbed
    except:
        return []
    

# @func:    settings_cmd(message) : bool
# @arg:
#       message:
#           the message to process
# @return:
#       True if successful, False otherwise
@client.event
async def settings_cmd(message):
    if not vaivora_constants.regex.settings.command.cmd_all.search(message.content):
        return False
    user_role       = vdst[message.server.id].get_role_user(message.author.id)
    grp_role        = vdst[message.server.id].get_role_group([role.id for role in message.author.roles])
    if user_role:
        user_role_idx   = vaivora_modules.settings.Settings.role_level.index(user_role)
    else:
        user_role_idx   = 0
    if grp_role:
        grp_role_idx    = vaivora_modules.settings.Settings.role_level.index(grp_role)
    else:
        grp_role_idx    = 0
    highest_role    = vaivora_modules.settings.Settings.role_level[user_role_idx if user_role_idx >= grp_role_idx else grp_role_idx]
    command_message = message.content
    command_message = vaivora_constants.regex.settings.command.prefix.sub('', command_message)
    message_args    = dict()
    if highest_role == "none":
        return False # silently deny no role
    try:
        command = splitDblQuotesSpaces(command_message)
    except ValueError:
        return await error(message.author, message.channel, \
                           vaivora_constants.command.syntax.cmd_error_bad_syntax_quote, \
                           vaivora_constants.command.syntax.cmd_settings)
    if command[0] == "help":
        for cmd_frag in vaivora_constants.command.settings.command:
            await client.send_message(message.author, cmd_frag)
            await asyncio.sleep(1)
        return True
    # rebase
    if vaivora_constants.regex.settings.command.cmd_rebase.match(command[0]):
        vdst[message.server.id].rebase_guild_talt()
        await client.send_message(message.channel, message.author.mention + " Guild Talt values have been rebased. Run `$settings get talt` to verify.\n")
        return True   
    # validate
    if vaivora_constants.regex.settings.command.cmd_valid.search(command[0]):
        if vaivora_constants.regex.settings.command.cmd_un.match(command[0]):
            mode = "invalidate"
        else:
            mode = "validate"
        if not message.mentions:
            if not vdst[message.server.id].validate_talt(message.author.id, mode):
                return await error(message.author, message.channel, \
                                   vaivora_constants.command.syntax.cmd_error_unauthorized, \
                                   vaivora_constants.command.syntax.cmd_settings, highest_role)
            await client.send_message(message.channel, message.author.mention + " " + \
                                      "Your command has been successfully recorded.\n" + \
                                      "Member contributions have been " + mode + "d.\n")
            return True
        else:
            errs = []
            for mention in message.mentions:
                mentname = (mention.nick if mention.nick else mention.name)
                if not vdst[message.server.id].validate_talt(message.author.id, mode, mention.id):
                    errs.append(mentname)
            if len(errs) == len(message.mentions):
                return await error(message.author, message.channel, \
                                   vaivora_constants.command.syntax.cmd_error_unauthorized, \
                                   vaivora_constants.command.syntax.cmd_settings, "None")
            elif errs:
                return await error(message.author, message.channel, \
                                   vaivora_constants.command.syntax.cmd_error_bad_settings, \
                                   vaivora_constants.command.syntax.cmd_settings, "mentions", errs)
    if len(command) == 1:
        return await error(message.author, message.channel, \
                           vaivora_constants.command.syntax.cmd_error_bad_syntax, \
                           vaivora_constants.command.syntax.cmd_settings)
    # set & get
    if vaivora_constants.regex.settings.command.cmd_getset.match(command[0]):
        #message_args['command'] = "get" if vaivora_constants.regex.settings.command.cmd_get.search(command[0]) else "set"
        if not vaivora_constants.regex.settings.command.cmd_gs2.search(command[1]):
            return False
        if vaivora_constants.regex.settings.command.cmd_gs23.search(command[1]):
            if not vaivora_constants.regex.settings.command.cmd_gs3.search(command[2]):
                return False
        # get
        if vaivora_constants.regex.settings.command.cmd_get.search(command[0]):
            # get talt
            if vaivora_constants.regex.settings.command.cmd_talt.search(command[1]):
                # get talt, default (guild)
                if len(command) == 2:
                    await client.send_message(message.channel, message.author.mention + " " + \
                                              "This guild currently has " + vdst[message.server.id].get_talt() + " Talt, " + \
                                              "is level " + vdst[message.server.id].get_guild_level() + ", and needs " + \
                                              vdst[message.server.id].get_talt_for_nextlevel() + " Talt to reach the next level.\n")
                    return True
                elif vaivora_constants.regex.settings.command.cmd_temp.match(command[2]):
                    talt_list   = vdst[message.server.id].get_temp_talt()
                    talt_msg    = "This guild currently has the following records temporarily stored: "
                # get talt all
                elif vaivora_constants.regex.settings.command.cmd_tallt.match(command[2]):
                    talt_list   = vdst[message.server.id].get_all_talt()
                    talt_msg    = "This guild thanks the following for contributing: "
                    await client.send_message(message.channel, message.author.mention + " " + \
                                              "This request may take some time. Please wait.\n")
                # get talt, user or users
                else:
                    contribs    = str()
                    for mention in message.mentions:
                        if type(mention) == discord.User or type(mention) == discord.Member:
                            talt_cont = int(vdst[message.server.id].get_talt(user=mention.id))
                            contribs += "\n`" + mention.name + "` has contributed `" + str(talt_cont) + "` Talt, or `" + str(talt_cont*20) + "` Points."
                    if contribs:
                        await client.send_message(message.channel, message.author.mention + contribs)
                    else:
                        await client.send_message(message.channel, message.author.mention + " " + \
                                                  "This guild currently has " + vdst[message.server.id].get_talt() + " Talt, " + \
                                                  "is level " + vdst[message.server.id].get_guild_level() + ", and needs " + \
                                                  vdst[message.server.id].get_talt_for_nextlevel() + " Talt to reach the next level.\n")
                    return True
                if talt_msg:
                    talt_list = sorted(talt_list.items(), key=itemgetter(1), reverse=True)
                    fmtt_list = []
                    for member, talt in talt_list:
                        if talt == 0 or member == "remainder" or member == "guild":
                            continue
                        try:
                            talt_user = await client.get_user_info(member)
                        except:
                            continue
                        fmtt_list.append("#   " + talt_user.name + ": " + str(int(talt)) + " T: " + str(int(talt)*20) + "P")
                    await client.send_message(message.channel, message.author.mention + " " + \
                                              talt_msg + "```python\n" + \
                                              ("\n".join(fmtt_list) if fmtt_list else "*crickets chirping*") + "```\n")
                    return True
            # get role
            elif vaivora_constants.regex.settings.command.cmd_role.search(command[1]):
                temp_users = []
                # get role auth
                if vaivora_constants.regex.settings.command.cmd_role_a.search(command[2]):
                    users = vdst[message.server.id].get_role(role="authorized")
                # get role member
                elif vaivora_constants.regex.settings.command.cmd_role_m.search(command[2]):
                    users = vdst[message.server.id].get_role(role="member")
                # get role boss
                elif vaivora_constants.regex.settings.command.cmd_ch_boss.search(command[2]):
                    users = vdst[message.server.id].get_role(role="boss")
                # get role, default (all)
                else:
                    users = [ ("#  " + usr) for usr in message.server.members ]
                if users:
                    for uid in users:
                        try:
                            uname = discord.utils.get(message.server.roles, mention=uid).name
                        except:
                            try:
                                uname = await client.get_user_info(uid)
                            except:
                                await client.send_message(message.channel, message.author.mention + " " + \
                                                      "(But nothing happened...)\n")
                                return False
                        if uname == None:
                            await client.send_message(message.channel, message.author.mention + " " + \
                                                      "(But nothing happened...)\n")
                            return False
                        uname = "#   " + str(uname)
                        temp_users.append(uname)
                    users = temp_users
                if users and users[0] != None:
                    await client.send_message(message.channel, message.author.mention + \
                                              "\nHere are the `" + command[2] + "` users:```python\n" + \
                                              '\n'.join(users) + "```\n")
                    return True
                else:
                    await client.send_message(message.channel, message.author.mention + " " + \
                                              "(But nothing happened...)\n")
                    return False
            else:
                return await error(message.author, message.channel, \
                                   vaivora_constants.command.syntax.cmd_error_bad_syntax, \
                                   vaivora_constants.command.syntax.cmd_settings, command[1])
        # set
        else:
            # set talt: $settings set talt n [unit] [user...]
            unit    = "Talt"
            if vaivora_constants.regex.settings.command.cmd_talt.search(command[1]):
                if not vaivora_constants.regex.format.matching.numbers.search(command[2]):
                    return await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error_bad_syntax, \
                                       vaivora_constants.command.syntax.cmd_settings, command[2])
                if highest_role == "none":
                    return await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error_unauthorized, \
                                       vaivora_constants.command.syntax.cmd_settings, highest_role)
                # set talt, default (no user): $settings 
                if len(command) >= 3 and len(command) <= 4 and not message.mentions:
                    if len(command) == 3:
                        unit    = "Talt"
                    elif vaivora_constants.regex.settings.command.cmd_tpoint.search(command[2] + " " + command[3]):
                        unit    = "Points"
                    elif vaivora_constants.regex.settings.command.cmd_talts.search(command[2] + " " + command[3]):
                        unit    = "Talt"
                    if not vdst[message.server.id].set_talt(message.author.id, command[2], unit):
                        return await error(message.author, message.channel, \
                                           vaivora_constants.command.syntax.cmd_error_unauthorized, \
                                           vaivora_constants.command.syntax.cmd_settings, highest_role)
                    confirm_msg = msg_talt(message, highest_role, command[2], unit)
                    if not confirm_msg:
                        return await error(message.author, message.channel, \
                                           vaivora_constants.command.syntax.cmd_error_unauthorized, \
                                           vaivora_constants.command.syntax.cmd_settings, "None")
                    await client.send_message(message.channel, message.author.mention + " " + \
                                              vaivora_constants.command.settings.acknowledge + \
                                              "Your changes to the Talt Tracker have been saved.\n" + \
                                              confirm_msg)
                    return True

                elif not message.mentions:
                    return await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error_bad_syntax, \
                                       vaivora_constants.command.syntax.cmd_settings)
                # set talt, points with users: $settings set n unit @user...
                elif message.mentions:
                    if vaivora_constants.regex.settings.command.cmd_tpoint.search(command[2] + " " + command[3]):
                        unit    = "Points"
                    elif vaivora_constants.regex.settings.command.cmd_talts.search(command[2] + " " + command[3]):
                        unit    = "Talt"
                    errs    = []
                    succ    = []
                    for mention in message.mentions:
                        mentname    = (mention.nick if mention.nick else mention.name)
                        if type(mention) == discord.User or type(mention) == discord.Member:
                            if not vdst[message.server.id].set_talt(message.author.id, command[2], unit, mention.id):
                                errs.append(mentname)
                            else:
                                talt    = vdst[message.server.id].get_talt(mention.id)
                                succ.append("`" + command[2] + " " + unit + "` has been modified for `" + mentname + "`; his or her new balance is " + talt + " Talt.")
                        else:
                            errs.append(mentname)
                    if errs and len(errs) == 1 and errs[0] == None:
                        return await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error_unauthorized, \
                                       vaivora_constants.command.syntax.cmd_settings, highest_role)
                    elif errs:
                        return await error(message.author, message.channel, \
                                           vaivora_constants.command.syntax.cmd_error_bad_settings, \
                                           vaivora_constants.command.syntax.cmd_settings, "mentions", errs)
                    else:
                        await client.send_message(message.channel, message.author.mention + " " + \
                                                  vaivora_constants.command.settings.acknowledge + \
                                                  "Your changes to the Talt Tracker have been saved.\n" + \
                                                  '\n'.join(succ))
                        return True
                # set talt, points; self: $settings set n unit
                elif not vdst[message.server.id].set_talt(message.author.id, command[2], unit):
                    return await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error_bad_syntax, \
                                       vaivora_constants.command.syntax.cmd_settings, message.id)
                else:
                    confirm_msg = msg_talt(message, highest_role, command[2], unit)
                    if not confirm_msg:
                        return await error(message.author, message.channel, \
                                           vaivora_constants.command.syntax.cmd_error_unauthorized, \
                                           vaivora_constants.command.syntax.cmd_settings, "None")
                    await client.send_message(message.channel, message.author.mention + " " + \
                                              vaivora_constants.command.settings.acknowledge + \
                                              "Your changes to the Talt Tracker have been saved.\n" + \
                                              confirm_msg)
                    return True
            # set role
            elif vaivora_constants.regex.settings.command.cmd_role.search(command[1]):
                if highest_role != "authorized" and highest_role != "super authorized":
                    return await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error_unauthorized, \
                                       vaivora_constants.command.syntax.cmd_settings, highest_role)
                if not vaivora_constants.regex.settings.command.cmd_roles.match(command[2]):
                    return await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error_bad_roles, \
                                       vaivora_constants.command.syntax.cmd_settings, command[2])
                errs    = []
                for mention in message.mentions:
                    utype = "users"
                    id_change = mention.id
                    mentname = mention.nick if mention.nick else mention.name
                    if not vdst[message.server.id].change_role(id_change, utype, command[2]):
                        errs.append(mentname)
                for mention in message.role_mentions:
                    utype = "group"
                    id_change = mention.mention
                    mentname = mention.name
                    if not vdst[message.server.id].change_role(id_change, utype, command[2]):
                        errs.append(mentname)
                if errs:
                    return await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error_bad_settings, \
                                       vaivora_constants.command.syntax.cmd_settings, "mentions", errs)
                elif not message.mentions and not message.role_mentions:
                    await client.send_message(message.channel, message.author.mention + " " + \
                                              "(But nothing happened...)\n")
                    return False
                else:
                    await client.send_message(message.channel, message.author.mention + " " + \
                                              vaivora_constants.command.settings.acknowledge + \
                                              "Your mentions have all been processed.\n" + \
                                              "Users are now of role `" + command[2] + "`.\n")
                    return True
            # set channel
            elif vaivora_constants.regex.settings.command.cmd_gs23.match(command[1]):
                if not vaivora_constants.regex.settings.command.cmd_gs3.match(command[2]):
                    return await error(message.author, message.client, \
                                       vaivora_constants.command.syntax.cmd_error_bad_channel, \
                                       vaivora_constants.command.syntax.cmd_settings, command[2])
                if vaivora_constants.regex.settings.command.cmd_ch_boss.match(command[2]):
                    ch_type = "boss"
                else:
                    ch_type = "management"
                errs = []
                succ = []
                if type(command[3:]) == list:
                    list_ch = command[3:]
                else:
                    list_ch = [(command[3],)]
                for pos_ch in list_ch:
                    #pos_ch = vaivora_constants.regex.settings.command.abrackets.sub('', pos_ch)
                    if not vaivora_constants.regex.settings.command.cmd_ch.match(pos_ch):
                        errs.append(pos_ch)
                    else:
                        vdst[message.server.id].set_channel(ch_type, pos_ch)
                if errs:
                    return await error(message.author, message.channel, \
                               vaivora_constants.command.syntax.cmd_error_bad_settings, \
                               vaivora_constants.command.syntax.cmd_settings, "channels", errs)
                else:
                    await client.send_message(message.channel, message.author.mention + " " + \
                                              vaivora_constants.command.settings.acknowledge + \
                                              "Your new " + ch_type + " channels are set.\n")
                    return True
            # set guild LV CUR
            elif vaivora_constants.regex.settings.command.cmd_guild.match(command[1]):
                if vaivora_constants.regex.settings.command.cmd_numbers.match(command[2]):
                    if vaivora_constants.regex.settings.command.cmd_numbers.match(command[3]):
                        if not vdst[message.server.id].set_remainder_talt(command[2], command[3]):
                            return await error(message.author, message.channel, \
                                               vaivora_constants.command.syntax.cmd_error_bad_settings, \
                                               vaivora_constants.command.syntax.cmd_settings, "`guild command`", (command[2:4]))
                        await client.send_message(message.channel, message.author.mention + " " + \
                                                  vaivora_constants.command.settings.acknowledge + \
                                                  "Your guild has been set to Lv." + command[2] + "; you need " + \
                                                  vdst[message.server.id].get_talt_for_nextlevel() + " Talt for next level.\n")
    elif vaivora_constants.regex.settings.command.cmd_add.search(command[0]):
        unit    = "Talt"
        if vaivora_constants.regex.settings.command.cmd_talt.search(command[1]):
            if not vaivora_constants.regex.format.matching.numbers.search(command[2]):
                return await error(message.author, message.channel, \
                                   vaivora_constants.command.syntax.cmd_error_bad_syntax, \
                                   vaivora_constants.command.syntax.cmd_settings, command[2])
            if highest_role == "none":
                return await error(message.author, message.channel, \
                                   vaivora_constants.command.syntax.cmd_error_unauthorized, \
                                   vaivora_constants.command.syntax.cmd_settings, highest_role)
            # add talt, default (no user): $settings 
            if len(command) >= 3 and len(command) <= 4 and not message.mentions:
                if len(command) == 3:
                    unit    = "Talt"
                elif vaivora_constants.regex.settings.command.cmd_tpoint.search(command[2] + " " + command[3]):
                    unit    = "Points"
                elif vaivora_constants.regex.settings.command.cmd_talts.search(command[2] + " " + command[3]):
                    unit    = "Talt"
                if not vdst[message.server.id].add_talt(message.author.id, command[2], unit):
                    return await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error_unauthorized, \
                                       vaivora_constants.command.syntax.cmd_settings, highest_role)
                confirm_msg = msg_talt(message, highest_role, command[2], unit)
                if not confirm_msg:
                    return await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error_unauthorized, \
                                       vaivora_constants.command.syntax.cmd_settings, "None")
                await client.send_message(message.channel, message.author.mention + " " + \
                                          vaivora_constants.command.settings.acknowledge + \
                                          "Your changes to the Talt Tracker have been saved.\n" + \
                                          confirm_msg)
                return True

            elif not message.mentions:
                return await error(message.author, message.channel, \
                                   vaivora_constants.command.syntax.cmd_error_bad_syntax, \
                                   vaivora_constants.command.syntax.cmd_settings)
            # set talt, points with users: $settings set n unit @user...
            elif message.mentions:
                if vaivora_constants.regex.settings.command.cmd_tpoint.search(command[2] + " " + command[3]):
                    unit    = "Points"
                elif vaivora_constants.regex.settings.command.cmd_talts.search(command[2] + " " + command[3]):
                    unit    = "Talt"
                errs    = []
                succ    = []
                for mention in message.mentions:
                    if type(mention) == discord.User or type(mention) == discord.Member:
                        mentname = (mention.nick if mention.nick else mention.name)
                        if not vdst[message.server.id].add_talt(message.author.id, command[2], unit, mention.id):
                            errs.append(mentname)
                        else:
                            talt    = vdst[message.server.id].get_talt(mention.id)
                            succ.append("`" + command[2] + " " + unit + "` has been credited to `" + mentname + "`; his or her new balance is " + talt + " Talt.")
                    else:
                        errs.append(mentname)
                if errs and len(errs) == 1 and errs[0] == None:
                    return await error(message.author, message.channel, \
                                   vaivora_constants.command.syntax.cmd_error_unauthorized, \
                                   vaivora_constants.command.syntax.cmd_settings, highest_role)
                elif errs:
                    return await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error_bad_settings, \
                                       vaivora_constants.command.syntax.cmd_settings, "mentions", errs)
                else:
                    await client.send_message(message.channel, message.author.mention + " " + \
                                              vaivora_constants.command.settings.acknowledge + \
                                              "Your changes to the Talt Tracker have been saved.\n" + \
                                              '\n'.join(succ))
                    return True
            # set talt, points; self: $settings set n unit
            elif not vdst[message.server.id].add_talt(message.author.id, command[2], unit):
                return await error(message.author, message.channel, \
                                   vaivora_constants.command.syntax.cmd_error_bad_syntax, \
                                   vaivora_constants.command.syntax.cmd_settings, message.id)
            else:
                confirm_msg = msg_talt(message, highest_role, command[2], unit)
                if not confirm_msg:
                    return await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error_unauthorized, \
                                       vaivora_constants.command.syntax.cmd_settings, "None")
                await client.send_message(message.channel, message.author.mention + " " + \
                                          vaivora_constants.command.settings.acknowledge + \
                                          "Your changes to the Talt Tracker have been saved.\n" + \
                                          confirm_msg)
                return True
    # promote & demote
    elif vaivora_constants.regex.settings.command.cmd_prdm.search(command[1]):
        if highest_role != "authorized" and highest_role != "super authorized":
            return await error(message.author, message.channel, \
                               vaivora_constants.command.syntax.cmd_error_unauthorized, \
                               vaivora_constants.command.syntax.cmd_settings, highest_role)
        if not message.mentions and not message.role_mentions:
            return await error(message.author, message.channel, \
                               vaivora_constants.command.syntax.cmd_error_no_users, \
                               vaivora_constants.command.syntax.cmd_settings)
        if vaivora_constants.regex.settings.command.cmd_pr.search(command[1]):
            mode = "promote"
        else:
            mode = "demote"
        errs = []
        for mention in (message.mentions + message.role_mentions):
            if type(mention) == discord.User or type(mention) == discord.Member:
                mentname = (mention.nick if mention.nick else mention.name)
                utype = "users"
            else:
                mentname = mention.name
                utype = "group"
            ment_role = vdst[message.server.id].get_role_user(mention.id)
            if mode == "promote" and ment_role == None:
                vdst[message.server.id].change_role(mention.id, utype, "member")
            elif mode == "promote" and ment_role == "member":
                vdst[message.server.id].change_role(mention.id, utype, "authorized")
            elif mode == "demote" and ment_role == "member":
                vdst[message.server.id].change_role(mention.id, utype)
            elif mode == "demote" and ment_role == "authorized":
                vdst[message.server.id].change_role(mention.id, utype, "member")
            else:
                errs.append(mentname)
        if errs:
            return await error(message.author, message.channel, \
                               vaivora_constants.command.syntax.cmd_error_bad_settings, \
                               vaivora_constants.command.syntax.cmd_settings, "mentions", errs)
        else:
            await client.send_message(message.channel, message.author.mention + " " + \
                                      "Your mentions have all been processed.\n" + \
                                      "Users have been " + mode + "d.\n")
            return True
    # rm
    elif vaivora_constants.regex.settings.command.cmd_rm.match(command[0]):
        if highest_role != "authorized" and highest_role != "super authorized":
            return await error(message.author, message.channel, \
                               vaivora_constants.command.syntax.cmd_error_unauthorized, \
                               vaivora_constants.command.syntax.cmd_settings, highest_role)
        # rm boss users
        if vaivora_constants.regex.settings.command.cmd_role.search(command[1]):
            if not vaivora_constants.regex.settings.command.cmd_ch_boss.match(command[2]):
                return await error(message.author, message.channel, \
                                   vaivora_constants.command.syntax.cmd_error_bad_roles, \
                                   vaivora_constants.command.syntax.cmd_settings, command[2])
            errs    = []
            for mention in message.mentions:
                mentname = (mention.nick if mention.nick else mention.name)
                if not vdst[message.server.id].rm_boss(mention.id):
                    errs.append(mentname)
            if errs:
                return await error(message.author, message.channel, \
                                   vaivora_constants.command.syntax.cmd_error_bad_settings, \
                                   vaivora_constants.command.syntax.cmd_settings, "mentions", errs)
            else:
                await client.send_message(message.channel, message.author.mention + " " + \
                                          "Your mentions have all been processed.\n" + \
                                          "Users have been removed from `boss` mentions.\n")
                return True
        # rm channel
        elif vaivora_constants.regex.settings.command.cmd_gs23.match(command[1]):
            if not vaivora_constants.regex.settings.command.cmd_gs3.match(command[2]):
                return await error(message.author, message.client, \
                                   vaivora_constants.command.syntax.cmd_error_bad_channel, \
                                   vaivora_constants.command.syntax.cmd_settings, command[2])
            if vaivora_constants.regex.settings.command.cmd_ch_boss.match(command[2]):
                ch_type = "boss"
            else:
                ch_type = "management"
            errs = []
            succ = []
            if type(command[3:]) == list:
                list_ch = command[3:]
            else:
                list_ch = [command[3]]
            for pos_ch in list_ch:
                if not vaivora_constants.regex.settings.command.cmd_ch.match(pos_ch):
                    errs.append(pos_ch)
                else:
                    vdst[message.server.id].rm_channel(ch_type, pos_ch)
                    succ.append(pos_ch)
            if succ:
                await client.send_message(message.channel, message.author.mention + " " + \
                                          vaivora_constants.command.boss.acknowledge + \
                                          " ".join(succ) + " have been removed from " + ch_type + " channels.\n")
            if errs:
                return await error(message.author, message.channel, \
                                   vaivora_constants.command.syntax.cmd_error_bad_settings, \
                                   vaivora_constants.command.syntax.cmd_settings, "channels", errs)
            else:
                return True
    # reset
    elif vaivora_constants.regex.settings.command.cmd_reset.search(command[0]):
        if vaivora_constants.regex.settings.command.cmd_talt.search(command[1]):
            if not message.mentions:
                vdst[message.server.id].reset_talt(message.author.id)
                await client.send_message(message.channel, message.author.mention + " " + \
                                          "You have reset your own Talt contribution.\n")
                return True
            elif highest_role != "authorized" and highest_role != "super authorized":
                return await error(message.author, message.channel, \
                                   vaivora_constants.command.syntax.cmd_error_unauthorized, \
                                   vaivora_constants.command.syntax.cmd_settings, highest_role)
            else:
                for mention in message.mentions:
                    vdst[message.server.id].reset_talt(mention.id)
                    await client.send_message(message.channel, message.author.mention + " " + \
                                              "Your command has been processed.\n" + \
                                              "You have reset the Talt contributions of the users mentioned.\n")
                    return True

####
#             


def msg_talt(message, highest_role, taltn, unit):
    if highest_role == "authorized" or highest_role == "super authorized":
        talt    = vdst[message.server.id].get_talt(message.author.id)
        confirm_msg = "`" + taltn + " " + unit + "` "
        confirm_msg += ("have" if int(taltn) > 1 else "has") + " been credited to your account. Your new balance is: `"
        confirm_msg += str(int(talt))
        confirm_msg += " Talt`.\n"
    elif highest_role == "member":
        talt    = vdst[message.server.id].get_talt(message.author.id)
        confirm_msg = "`" + taltn + " " + unit + "` "
        confirm_msg += ("have" if int(taltn) > 1 else "has") + " been temporarily recorded. Your balance, once confirmed, will be: `"
        confirm_msg += str(int(talt) + int(taltn))
        confirm_msg += " Talt.` (Currently: `" + str(talt) + "Talt.`)\n"
    else:
        confirm_msg = ""
    return confirm_msg


    
# @func:    sanitize_cmd(str, str) : void
# @arg:
#       message : discord.Message
#           The message to sanitize
#       command_type : str
#           command_boss        = "boss"
#           command_settings    = "settings"
@client.event
async def sanitize_cmd(message, command_type):
    cmd_message =   to_sanitize.sub('', message.content)
    cmd_message =   cmd_message.lower()
    try:
        command =   splitDblQuotesSpaces(cmd_message)
    except ValueError:
        await client.send_message(message.author if not message.server else message.channel, \
                                  "Your command for `$" + command_type + "` had misused quotes somewhere.\n")
        return False

    if len(command) == 1:
        return

    command     =   command[1:]

    if not message.server or rgx_help.match(command[0]):
        server_id   =   message.author.id
        msg_ch_id   =   message.author
        msg_channel =   message.author
        msg_prefix  =   ""
    else:
        server_id   =   message.server.id
        msg_ch_id   =   message.channel.id
        msg_channel =   message.channel
        msg_prefix  =   message.author.mention + " "
    
    if command_type == command_boss:
        return_msg  = vaivora_modules.boss.process_command(server_id, msg_ch_id, command)
    elif command_type == command_settings:
        return_msg  = vaivora_modules.settings.process_commands(commmand)
    else:
        return # command was incorrect

    await client.send_message(msg_channel, msg_prefix + return_msg[0])
    if len(return_msg) > 1:
        for msg_frag in return_msg[1:]:
            await asyncio.sleep(1)
            await client.send_message(msg_channel, msg_frag)



# begin periodic database check
####

# @func:    check_databases() : void
#       Checks databases routinely, by minute.
async def check_databases():
    while first_run:
        await asyncio.sleep(5)
    print('Startup completed; starting check_database')
    results         =   dict()
    minutes         =   dict()
    no_repeat       =   list()
    today           =   datetime.today() # check on first launch

    while not client.is_closed:
        await asyncio.sleep(59)
        print(datetime.today().strftime("%Y/%m/%d %H:%M"), "- Valid DBs:", len(vdbs))

        # prune no-repeats
        purged      =   list()
        if len(minutes) > 0:
            for rec_hash, rec_mins in minutes.items():
                mins_now    =   datetime.now().minute
                # e.g. 48 > 03 (if record was 1:03 and time now is 12:48), passes conds 1 & 2 but fails cond 3
                if rec_mins < mins_now and (mins_now-rec_mins) > 0 and (mins_now-rec_mins+15+1) < 60:
                    no_repeat.remove(rec_hash)
                    purged.append(rec_hash)

        for purge in purged:
            try:
                del minutes[purge]
            except:
                continue

        for vdb_id, valid_db in vdbs.items():
            loop_time = datetime.today()
            print(loop_time.strftime("%H:%M"), "- in DB:", vdb_id)
            results[vdb_id] = []
            if today.day != loop_time.day:
                today = loop_time
            
            # check all timers
            message_to_send   = list()
            cur_channel       = str()
            results[vdb_id]   = valid_db.check_db_boss()

            # empty; dismiss
            if not results[vdb_id]:
                continue

            # sort by time - yyyy, mm, dd, hh, mm
            results[vdb_id].sort(key=itemgetter(5,6,7,8,9))

            # iterate 
            for result in results[vdb_id]:
                cur_channel     =   result[4]
                list_time       =   [ int(t) for t in result[5:10] ]
                record_info     =   [ str(r) for r in result[0:5] ]

                entry_time      =   datetime(*list_time)
                record          =   vaivora_modules.boss.process_record(record_info[0], record_info[3], entry_time, record_info[2], record_info[1])
                #                   channel           :    boss              :                       2017/01/01 12:00      :    channel
                record2byte     =   record_info[4] + ":" + record_info[0] + ":" + entry_time.strftime("%Y/%m/%d %H:%M") + ":" + record_info[1]
                record2byte     =   bytearray(record2byte, 'utf-8')
                hashedblake     =   blake2b(digest_size=48)
                hashedblake.update(record2byte)
                hashed_record   =   hashedblake.hexdigest()
                
                if hashed_record in no_repeat:
                    continue

                time_diff       =   entry_time - datetime.now() + timedelta(hours=-3)

                # process time difference
                if time_diff.days < 0:
                    continue

                # append record to message queue
                if time_diff.seconds < 900 and time_diff.days == 0:
                    no_repeat.append(hashed_record)
                    message_to_send.append([record, record_info[4],])
                    minutes[str(hashed_record)]     =   entry_time.minute

            # empty record for this server
            if len(message_to_send) == 0:
                continue 

            role_str = str()

            # compare roles against server
            srv = client.get_server(vdb_id)
            for uid in vdst[vdb_id].get_role("boss"):
                try:    
                    # group mention
                    if discord.utils.get(srv.roles, mention=uid):
                        role_str    += uid + " "

                    # user mention
                    else:
                        boss_user   = await client.get_user_info(uid)
                        role_str    += boss_user.mention + " "

                except:
                    try:
                        # user mention
                        boss_user   = await client.get_user_info(uid)
                        role_str    += boss_user.mention + " "
                    except:
                        continue

            # no roles detected; use empty string
            role_str = role_str if role_str else ""

            # replace time_str with server setting warning, eventually
            time_str = "15"

            cur_channel         =   ''
            discord_message     =   ''
            for message in message_to_send:
                if cur_channel != message[-1]:
                    if cur_channel:
                        discord_message += "```"
                        await client.send_message(srv.get_channel(cur_channel), discord_message)
                        discord_message = ''
                    cur_channel = message[-1]

                    # replace time_str with server setting warning, eventually
                    discord_message = role_str + " The following bosses will spawn within " + time_str + " minutes: ```python\n"
                discord_message += message[0]
            # flush
            discord_message += "```"
            await client.send_message(srv.get_channel(cur_channel), discord_message)
            discord_message = ''
        #await client.process_commands(message)
        await asyncio.sleep(1)
####
# end of periodic database check



# begin async functions for vaivora_modules.boss
####

# @func:    check_boss(str) : str
# @arg:
#       boss:
#           the boss to check
# @return:
#       a str containing the boss idx
async def check_boss(boss):
    return vaivora_modules.boss.check_boss(boss)

# @func:    check_maps(str, str) : str
# @arg:
#       boss:
#           the boss to check
# @return:
#       a str containing the maps to boss
async def check_maps(maps, boss):
    return vaivora_modules.boss.check_maps(maps, boss)

####
# end of async functions for vaivora_modules.boss



# error handling
####

# @func:  error(args**) : int
#       begin code for error message printing to user
# @arg:
#       user:
#           Discord.user
#       channel:
#           server channel
#       etype:
#           [e]rror type
#       ecmd:
#           [e]rror (invoked by) command
#       msg:
#           (default: '') (optional)
#           message for better error clarity
#       xmsg:
#           (default: '') (optional)
#           secondary message for better error clarity
# @return:
#       -1:
#           BROAD:  the command was correctly formed but the argument is too broad
#       -2:
#           WRONG:  the command was correctly formed but could not validate arguments
#       -127:
#           SYNTAX: malformed command: quote mismatch, argument count
async def error(user, channel, etype, ecmd, msg='', xmsg=''):
    # get the user in mentionable string
    user_name = user.mention
    # convert args
    if msg:
        msg   = str(msg)
    if xmsg:
        xmsg  = str(xmsg)
    # prepare a list to send message
    ret_msg   = list()

    # boss command only
    if ecmd == vaivora_constants.command.syntax.cmd_boss:
        # broad
        if etype == vaivora_constants.command.syntax.cmd_error_ambiguous:
            ret_msg.append(user_name + the_following_argument('name') + msg + \
                           ") for `$boss` has multiple matching spawn points:\n")
            ret_msg.append(vaivora_constants.command.syntax.code_block)
            ret_msg.append('\n'.join(vaivora_constants.command.boss.boss_locs[msg]))
            ret_msg.append(vaivora_constants.command.syntax.code_block)
            ret_msg.append(vaivora_constants.command.syntax.cmd_error_cmd_ambiguous)
            ret_msg.append(vaivora_constants.command.syntax.cmd_error_record_map)
            error_code = vaivora_constants.values.error_codes.broad
        elif etype == vaivora_constants.command.syntax.cmd_error_unknown:
            ret_msg.append(user_name + " I'm sorry. Your command failed for unknown reasons.\n" + \
                           "This command failure has been recorded.\n" + \
                           "Please try again shortly.\n")
            with open('wings_of_vaivora-error.txt', 'a') as f:
                f.write(str(datetime.today()) + ":" + user_name + " sent a wrong/malformed command.\n")
            error_code = vaivora_constants.values.error_codes.wrong
        # unknown boss
        elif etype == vaivora_constants.command.syntax.cmd_error_bad_boss_name:
            ret_msg.append(user_name + the_following_argument('name', msg) + \
                           " is invalid for `$boss`. This is a list of bosses you may use:\n")
            ret_msg.append(vaivora_constants.command.syntax.code_block + "python")
            ret_msg.append("#   " + '\n#   '.join(vaivora_constants.command.boss.bosses))
            ret_msg.append(vaivora_constants.command.syntax.code_block)
            ret_msg.append(vaivora_constants.command.syntax.cmd_error_record_name)
            error_code = vaivora_constants.values.error_codes.wrong
        elif etype == vaivora_constants.command.syntax.cmd_error_bad_boss_status:
            ret_msg.append(user_name + the_following_argument('status', msg) + \
                           ") is invalid for `$boss`. You may not select `anchored` for its status.\n")
            error_code = vaivora_constants.values.error_codes.wrong
        elif etype == vaivora_constants.command.syntax.cmd_error_bad_boss_map:
            try_msg = list()
            try_msg.append(user_name + the_following_argument('map', msg) + \
                           (msg if msg == '' else "(number)") + " is invalid for `$boss`.")
            try: # make sure the data is valid by `try`ing
                try_msg.append(vaivora_modules.boss.get_maps(xmsg))
                try_msg.append(vaivora_constants.command.syntax.cmd_error_record_map)
                # seems to have succeeded, so extend to original
                ret_msg.extend(try_msg)
                error_code = vaivora_constants.values.error_codes.wrong
            except: # boss not found! 
               ret_msg.append(user_name + " " + vaivora_constants.command.syntax.debug_msg)
               ret_msg.append(vaivora_constants.command.syntax.cmd_error_cmd_malformed)
               error_code = vaivora_constants.values.error_codes.syntax
               with open(vaivora_constants.values.filenames.debug_file, 'a') as f:
                   f.write(str(datetime.today()) + ":" + user_name + " typed " + xmsg + " for boss.\n")
        elif etype == vaivora_constants.command.syntax.cmd_error_bad_boss_channel:
            ret_msg.append(user_name + the_following_argument('channel', msg) + \
                           " (number) is invalid for `$boss`. " + xmsg + " is a field boss, thus " + \
                           "variants that spawn on channels other than 1 (or other maps) are considered world bosses " + \
                           "with unpredictable spawns.\n")
            error_code = vaivora_constants.values.error_codes.wrong
        elif etype == vaivora_constants.command.syntax.cmd_error_bad_boss_time:
            ret_msg.append(user_name + the_following_argument('time', msg) + \
                           " is invalid for `$boss`.\n")
            ret_msg.append("Omit spaces; record in 12H (with AM/PM) or 24H time.\n")
            ret_msg.append(vaivora_constants.command.syntax.cmd_error_cmd_malformed)
            error_code = vaivora_constants.values.error_codes.wrong
        elif etype == vaivora_constants.command.syntax.cmd_error_bad_boss_time_wrap:
            ret_msg.append(user_name + the_following_argument('time', msg) + \
                           " overlaps too closely with an existing record.\n")
            ret_msg.append(vaivora_constants.command.syntax.cmd_error_cmd_wrong)
            error_code = vaivora_constants.values.error_codes.wrong
        elif etype == vaivora_constants.command.syntax.cmd_error_bad_boss_status:
            ret_msg.append(user_name + the_following_argument('status', 'anchored') + \
                           " is invalid for `$boss`.\n" +
                           "You cannot anchor events or bosses of this kind.\n")
            error_code = vaivora_constants.values.error_codes.wrong
        elif etype == vaivora_constants.command.syntax.cmd_error_bad_syntax_arg_ct:
            ret_msg.append(user_name + " Your command for `$boss` had too few arguments.\n" + \
                           "Expected: 3 to 4; got: " + msg + ".\n")
            ret_msg.append(vaivora_constants.command.syntax.cmd_error_cmd_malformed)
            error_code = vaivora_constants.values.error_codes.syntax
        elif etype == vaivora_constants.command.syntax.cmd_error_bad_syntax_quote:
            ret_msg.append(user_name + " Your command for `$boss` had misused quotes somewhere.\n")
            ret_msg.append(vaivora_constants.command.syntax.cmd_error_cmd_malformed)
            error_code = vaivora_constants.values.error_codes.syntax
        elif etype == vaivora_constants.command.syntax.cmd_error_bad_syntax:
            ret_msg.append(user_name + " Your command could not be parsed. Re-check the syntax, and try again.\n" + \
                           ("Message: " + msg) if msg else "")
            ret_msg.append(vaivora_constants.command.syntax.cmd_error_cmd_malformed)
            error_code = vaivora_constants.values.error_codes.syntax
        else:
            ret_msg.append(user_name + " " + vaivora_constants.command.syntax.debug_msg + "\n" + etype)
            ret_msg.append(vaivora_constants.command.syntax.cmd_error_cmd_malformed)
            error_code = vaivora_constants.values.error_codes.syntax
            await client.send_message(channel, '\n'.join(ret_msg))
            return error_code
        # end of conditionals for vaivora_constants.command.syntax.cmd_boss
        # begin common return for $boss
        ret_msg.append("For syntax: `$boss help`")
        await client.send_message(channel, '\n'.join(ret_msg))
        return error_code
        # end of common return for $boss
    elif ecmd == vaivora_constants.command.syntax.cmd_settings:
        if etype == vaivora_constants.command.syntax.cmd_error_unauthorized:
            ret_msg.append(user_name + " Your command failed because your user level is too low. User level: " + msg + "\n")
            ret_msg.append(vaivora_constants.command.syntax.cmd_error_unauthorized)
            error_code = vaivora_constants.values.error_codes.unauth
        elif etype == vaivora_constants.command.syntax.cmd_error_bad_syntax:
            ret_msg.append(user_name + " Your command could not be parsed. Re-check the syntax, and try again.\n" + \
                           ("Message: " + msg) if msg else "")
            ret_msg.append(vaivora_constants.command.syntax.cmd_error_cmd_malformed)
            error_code = vaivora_constants.values.error_codes.syntax
        elif etype == vaivora_constants.command.syntax.cmd_error_no_users:
            ret_msg.append(user_name + " You need to enter at least one user.\n")
            ret_msg.append(vaivora_constants.command.syntax.cmd_error_no_users)
            error_code = vaivora_constants.values.error_codes.syntax
        elif etype == vaivora_constants.command.syntax.cmd_error_bad_settings:
            ret_msg.append(user_name + " Your following " + msg + " could not be processed: ```\n")
            ret_msg.append(('\n'.join(xmsg) if type(xmsg) == list else xmsg) + "```\n")
            ret_msg.append("Check the Vaivora settings of these " + msg + ".\n")
            error_code = vaivora_constants.values.error_codes.wrong
        elif etype == vaivora_constants.command.syntax.cmd_error_bad_roles:
            ret_msg.append(user_name + " You used an incorrect role. Valid roles are `authorized` and `member`.\n")
            ret_msg.append("You entered: " + msg + "\n")
            error_code = vaivora_constants.values.error_codes.wrong
        elif etype == vaivora_constants.command.syntax.cmd_error_bad_channel:
            ret_msg.append(user_name + " You used an incorrect channel. Valid channels are `boss` and `management`.\n")
            ret_msg.append("You entered: " + msg + "\n")
            error_code = vaivora_constants.values.error_codes.wrong
        elif etype == vaivora_constants.command.syntax.cmd_error_not_mgmt_channel:
            ret_msg.append(user_name + " You cannot use this command in channel: " + msg + "\n")
            if xmsg:
                ret_msg.append("You are only permitted to use `setting` commands in: ```\n")
                ret_msg.append('\n'.join(xmsg) + "```")
            error_code = vaivora_constants.values.error_codes.wrong
        else:
            ret_msg.append(user_name + " " + vaivora_constants.command.syntax.debug_msg + "\n" + etype)
            ret_msg.append(vaivora_constants.command.syntax.cmd_error_cmd_malformed)
            error_code = vaivora_constants.values.error_codes.syntax
            await client.send_message(channel, '\n'.join(ret_msg))
            return error_code
        ret_msg.append("For syntax: `$settings help`")
        await client.send_message(channel, '\n'.join(ret_msg))
        return error_code
    # todo: reminders, Talt tracking, permissions
    else:
        # todo
        ret_msg.append(user_name + cmd_usage['debug'])
        ret_msg.append(vaivora_constants.command.syntax.cmd_error_cmd_malformed)
        error_code = vaivora_constants.values.error_codes.syntax
        await client.send_message(channel, '\n'.join(ret_msg))
        return error_code 
####
# end of error



# misc
####
# @func:  the_following_argument(str): begin concatenated string
# @arg:
#     arg: str; e.g. boss, map, time
#     val: str; the value of arg
# @return:
#     str, containing message
def the_following_argument(arg, val):
    return " The following argument `" + arg + "` (*" + val + "*)"
# end of the_following_argument
####
#



# begin everything
with open('discordtoken', 'r') as f:
    secret = f.read()

client.loop.create_task(check_databases())
client.run(secret)