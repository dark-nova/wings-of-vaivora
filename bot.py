#!/usr/bin/env python
import discord
import logging
import sqlite3
import shlex
import asyncio
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

to_sanitize         = re.compile(r'[^a-z0-9 .:$",-]', re.IGNORECASE)

# snippet from discord.py docs
# logger = logging.getLogger(vaivora_constants.values.filenames.logger)
# logger.setLevel(logging.WARNING)
# handler = logging.FileHandler(vaivora_constants.values.filenames.log_file, encoding="utf-8")
# handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
# logger.addHandler(handler)

# @func:    on_ready()
# @return:
#   None
@client.event
async def on_ready():
    print("Logging in...")
    print('Successsfully logged in as: ' + client.user.name + '#' + \
          client.user.id + '. Ready!')
    await client.change_presence(game=discord.Game(name="with startup. Wait 5 seconds..."), status=discord.Status.idle)
    valid_dbs = []
    for server in client.servers:
        if server.unavailable:
            continue
        vdbs[server.id]     = vaivora_modules.db.Database(server.id)
        o_id                = server.owner.id
        vdst[server.id]     = vaivora_modules.settings.Settings(server.id, o_id)
    await send_news()
    await asyncio.sleep(3)
    await client.change_presence(game=discord.Game(name="# [$help] or [Vaivora, help] for info"), status=discord.Status.online)
    return

@client.event
async def send_news():
    modified    = False
    temporary   = []
    vaivora_version   = vaivora_modules.version.get_current_version()
    if os.stat(vaivora_constants.values.filenames.welcomed).st_size == 0:
        await write_anew(client.servers)
        return True
    do_not_msg  = await get_unsubscribed()
    with open(vaivora_constants.values.filenames.welcomed, 'r') as original:
        for line in original:
            if not line or line.isspace():
                continue
            try:
                srv_tup = line.split(':')
                srv_ver = srv_tup[1].rstrip('\n')
                srv_sid = srv_tup[0]
                srv_chk = vaivora_modules.version.check_revisions(srv_ver)
                if srv_chk:
                    owner = client.get_server(srv_sid).owner
                    if owner.id in do_not_msg:
                        temporary.append(line)
                    else:
                        modified = True
                        for vaivora_log in vaivora_modules.version.get_changelogs(srv_chk):
                            await client.send_message(owner, vaivora_log)
                        temporary.append(srv_sid + ":" + vaivora_version + "\n") # updated
                else:
                    temporary.append(line)
            except:
                continue
    # write back over
    with open(vaivora_constants.values.filenames.welcomed, 'w') as original:
        for line in temporary:
            original.write(line)

    sub_list    = []
    try:
        with open(vaivora_constants.values.filenames.subbed, 'r') as subbed_users:
            for s_user in subbed_users:
                if not line or line.isspace():
                    continue
                usr_tup = line.split(':')
                usr_ver = srv_tup[1].rstrip('\n')
                usr_sid = srv_tup[0]
                usr_chk = vaivora_modules.version.check_revisions(usr_ver)
                if usr_chk:
                    usr = await client.get_user_info(usr_sid)
                    for vaivora_log in vaivora_modules.version.get_changelogs(usr_chk):
                        #await client.send_message(usr, vaivora_log)
                        pass
                    sub_list.append(usr_sid + ":" + vaivora_version) # updated
                else:
                    sub_list.append(line)
        with open(vaivora_constants.values.filenames.subbed, 'w+') as subbed_users:
            if len(sub_list) == 0:
                pass
            elif len(sub_list) > 1:
                unsubbed.write('\n'.join(sub_list))
            if len(sub_list) >= 1:
                unsubbed.write(sub_list[-1] + "\n")
    except FileNotFoundError:
        pass
    return True


# @func:    write_anew([discord.Server**]) : void
# @arg:
#       servers:
#           a list of servers connected/served by this bot
@client.event
async def write_anew(servers):
    vaivora_version   = vaivora_modules.version.get_current_version()
    with open(vaivora_constants.values.filenames.welcomed, 'a') as original:
        for server in servers:
            original.write(server.id + ':' + vaivora_version)
            await client.send_message(server.owner, vaivora_constants.values.words.message.welcome)
            n_revs = vaivora_modules.version.get_revisions()
            i = 1
            for vaivora_log in vaivora_modules.version.get_changelogs():
                i += 1
                await client.send_message(server.owner, "Changelog " + i + " of " + n_revs + "\n" + \
                                          vaivora_log)
            await client.send_message(server.owner, \
                                      vaivora_modules.version.get_subscription_msg())


# @func:    on_server_available(discord.Server) : bool
# @return:
#       True if ready, False otherwise
@client.event
async def on_server_join(server):
    already           = False
    vaivora_version   = vaivora_modules.version.get_current_version()
    if server.unavailable:
        return False
    server_id         = str(server.id)
    if not re.match(r'[0-9]{18,}', server_id):
        return False # somehow invalid.
    with open(vaivora_constants.values.filenames.valid_db, 'r') as valid_file:
        f = valid_file.read()
    for line in f:
        if server_id in line:
            already   = True
            return True
    if not already:
        vdbs[server_id]     = vaivora_modules.db.Database(server_id)
        o_id                = client.get_server(server_id).owner.id
        vdst[server_id]     = vaivora_modules.settings.Settings(server_id, o_id)
        with open(vaivora_constants.values.filenames.valid_db, 'a') as f:
            f.write(server_id)
            await write_anew([server,])
        # else:
        #     await send_news()
    return True


# @func:    on_message(Discord.message) : bool
#     begin code for message processing
# @arg:
#     message: Discord.message; includes message among sender (Discord.user) and server (Discord.server)
# @return:
#     True if succeeded, False otherwise
@client.event
async def on_message(message):
    await client.wait_until_ready()
    # direct message processing
    if message.author == client.user:
        return True # do not respond to self
    if not message.channel or not message.channel.name:
        # boss help
        if rgx_boss.match(message.content):
            if vaivora_constants.regex.boss.command.arg_help.search(message.content):
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
    elif vaivora_constants.fun.stab.search(message.content):
        await client.add_reaction(message, "🗡")
        await client.add_reaction(message, "⚔")
        for emoji in message.server.emojis:
            if emoji.name == "Manamana":
                await client.add_reaction(message, emoji)
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
        command = shlex.split(command_message)
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
                        talt_user = await client.get_user_info(member)
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
                            uname = await client.get_user_info(uid)
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
                for mention in (message.mentions + message.role_mentions):
                    mentname = (mention.nick if mention.nick else mention.name)
                    if type(mention) == discord.User or type(mention) == discord.Member:
                        utype = "users"
                        id_change = mention.id
                    else:
                        utype = "group"
                        id_change = mention.mention
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
                    list_ch = [command[3]]
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


# @func:    convert_id_to_user(str) : discord.User
# @arg:
#       uid:
#           the user id of the user to retrieve
# @return:
#       the user who has the uid
# def convert_id_to_user(uid):
#     return await client.get_user_info(uid)



# @func:    boss_cmd(discord.Message, bool) : bool
# @arg:
#       message:
#           the message to process
#       pm:
#           (default: False)
#           if the message was a direct message or not
# @return:
# #       True if successful, False otherwise
# @client.event
# async def boss_cmd(message):
#     msg_prefix  =   ""
#     # private dm
#     if not message.server:
#         message_srv     =   message.author.id
#         reply_channel   =   message.author
#     # server channel
#     else:
#         message_srv     =   message.server.id
#         reply_channel   =   message.channel
#         msg_prefix      =   message.author.mention + " "

#     return_msg  =   await sanitize_cmd(message_srv, reply_channel, message, command_boss)

    

    # # strip leading command/arg
    # command_message = vaivora_constants.regex.boss.command.prefix.sub('', command_message)
    # message_args    = dict() # keys(): name, channel, map, time, 
    # boss_channel    = 1
    # maps_idx        = -1
    # # command: list of arguments
    # try:
    #     command = shlex.split(command_message)
    # except ValueError:
    #     return await error(message.author, message.channel, \
    #                        vaivora_constants.command.syntax.cmd_error_bad_syntax_quote, \
    #                        vaivora_constants.command.syntax.cmd_boss)
    # if len(command) < 1 or command[0] == "help" and not pm:
    #     for cmd_frag in vaivora_modules.boss.command:
    #         await client.send_message(message.author, cmd_frag)
    #         await asyncio.sleep(1)
    #     return True
    # elif command[0] == "help" and pm:
    #     for cmd_frag in vaivora_modules.boss.command:
    #         await client.send_message(message.author, cmd_frag)
    #         await asyncio.sleep(1)
    #     return True
    # elif pm:
    #     return False
    # # begin checking validity
    # #     arg validity
    # #         count
    # #             [3,4] - killed/anchored
    # #             [2,3] - erase
    # if len(command) < 2:
    #     return await error(message.author, message.channel, \
    #                        vaivora_constants.command.syntax.cmd_error_bad_syntax, \
    #                        vaivora_constants.command.syntax.cmd_boss, command_message)
    # if (vaivora_constants.regex.boss.status.all_status.match(command[1]) and \
    #     (len(command) < vaivora_constants.command.boss.arg_min or \
    #      len(command) > vaivora_constants.command.boss.arg_max)) or \
    #    (vaivora_constants.regex.boss.command.arg_erase.match(command[1]) and \
    #     (len(command) < vaivora_constants.command.boss.arg_del_min or \
    #      len(command) > vaivora_constants.command.boss.arg_del_max)):
    #     return await error(message.author, message.channel, \
    #                        vaivora_constants.command.syntax.cmd_error_bad_syntax_arg_ct, \
    #                        vaivora_constants.command.syntax.cmd_boss, len(command))
    # #         status
    # if (not vaivora_constants.regex.format.matching.letters.match(command[0]) or \
    #     not (vaivora_constants.regex.boss.status.all_status.match(command[1]) or \
    #          vaivora_constants.regex.boss.command.arg_erase.match(command[1]) or \
    #          vaivora_constants.regex.boss.command.arg_list.match(command[1]) or \
    #          vaivora_constants.regex.boss.command.arg_info.match(command[1]) or \
    #          vaivora_constants.regex.boss.command.arg_boss.match(command[1]))) or \
    #   (vaivora_constants.regex.boss.status.all_status.match(command[1]) and \
    #    not vaivora_constants.regex.format.time.full.match(command[2])):
    #     return await error(message.author, message.channel, \
    #                        vaivora_constants.command.syntax.cmd_error_bad_syntax, \
    #                        vaivora_constants.command.syntax.cmd_boss)
    # #         boss
    # if vaivora_constants.regex.boss.command.arg_all.match(command[0]):
    #     lookup_boss = vaivora_constants.command.boss.bosses
    #     if vaivora_constants.regex.boss.command.arg_boss_w.match(command[1]):
    #         await client.send_message(message.channel, message.author.mention + " " + \
    #                                   vaivora_modules.boss.get_bosses_world())
    #         return True
    #     elif vaivora_constants.regex.boss.command.arg_boss_f.match(command[1]):
    #         await client.send_message(message.channel, message.author.mention + " " + \
    #                                   vaivora_modules.boss.get_bosses_field())
    #         return True
    # else:
    #     boss_idx = await check_boss(command[0])
    #     if boss_idx < 0  or boss_idx >= len(vaivora_constants.command.boss.bosses):
    #         return await error(message.author, message.channel, \
    #                            vaivora_constants.command.syntax.cmd_error_bad_boss_name, \
    #                            vaivora_constants.command.syntax.cmd_boss, command[0])
    #     lookup_boss = [vaivora_constants.command.boss.bosses[boss_idx],]
    # arg_map_idx     = 3 if vaivora_constants.regex.boss.status.all_status.match(command[1]) else 2
    # if len(lookup_boss) == 1 and vaivora_constants.regex.boss.command.arg_info.match(command[1]):
    #     if vaivora_constants.regex.boss.command.arg_syns.match(command[1]):
    #         await client.send_message(message.channel, message.author.mention + " " + \
    #                                   vaivora_modules.boss.get_syns(lookup_boss[0]))
    #     else:
    #         await client.send_message(message.channel, message.author.mention + " " + \
    #                                   vaivora_modules.boss.get_maps(lookup_boss[0]))
    #     return True
    # # boss list
    # if vaivora_constants.regex.boss.command.arg_list.match(command[1]):
    #     valid_boss_records = list()
    #     boss_records = vdbs[command_server].check_db_boss(lookup_boss) # possible return
    #     if not boss_records: # empty
    #         await client.send_message(message.channel, message.author.mention + "  " + \
    #                                   "No results found! Try a different boss.\n")
    #         return True
    #     for boss_record in boss_records:
    #         boss_st     = (boss_record[3] if boss_record[3] == "died" else ("was " + boss_record[3]))
    #         record_date = [int(rec) for rec in boss_record[5:10]]
    #         record_date = datetime(*record_date) + \
    #                       vaivora_constants.values.time.offset.pacific2server
    #         tense = " and "
    #         tense_time = " minutes "
    #         time_diff = datetime.now() + vaivora_constants.values.time.offset.pacific2server - record_date
    #         if int(time_diff.days) >= 0:
    #             tense += "should have respawned at "
    #             tense_time += "ago"
    #             tense_mins = int(time_diff.seconds / 60) + int(time_diff.days)*vaivora_constants.values.time.seconds.in_day
    #         else:
    #             tense += "will respawn " + ("around " if boss_record[3] != "anchored" else "as early as ")
    #             tense_time += "from now"
    #             tense_mins = int((vaivora_constants.values.time.seconds.in_day - time_diff.seconds) / 60)

    #         if tense_mins > 99:
    #             tense_mins = str(int(tense_mins / 60)) + " hours, " + str(tense_mins % 60)
    #             if int(time_diff.days) >= 1:
    #                 tense_mins = str(time_diff.days) + " day(s), " + tense_mins
    #         elif tense_mins < 0:
    #             tense_mins = str(int(24 + tense_mins / 60)) + " hours, " + str(tense_mins % 60)
    #         else:
    #             tense_mins = str(tense_mins)
    #         valid_boss_records.append("\"" + boss_record[0] + "\" " + boss_st + \
    #                                   " in ch." + str(int(boss_record[1])) + tense + \
    #                                   record_date.strftime("%Y/%m/%d \"%H:%M\"") + \
    #                                   " (" + str(tense_mins) + tense_time + ")" + \
    #                                   ".\nLast known map: #   " + boss_record[2])
    #     await client.send_message(message.channel, message.author.mention + " Records: ```python\n" + \
    #                               '\n\n'.join(valid_boss_records) + "\n```")
    #     return True
    # if len(lookup_boss) == 1 and lookup_boss[0] in vaivora_constants.command.boss.bosses_field and len(command) > 3:
    #     boss_channel    = 1
    #     xmsg            = lookup_boss[0] if lookup_boss[0] == "Blasphemous Deathweaver" else ""
    #     try:
    #         maps_idx = await check_maps(command[arg_map_idx], lookup_boss[0])
    #         if maps_idx >= len(vaivora_constants.command.boss.boss_locs[lookup_boss[0]]):
    #             raise
    #     except:
    #         return await error(message.author, message.channel, \
    #                            vaivora_constants.command.syntax.cmd_error_bad_boss_map, \
    #                            vaivora_constants.command.syntax.cmd_boss, xmsg=xmsg)
    # elif len(lookup_boss) == 1 and lookup_boss[0] in vaivora_constants.command.boss.bosses_world:
    #     boss_channel    = 1 if len(command) == arg_map_idx else vaivora_modules.boss.validate_channel(command[arg_map_idx])
    #     maps_idx        = 0
    # else:
    #     boss_channel    = 1
    #     maps_idx        = -1
    # # boss erase
    # if vaivora_constants.regex.boss.command.arg_erase.match(command[1]):
    #     vdbs[command_server].rm_entry_db_boss(lookup_boss, boss_channel)
    #     await client.send_message(message.channel, message.author.mention + " Record successfully erased.\n")
    #     return True
    # # (implicit) boss status
    # if len(lookup_boss) > 1:
    #     return await error(message.author, message.channel, \
    #                        vaivora_constants.command.syntax.cmd_error_bad_boss_name, \
    #                        vaivora_constants.command.syntax.cmd_boss, command[0])
    # message_args['name']    = lookup_boss[0]
    # message_args['channel'] = boss_channel
    # if maps_idx >= 0:
    #     message_args['map'] = vaivora_constants.command.boss.boss_locs[message_args['name']][maps_idx]
    # else:
    #     message_args['map'] = 'N/A'
    # # process time
    # #     antemeridian
    # if   vaivora_constants.regex.format.time.am.search(command[arg_map_idx - 1]):
    #     boss_time   = vaivora_constants.regex.format.time.delim.split(vaivora_constants.regex.format.time.am.sub('', command[arg_map_idx - 1]))
    #     boss_hour   = int(boss_time[0]) % 12
    # #     postmeridian
    # elif vaivora_constants.regex.format.time.pm.search(command[arg_map_idx - 1]):
    #     boss_time   = vaivora_constants.regex.format.time.delim.split(vaivora_constants.regex.format.time.pm.sub('', command[arg_map_idx - 1]))
    #     boss_hour   = (int(boss_time[0]) % 12) + 12
    # #     24h time
    # else:
    #     boss_time   = command[arg_map_idx - 1].split(':')
    #     boss_hour   = int(boss_time[0])
    # if boss_hour > 24:
    #     return await error(message.author, message.channel, \
    #                        vaivora_constants.command.syntax.cmd_error_bad_boss_time, \
    #                        vaivora_constants.command.syntax.cmd_boss, msg=command[arg_map_idx - 1])
    # boss_minutes = int(boss_time[1])
    # original_boss_hour  = boss_hour
    # approx_server_time  = datetime.now() + vaivora_constants.values.time.offset.pacific2server
    # boss_day    = approx_server_time.day if boss_hour <= int(approx_server_time.hour) \
    #                                      else (approx_server_time.day-1)
    # boss_month  = approx_server_time.month
    # boss_year   = approx_server_time.year
    # # late recorded time; correct with -1 day
    # mdate = datetime(boss_year, boss_month, boss_day, hour=boss_hour, minute=boss_minutes)
    # time_diff = approx_server_time-mdate
    # if time_diff.seconds < 0:  #or time_diff.seconds > 64800:
    #     with open(vaivora_constants.values.filenames.debug_file,'a') as f:
    #         f.write("server", message.server, "; time_diff", time_diff, "; mdate", mdate)
    #     return await error(message.author, message.channel, \
    #                        vaivora_constants.command.syntax.cmd_error_bad_boss_time, \
    #                        vaivora_constants.command.syntax.cmd_boss, msg=command[arg_map_idx - 1])
    # wait_time = vaivora_constants.values.time.offset.boss_spawn_04h + \
    #             vaivora_constants.values.time.offset.server2pacific
    # boss_hour = boss_hour + (int(wait_time.seconds) / 3600) # boss_hour in Pacific/local
    # if message_args['name'] in vaivora_constants.command.boss.bosses_events and \
    #   vaivora_constants.regex.boss.status.anchored.match(command[1]):
    #     return await error(message.author, message.channel, \
    #                        vaivora_constants.command.syntax.cmd_error_bad_boss_status, \
    #                        vaivora_constants.command.syntax.cmd_boss, msg=command[1])
    # elif message_args['name'] in vaivora_constants.command.boss.boss_spawn_02h or \
    #   vaivora_constants.regex.boss.status.warning.match(command[1]):
    #     if boss_hour < 2:
    #         boss_hour += 22
    #         boss_day -= 1
    #     else:
    #         boss_hour -= 2
    # elif message_args['name'] in vaivora_constants.command.boss.boss_spawn_16h:
    #     boss_hour += 12 # 12 + 4 = 16
    # elif vaivora_constants.regex.boss.status.anchored.match(command[1]):
    #     boss_hour -= 1
    # if int(boss_hour / 24):
    #     boss_hour = boss_hour % 24
    #     tomorrow = (datetime(boss_year, boss_month, boss_day)+timedelta(days=1))
    #     boss_day = tomorrow.day
    #     boss_month = tomorrow.month
    #     boss_year = tomorrow.year
    # # add them to dict
    # message_args['hour']      = boss_hour
    # message_args['mins']      = boss_minutes
    # message_args['day']       = boss_day
    # message_args['month']     = boss_month
    # message_args['year']      = boss_year
    # message_args['status']    = command[1] # anchored or died
    # message_args['srvchn']    = message.channel.id
    # status = vdbs[command_server].update_db_boss(message_args)
    # if not status: # update_db_boss failed
    #     return await error(message.author, message.channel, \
    #                        vaivora_constants.command.syntax.cmd_error_bad_boss_time_wrap, \
    #                        vaivora_constants.command.syntax.cmd_boss, \
    #                        msg=(datetime(boss_year, boss_month, boss_day, original_boss_hour, boss_minutes).strftime("%Y/%m/%d %H:%M")))
    # await client.send_message(message.channel, message.author.mention + " " + \
    #                           vaivora_constants.command.boss.acknowledge + \
    #                           "```python\n"
    #                           "\"" + message_args['name'] + "\" " + \
    #                           message_args['status'] + " at " + \
    #                           ("0" if original_boss_hour < 10 else "") + \
    #                           str(original_boss_hour) + ":" + \
    #                           ("0" if message_args['mins'] < 10 else "") + \
    #                           str(message_args['mins']) + \
    #                           ", in ch." + str(message_args['channel']) + ": " + \
    #                           (("\"" + message_args['map'] + "\"") if message_args['map'] != "N/A" else "") + "```\n")
    # #await client.process_commands(message)
    # return True # command processed
####
#
    
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
        command =   shlex.split(cmd_message)
    except ValueError:
        return "Your command for `$" + command_type + "` had misused quotes somewhere.\n"

    if len(command) == 1:
        return

    command     =   command[1:]

    if rgx_help.match(command[0]) or not message.server:
        server_id   =   message.author.id
        msg_channel =   message.author
        msg_prefix  =   ""
    else:
        server_id   =   message.server.id
        msg_channel =   message.channel
        msg_prefix  =   message.author.mention + " "
    
    if command_type == command_boss:
        return_msg  = vaivora_modules.boss.process_command(server_id, msg_channel, command)
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
    await client.wait_until_ready()
    results       = dict()
    today         = datetime.today() # check on first launch
    inactive_time = timedelta(0)
    inactive      = False
    while not client.is_closed:
        no_repeat = []
        #await asyncio.sleep(6)
        await asyncio.sleep(59)
        with open(vaivora_constants.values.filenames.no_repeat, 'r') as f:
            for line in f:
                no_repeat.append(line.strip())
        print(datetime.today().strftime("%Y/%m/%d %H:%M"), "- Valid DBs: ", len(vdbs))
        for vdb_id, valid_db in vdbs.items():
            print(datetime.today().strftime("%Y/%m/%d %H:%M"), "- in DB ", vdb_id)
            results[vdb_id] = []
            ####TODO: replace 900 with custom setting for warning
            loop_time = datetime.today()
            if today.day != loop_time.day:
                today = loop_time
            if inactive_time.seconds > 900 and not inactive:
                no_repeat = []
                with open(vaivora_constants.values.filenames.no_repeat_t + today.strftime("_%Y%m%d") + ".txt", "a") as archive:
                    with open(vaivora_constants.values.filenames.no_repeat, "r") as original:
                        for line in original:
                            archive.write(line)
                # erase contents after transferring$setting
                open(vaivora_constants.values.filenames.no_repeat, "w").close()
                inactive = True
            # check all timers
            message_to_send   = list()
            cur_channel       = str()
            results[vdb_id]   = valid_db.check_db_boss()
            # empty; dismiss
            if not results[vdb_id]:
                continue
            # sort by time - yyyy, mm, dd, hh, mm
            results[vdb_id].sort(key=itemgetter(5,6,7,8,9))
            for result in results[vdb_id]:
                message_to_send   = list()
                cur_channel       = str()
                list_time = [ int(t) for t in result[5:10] ]
                try:
                    entry_time    = datetime(*list_time)
                except:
                    # invalid entry
                    ####TODO: remove entry
                    continue
                entry_time_east   = entry_time + vaivora_constants.values.time.offset.pacific2server
                time_diff         = entry_time - datetime.now()
                if time_diff.days < 0:
                    continue
                ####TODO: replace "900" with custom setting interval
                if time_diff.seconds < 900 and time_diff.days == 0:
                    result        = [ str(r) for r in result ]
                    boss_entry    = []
                    boss_entry.append(vaivora_modules.utils.format_message_boss(result[0], result[3], entry_time_east, result[2], result[1]))
                    boss_entry.append(result[4],)
                    boss_rec      = result[4] + ":" + result[0] + ":" + result[3] + ":" + \
                                    entry_time_east.strftime("%Y/%m/%d %H:%M") + ":" + result[1] + "\n"
                    if boss_rec.rstrip() in no_repeat or boss_rec in no_repeat:
                        continue # already warned
                    else:
                        with open(vaivora_constants.values.filenames.no_repeat, 'a') as f:
                            f.write(boss_rec)
                        message_to_send.append(boss_entry)
                        no_repeat.append(boss_rec)
            if len(message_to_send) == 0:
                inactive_time += (datetime.today()-loop_time)
                continue # empty record for this server
            else:
                inactive_time = timedelta(0)
                inactive      = False
            role_str = str()
            srv = client.get_server(vaivora_constants.regex.db.ext.sub('', vdb_id))
            for uid in vdst[vdb_id].get_role("boss"):
                try:    
                    # group mention
                    if discord.utils.get(srv.roles, mention=uid):
                        role_str    += uid + " "
                    else:
                        boss_user   = await client.get_user_info(uid)
                        role_str    += boss_user.mention + " "
                except:
                    # user mention
                    boss_user   = await client.get_user_info(uid)
                    role_str    += boss_user.mention + " "
            role_str = role_str if role_str else ""
            time_str = "15"
            # for role in srv.roles:
            #     if role.mentionable and role.name == "Boss Hunter":
            #         role_str = role.mention
            #         break
            cur_channel = ''
            for message in message_to_send:
                if cur_channel != message[-1] and not vaivora_constants.regex.format.matching.letters.match(message[-1]):
                    if cur_channel:
                        discord_message += "```"
                        await client.send_message(srv.get_channel(cur_channel), discord_message)
                        discord_message = ''
                    cur_channel = message[-1]
                    #TODO: Replace 15 with custom server time threshold
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