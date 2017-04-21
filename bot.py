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
client    = discord.Client()
vdbs      = dict()

# snippet from discord.py docs
logger = logging.getLogger(vaivora_constants.values.filenames.logger)
logger.setLevel(logging.WARNING)
handler = logging.FileHandler(vaivora_constants.values.filenames.log_file, encoding="utf-8")
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# @func:    on_ready()
# @return:
#   None
@client.event
async def on_ready():
    print("Logging in...")
    print('Successsfully logged in as: ' + client.user.name + '#' + \
          client.user.id + '. Ready!')

    valid_dbs = []

    # check each authorized server if welcomed or not -- possibly obsolete
    # with open(vaivora_constants.values.filenames.welcomed, 'w+') as welcomed:
    #     for line in welcomed:
    #         for server in client.servers:
    #             if not str(server.id) in line:
    #                 # authorized but not welcomed? welcome!
    #                 await on_server_join(server)
    # with open(vaivora_constants.values.filenames.welcomed, 'w+') as original:
    #     with open(vaivora_constants.values.filenames.welcomed_t, 'w+') as temporary:
    #         for line in original:
    #             srv_ver = line.split(':')[1]
    #             srv_chk = vaivora_modules.version.check_revisions(srv_ver)
    #             if srv_chk:
    #                 await client.send_message(server.owner, vaivora_modules.version.get_changelogs(srv_chk))
    #                 temporary.write(line.split(':')[0] + ":" + vaivora_version + "\n") # updated
    #             else:
    #                 temporary.write(line)
    #         # write back over
    #         for line in temporary:
    #             original.write(line)
    # open(vaivora_constants.values.filenames.welcomed_t, 'w').close()  

    for server in client.servers:
        vdbs[str(server.id)] = vaivora_modules.db.Database(str(server.id))
    await send_news()
    return

@client.event
async def send_news():
    vaivora_version   = vaivora_modules.version.get_current_version()
    if os.stat(vaivora_constants.values.filenames.welcomed).st_size == 0:
        await write_anew(client.servers)
        return True
    #try:
    with open(vaivora_constants.values.filenames.welcomed, 'r') as original:
        with open(vaivora_constants.values.filenames.welcomed_t, 'w+') as temporary:
            for line in original:
                if not line or line.isspace():
                    continue
                srv_tup = line.split(':')
                srv_ver = srv_tup[1].rstrip('\n')
                srv_sid = srv_tup[0]
                srv_chk = vaivora_modules.version.check_revisions(srv_ver)
                if srv_chk:
                    for vaivora_log in vaivora_modules.version.get_changelogs(srv_chk):
                        await client.send_message(client.get_server(srv_sid).owner, vaivora_log)
                    temporary.write(srv_sid + ":" + vaivora_version + "\n") # updated
                else:
                    temporary.write(line)
                # write back over
    with open(vaivora_constants.values.filenames.welcomed_t, 'r') as temporary:
        with open(vaivora_constants.values.filenames.welcomed, 'w+') as original:
            for line in temporary:
                original.write(line)
    #except:
        # file most likely does not exist or is empty. redo.
        #await write_anew(client.servers)
        #pass
    
    open(vaivora_constants.values.filenames.welcomed_t, 'w').close()
    return True


@client.event
async def write_anew(servers):
    vaivora_version   = vaivora_modules.version.get_current_version()
    with open(vaivora_constants.values.filenames.welcomed, 'a') as original:
        for server in servers:
            original.write(server.id + ':' + vaivora_version)
            await client.send_message(server.owner, vaivora_constants.values.words.message.welcome)
            for vaivora_log in vaivora_modules.version.get_changelogs():
                await client.send_message(server.owner, vaivora_log)


# @func:    on_server_available(discord.Server)
# @return:
#   True if ready, False otherwise
@client.event
async def on_server_join(server):
    print('called on_server_join')
    already           = False
    vaivora_version   = vaivora_modules.version.get_current_version()
    if server.unavailable:
        return False
    server_id         = str(server.id)
    if not re.match(r'[0-9]{18,}', server_id):
        return False # somehow invalid.

    with open(vaivora_constants.values.filenames.valid_db, 'a') as f:
        for line in f:
            if server_id in line:
                already   = True
                break

        if not already:
            vdbs[server_id]   = vaivora_modules.db.Database(server_id)
            f.write(server_id)
            await write_anew([server,])
        else:
            await send_news()
    return True


# @func:    on_message(Discord.message) : bool
#     begin code for message processing
# @arg:
#     message: Discord.message; includes message among sender (Discord.user) and server (Discord.server)
# @return:
#     True if succeeded, False otherwise
@client.event
async def on_message(message):
    
    # 'name' channel processing
    if not message.channel or not message.channel.name:
        if vaivora_constants.regex.boss.command.prefix.match(message.content):
            if vaivora_constants.regex.boss.command.arg_help.search(message.content):
                return await boss_cmd(message, pm=True)
        return True

    if "$debug" in message.content:

        return await client.send_message(message.author, "server: " + message.server.name + ", id: " + message.server.id + "\n")

    ####TODO: replace with custom setting
    if "timer" in message.channel.name or "boss" in message.channel.name:

        return await boss_cmd(message)

    if vaivora_constants.fun.ohoho.search(message.content):

        await client.send_message(message.channel, "https://youtu.be/XzBCBIVC7Qg?t=12s")
        return True

    elif vaivora_constants.fun.meme.match(message.content):

        await client.send_message(message.channel, message.author.mention + " " + "http://i.imgur.com/xiuxzUW.png")
        return True


    #await client.process_commands(message)
    
# @func:    boss_cmd(discord.Message, bool) : bool
# @arg:
#       message:
#           the message to process
#       pm:
#           (default: False)
#           if the message was a direct message or not
# @return:
#       True if successful, False otherwise
@client.event
async def boss_cmd(message, pm=False):
    if not pm:
        command_server  = message.server.id # changed to id
    command_message = message.content
      
    if not vaivora_constants.regex.boss.command.prefix.match(command_message):
        return False
    else:
        # sanitize & standardize
        command_message = vaivora_constants.regex.format.matching.to_sanitize.sub('', command_message)
        command_message = command_message.lower()             
        # strip leading command/arg
        command_message = vaivora_constants.regex.boss.command.prefix.sub('', command_message)
        message_args    = dict() # keys(): name, channel, map, time, 
        boss_channel    = 1
        maps_idx        = -1

        # command: list of arguments
        try:
            command = shlex.split(command_message)
        except ValueError:
            return await error(message.author, message.channel, \
                               vaivora_constants.command.syntax.cmd_error_bad_syntax_quote, \
                               vaivora_constants.command.syntax.cmd_boss)

        if command[0] == "help" and not pm:
            await client.send_message(message.channel, message.author.mention + " " + \
                                      vaivora_constants.command.boss.command)
            return True
        elif command[0] == "help" and pm:
            await client.send_message(message.author, \
                                      vaivora_constants.command.boss.command)
            return True
        elif pm:
            return False
        
        # begin checking validity
        #     arg validity
        #         count
        #             [3,4] - killed/anchored
        #             [2,3] - erase
        if len(command) < 2:

            return await error(message.author, message.channel, \
                               vaivora_constants.command.syntax.cmd_error_bad_syntax, \
                               vaivora_constants.command.syntax.cmd_boss, command_message)

        if (vaivora_constants.regex.boss.status.all_status.match(command[1]) and \
            (len(command) < vaivora_constants.command.boss.arg_min or \
             len(command) > vaivora_constants.command.boss.arg_max)) or \
           (vaivora_constants.regex.boss.command.arg_erase.match(command[1]) and \
            (len(command) < vaivora_constants.command.boss.arg_del_min or \
             len(command) > vaivora_constants.command.boss.arg_del_max)):

            return await error(message.author, message.channel, \
                               vaivora_constants.command.syntax.cmd_error_bad_syntax_arg_ct, \
                               vaivora_constants.command.syntax.cmd_boss, len(command))

        #         status
        if (not vaivora_constants.regex.format.matching.letters.match(command[0]) or \
            not (vaivora_constants.regex.boss.status.all_status.match(command[1]) or \
                 vaivora_constants.regex.boss.command.arg_erase.match(command[1]) or \
                 vaivora_constants.regex.boss.command.arg_list.match(command[1]) or \
                 vaivora_constants.regex.boss.command.arg_info.match(command[1]) or \
                 vaivora_constants.regex.boss.command.arg_boss.match(command[1]))) or \
          (vaivora_constants.regex.boss.status.all_status.match(command[1]) and \
           not vaivora_constants.regex.format.time.full.match(command[2])):
            
            return await error(message.author, message.channel, \
                               vaivora_constants.command.syntax.cmd_error_bad_syntax, \
                               vaivora_constants.command.syntax.cmd_boss)


        #         boss
        if vaivora_constants.regex.boss.command.arg_all.match(command[0]):

            lookup_boss = vaivora_constants.command.boss.bosses
            if vaivora_constants.regex.boss.command.arg_boss_w.match(command[1]):

                await client.send_message(message.channel, message.author.mention + " " + \
                                          vaivora_modules.boss.get_bosses_world())
                return True

            elif vaivora_constants.regex.boss.command.arg_boss_f.match(command[1]):

                await client.send_message(message.channel, message.author.mention + " " + \
                                          vaivora_modules.boss.get_bosses_field())
                return True

        else:

            boss_idx = await check_boss(command[0])
            if boss_idx < 0  or boss_idx >= len(vaivora_constants.command.boss.bosses):

                return await error(message.author, message.channel, \
                                   vaivora_constants.command.syntax.cmd_error_bad_boss_name, \
                                   vaivora_constants.command.syntax.cmd_boss, command[0])

            lookup_boss = [vaivora_constants.command.boss.bosses[boss_idx],]


        arg_map_idx     = 3 if vaivora_constants.regex.boss.status.all_status.match(command[1]) else 2
        

        if len(lookup_boss) == 1 and vaivora_constants.regex.boss.command.arg_info.match(command[1]):

            if vaivora_constants.regex.boss.command.arg_syns.match(command[1]):

                await client.send_message(message.channel, message.author.mention + " " + \
                                          vaivora_modules.boss.get_syns(lookup_boss[0]))
            
            else:

                await client.send_message(message.channel, message.author.mention + " " + \
                                          vaivora_modules.boss.get_maps(lookup_boss[0]))

            return True


        # boss list
        if vaivora_constants.regex.boss.command.arg_list.match(command[1]):

            valid_boss_records = list()
            boss_records = vdbs[command_server].check_db_boss(lookup_boss) # possible return
            if not boss_records: # empty

                await client.send_message(message.channel, message.author.mention + "  " + \
                                          "No results found! Try a different boss.\n")
                return True

            for boss_record in boss_records:

                record_date = [int(rec) for rec in boss_record[5:10]]
                record_date = datetime(*record_date) + \
                              vaivora_constants.values.time.offset.pacific2server
                tense = " and "
                tense_time = " minutes "
                time_diff = datetime.now() + vaivora_constants.values.time.offset.pacific2server - record_date
                if int(time_diff.days) >= 0:
                    tense += "should have respawned at "
                    tense_time += "ago"
                    tense_mins = int(time_diff.seconds / 60)
                else:
                    tense += "will respawn around "
                    tense_time += "from now"
                    tense_mins = int((vaivora_constants.values.time.seconds.in_day - time_diff.seconds) / 60)

                if tense_mins > 99:
                    tense_mins = str(int(tense_mins / 60)) + " hours, " + str(tense_mins % 60)
                elif tense_mins < 0:
                    tense_mins = str(int(24 + tense_mins / 60)) + " hours, " + str(tense_mins % 60)
                else:
                    tense_mins = str(tense_mins)

                valid_boss_records.append("\"" + boss_record[0] + "\" " + boss_record[3] + \
                                          " in ch." + str(int(boss_record[1])) + tense + \
                                          record_date.strftime("%Y/%m/%d \"%H:%M\"") + \
                                          " (" + str(tense_mins) + tense_time + ")" + \
                                          ".\nLast known map: #   " + boss_record[2])

            await client.send_message(message.channel, message.author.mention + " Records: ```python\n" + \
                                      '\n\n'.join(valid_boss_records) + "\n```")
            return True


        if len(lookup_boss) == 1 and lookup_boss[0] in vaivora_constants.command.boss.bosses_field:

            boss_channel    = 1
            xmsg            = lookup_boss[0] if lookup_boss[0] == "Blasphemous Deathweaver" else ""

            try:

                maps_idx = await check_maps(command[arg_map_idx], lookup_boss[0])
                if maps_idx < 0 or maps_idx >= len(vaivora_constants.command.boss.boss_locs[lookup_boss[0]]):

                    raise

            except:

                return await error(message.author, message.channel, \
                                   vaivora_constants.command.syntax.cmd_error_bad_boss_map, \
                                   vaivora_constants.command.syntax.cmd_boss, xmsg=xmsg)

        elif len(lookup_boss) == 1 and lookup_boss[0] in vaivora_constants.command.boss.bosses_world:

            boss_channel    = 0 if len(command) == arg_map_idx else vaivora_modules.boss.validate_channel(command[arg_map_idx])
            maps_idx        = 0

        else:

            boss_channel    = 0
            maps_idx        = 0

        
        # boss erase
        if vaivora_constants.regex.boss.command.arg_erase.match(command[1]):
            
            vdbs[command_server].rm_entry_db_boss(lookup_boss, boss_channel)
            await client.send_message(message.channel, message.author.mention + " Record successfully erased.\n")
            return True


        # (implicit) boss status
        if len(lookup_boss) > 1:

            return await error(message.author, message.channel, \
                               vaivora_constants.command.syntax.cmd_error_bad_boss_name, \
                               vaivora_constants.command.syntax.cmd_boss, command[0])

        message_args['name']    = lookup_boss[0]
        message_args['channel'] = boss_channel

        if maps_idx >= 0:

            message_args['map'] = vaivora_constants.command.boss.boss_locs[message_args['name']][maps_idx]

        else:

            message_args['map'] = 'N/A'

        # process time
        #     antemeridian
        if   vaivora_constants.regex.format.time.am.search(command[arg_map_idx - 1]):

            boss_time   = vaivora_constants.regex.format.time.delim.split(vaivora_constants.regex.format.time.am.sub('', command[arg_map_idx - 1]))
            boss_hour   = int(boss_time[0]) % 12

        #     postmeridian
        elif vaivora_constants.regex.format.time.pm.search(command[arg_map_idx - 1]):

            boss_time   = vaivora_constants.regex.format.time.delim.split(vaivora_constants.regex.format.time.pm.sub('', command[arg_map_idx - 1]))
            boss_hour   = (int(boss_time[0]) % 12) + 12

        #     24h time
        else:

            boss_time   = command[arg_map_idx - 1].split(':')
            boss_hour   = int(boss_time[0])


        if boss_hour > 24:

            return await error(message.author, message.channel, \
                               vaivora_constants.command.syntax.cmd_error_bad_boss_time, \
                               vaivora_constants.command.syntax.cmd_boss, msg=command[arg_map_idx - 1])

        boss_minutes = int(boss_time[1])
        original_boss_hour  = boss_hour
        approx_server_time = datetime.now() + vaivora_constants.values.time.offset.pacific2server
        boss_day    = approx_server_time.day if boss_hour <= int(approx_server_time.hour) \
                                             else (approx_server_time.day-1)
        boss_month  = approx_server_time.month
        boss_year   = approx_server_time.year

        # late recorded time; correct with -1 day
        mdate = datetime(boss_year, boss_month, boss_day, hour=boss_hour, minute=boss_minutes)
        time_diff = approx_server_time-mdate
        if time_diff.seconds < 0:  #or time_diff.seconds > 64800:
            with open(vaivora_constants.values.filenames.debug_file,'a') as f:
                f.write("server", message.server, "; time_diff", time_diff, "; mdate", mdate)
            return await error(message.author, message.channel, \
                               vaivora_constants.command.syntax.cmd_error_bad_boss_time, \
                               vaivora_constants.command.syntax.cmd_boss, msg=command[arg_map_idx - 1])

        wait_time = vaivora_constants.values.time.offset.boss_spawn_04h + \
                    vaivora_constants.values.time.offset.server2pacific
        boss_hour = boss_hour + (int(wait_time.seconds) / 3600) # boss_hour in Pacific/local

        if message_args['name'] in vaivora_constants.command.boss.bosses_events and \
          vaivora_constants.regex.boss.status.anchored.match(command[1]):

            return await error(message.author, message.channel, \
                               vaivora_constants.command.syntax.cmd_error_bad_boss_status, \
                               vaivora_constants.command.syntax.cmd_boss, msg=command[1])


        elif message_args['name'] in vaivora_constants.command.boss.boss_spawn_02h or \
             vaivora_constants.regex.boss.status.warning.match(command[1]):

            if boss_hour < 2:

                boss_hour += 22
                boss_day -= 1

            else:

                boss_hour -= 2

        elif message_args['name'] in vaivora_constants.command.boss.boss_spawn_16h:

            boss_hour += 12 # 12 + 4 = 16
            
        if int(boss_hour / 24):

            boss_hour = boss_hour % 24
            tomorrow = (datetime(boss_year, boss_month, boss_day)+timedelta(days=1))
            boss_day = tomorrow.day
            boss_month = tomorrow.month
            boss_year = tomorrow.year

        # add them to dict
        message_args['hour']      = boss_hour
        message_args['mins']      = boss_minutes
        message_args['day']       = boss_day
        message_args['month']     = boss_month
        message_args['year']      = boss_year
        message_args['status']    = command[1] # anchored or died
        message_args['srvchn']    = message.channel.id

        # May be obsoleted code -- database already sanitizes
        # status  = vdbs[command_server].validate_discord_db()

        # if not status: # db is not valid
        #     vdbs[command_server].create_db() # (re)create db
        #     return await error(message.author, message.channel, \
        #                        vaivora_constants.command.syntax.cmd_error\
        #                        [vaivora_constants.command.syntax.R]\
        #                        [vaivora_constants.command.syntax.BAD]\
        #                        [vaivora_constants.command.syntax.SYN][3], \
        #                        vaivora_constants.command.syntax.cmd_boss)
            
        status = vdbs[command_server].update_db_boss(message_args)

        if not status: # update_db_boss failed
            return await error(message.author, message.channel, \
                               vaivora_constants.command.syntax.cmd_error_bad_boss_time_wrap, \
                               vaivora_constants.command.syntax.cmd_boss, \
                               msg=(datetime(boss_year, boss_month, boss_day, original_boss_hour, boss_minutes).strftime("%Y/%m/%d %H:%M")))

        await client.send_message(message.channel, message.author.mention + " " + \
                                  vaivora_constants.command.boss.acknowledge + \
                                  message_args['name'] + " " + message_args['status'] + " at " + \
                                  ("0" if original_boss_hour < 10 else "") + \
                                  str(original_boss_hour) + ":" + \
                                  ("0" if message_args['mins'] < 10 else "") + \
                                  str(message_args['mins']) + ", in ch." + str(message_args['channel']) + ": " + \
                                  (message_args['map'] if message_args['map'] != "N/A" else ""))

        #await client.process_commands(message)
        return True # command processed
####
#
    


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
        await asyncio.sleep(60)
        with open(vaivora_constants.values.filenames.no_repeat, 'r') as f:
            for line in f:
                no_repeat.append(line.strip())
        print(today.strftime("%Y/%m/%d %H:%M"), "- Valid DBs: ", len(vdbs))
        for vdb_id, valid_db in vdbs.items():
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
                # erase contents after transferring
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

            ####TODO: replace "@here" with custom setting of role
            role_str = "@here"
            time_str = "15"
            srv = client.get_server(vaivora_constants.regex.db.ext.sub('', vdb_id))
            for role in srv.roles:
                if role.mentionable and role.name == "Boss Hunter":
                    role_str= role.mention
                    break

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
        ret_msg.append("For syntax: $boss help")
        await client.send_message(channel, '\n'.join(ret_msg))
        return error_code
        # end of common return for $boss

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