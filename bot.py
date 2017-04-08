#!/usr/bin/env python
import discord
import logging
import sqlite3
import shlex
import asyncio
import re
import os
from datetime import datetime, timedelta
from operator import itemgetter

# import additional constants
from importlib import import_module as im
import vaivora_constants
for mod in vaivora_constants.modules:
    im(mod)
#import vaivora_modules.db
import vaivora_modules.version

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

    welcomed  = open(vaivora_constants.values.filenames.welcomed, 'w+')

    # check each authorized server if welcomed or not
    for server in client.servers:
        if not str(server.id) in welcomed:
            # authorized but not welcomed? welcome!
            await on_server_join(server)

    for valid_db in open(vaivora_constants.values.filenames.valid_db, 'r'):
        vdb   = valid_db.rstrip('\n')
        # database automatically validated, created, sanitized with instantiation
        vdbs[vdb]   = vaivora_modules.db.Database(vdb)
    return

# @func:    on_server_available(discord.Server)
# @return:
#   True if ready, False otherwise
@client.event
async def on_server_join(server):
    vaivora_version   = vaivora_modules.version.get_current_version()
    if server.unavailable:
        return False
    server_name  = str(server.id)
    if not re.match(r'[0-9]{18,}', server_name):
        return False # somehow invalid.

    with open(vaivora_constants.values.filenames.valid_db, 'a') as f:
        if not server_name in f:
            vdbs[server_name]     = vaivora_modules.db.Database(server_name)
            f.write(server_name + "\n")

    with open(vaivora_constants.values.filenames.welcomed, 'r') as original:
        with open(vaivora_constants.values.filenames.welcomed_t, 'w+') as temporary:
            if not server_name in original: # welcome, now!
                await client.send_message(server.owner, vaivora_constants.values.words.message.welcome)
                await client.send_message(server.owner, vaivora_modules.version.get_changelogs())
                for line in original:
                    temporary.write(line)
                temporary.write(server_name + ":" + vaivora_version)
            else: # let's see what you're missing
                for line in original:
                    if server_name in line:
                        srv_ver = line.split(':')[1]
                        srv_chk = vaivora_modules.version.check_revisions(srv_ver)
                        if srv_chk:
                            await client.send_message(server.owner, vaivora_modules.version.get_changelogs(srv_chk))
                            temporary.write(line.split(':')[0] + ":" + vaivora_version) # updated
                            continue
                    temporary.write(line) # no changes

    # write back over
    with open(vaivora_constants.values.filenames.welcomed_t, 'r') as temporary:
        with open(vaivora_constants.values.filenames.welcomed, 'w+') as original:
            for line in temporary:
                original.write(line)

    return True


# begin code for message processing
# @func:    on_message(Discord.message)
# @arg:
#     message: Discord.message; includes message among sender (Discord.user) and server (Discord.server)
# @return:
#     None
@client.event
async def on_message(message):
    # 'name' channel processing
    if not message.channel or not message.channel.name:
        # ignore direct messages for now
        return

    if "timer" in message.channel.name or "boss" in message.channel.name:
        command_server  = message.server.id # changed to id
        command_message = message.content
    
        # TODO: Replace hard-coded words with custom setting if set
        if vaivora_constants.regex.boss.command.prefix.match(command_message):
            # sanitize & standardize
            command_message = vaivora_constants.regex.format.matching.to_sanitize.sub('', command_message)
            command_message = command_message.lower()             
            # strip leading command/arg
            command_message = vaivora_constants.regex.boss.command.prefix.sub('', command_message)
            message_args    = dict() # keys(): name, channel, map, time, 
            boss_channel    = 1
            maps_idx        = -1

            # if odd amount of quotes, drop
            if len(vaivora_constants.regex.format.matching.quotes.findall(command_message)) % 2:
                err_code = await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R]\
                                       [vaivora_constants.command.syntax.BAD]\
                                       [vaivora_constants.command.syntax.SYN][4], vaivora_constants.command.syntax.cmd_boss)
                return err_code

            # command: list of arguments
            command = shlex.split(command_message)
            if command[0] == "help":
                await client.send_message(message.channel, message.author.mention + " " + \
                                          vaivora_constants.command.boss.command)
                return True

            # if command[0] == "synonyms"

            if len(command) < 2:
                err_code = await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R]\
                                       [vaivora_constants.command.syntax.BAD]\
                                       [vaivora_constants.command.syntax.SYN][1], \
                                       vaivora_constants.command.syntax.cmd_boss, command_message)
                return err_code

            # begin checking validity
            #     arg validity
            #         count: [3,5] - killed/anchored
            #                [2,3] - erase
            if (vaivora_constants.regex.boss.status.all_status.match(command[1]) and \
               (len(command) < vaivora_constants.command.boss.arg_min or len(command) > vaivora_constants.command.boss.arg_max)):
                err_code = await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R]\
                                       [vaivora_constants.command.syntax.BAD]\
                                       [vaivora_constants.command.syntax.SYN][2], \
                                       vaivora_constants.command.syntax.cmd_boss, len(command))
                return err_code

            if (vaivora_constants.regex.boss.command.arg_erase.match(command[1]) and (len(command) < 2 or len(command) > 3)): #### TODO: change constants
                err_code = await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R]\
                                       [vaivora_constants.command.syntax.BAD]\
                                       [vaivora_constants.command.syntax.SYN][2], \
                                       vaivora_constants.command.syntax.cmd_boss, len(command))
                return err_code

            #         boss: letters
            #         status: anchored, died
            #         time: format
            if not vaivora_constants.regex.format.matching.letters.match(command[0]):
                err_code = await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R]\
                                       [vaivora_constants.command.syntax.BAD]\
                                       [vaivora_constants.command.syntax.SYN][1], \
                                       vaivora_constants.command.syntax.cmd_boss)
                return err_code
            if not (vaivora_constants.regex.boss.status.all_status.match(command[1]) or \
               vaivora_constants.regex.boss.command.arg_erase.match(command[1]) or \
               vaivora_constants.regex.boss.command.arg_list.match(command[1])): 
                err_code = await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R]\
                                       [vaivora_constants.command.syntax.BAD]\
                                       [vaivora_constants.command.syntax.SYN][1], \
                                       vaivora_constants.command.syntax.cmd_boss)
                return err_code
            if vaivora_constants.regex.boss.status.all_status.match(command[1]) and not vaivora_constants.regex.format.time.full.match(command[2]):
                err_code = await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R]\
                                       [vaivora_constants.command.syntax.BAD]\
                                       [vaivora_constants.command.syntax.SYN][1], \
                                       vaivora_constants.command.syntax.cmd_boss)
                return err_code

            #     boss validity
            #         all list
            bossrec_str = list()
            if vaivora_constants.regex.boss.command.arg_all.match(command[0]) and \
               vaivora_constants.regex.boss.command.arg_list.match(command[1]):
                bossrec = await func_discord_db(command_server, check_boss_db, bosses) # possible return
                if not bossrec: # empty
                    await client.send_message(message.channel, message.author.mention + " No results found! Try a different boss.")
                    return True
                for brec in bossrec:
                    recdate = datetime(int(brec[5]), \
                                       int(brec[6]), \
                                       int(brec[7]), \
                                       int(brec[8]), \
                                       int(brec[9])) \
                              + vaivora_constants.values.time.offset.pacific2server
                    tense = " and "
                    tense_time = " minutes "
                    difftime = datetime.now()+vaivora_constants.values.time.offset.pacific2server-recdate
                    days = int(difftime.days)
                    if days >= 0:
                        tense += "should have respawned at "
                        tense_time += "ago"
                        tense_mins = int(difftime.seconds / 60) + int(difftime.days*vaivora_constants.values.time.seconds.in_day/60)
                    else:
                        tense += "will respawn around "
                        tense_time += "from now"
                        tense_mins = int((vaivora_constants.values.time.seconds.in_day - difftime.seconds) / 60)

                    if tense_mins > 0:
                        tense_mins = str(int(tense_mins/60)) + " hours, " + str(tense_mins % 60)
                    elif tense_mins < 0:
                        tense_mins = str(int(24 + tense_mins/60)) + " hours, " + str(tense_mins % 60)
                    else:
                        tense_mins = str(tense_mins)

                    if days > 1:
                        tense_mins = str(abs(days)) + " days, " + tense_mins
                    elif days > 0:
                        tense_mins = str(abs(days)) + " day, " + tense_mins


                    bossrec_str.append("\"" + brec[0] + "\" " + brec[3] + " in ch." + str(int(brec[1])) + tense + \
                                       recdate.strftime("%Y/%m/%d %H:%M") + \
                                       " (" + tense_mins + tense_time + ")" + \
                                       ". Last known map: # " + brec[2])
                await client.send_message(message.channel, message.author.mention + " Records: ```python\n" + \
                                          '\n\n'.join(bossrec_str) + "\n```")
                return True

            elif vaivora_constants.regex.boss.command.arg_all.match(command[0]) and \
              vaivora_constants.regex.boss.command.arg_erase.match(command[1]):
                for boss in bosses:
                    await func_discord_db(command_server, rm_ent_boss_db, xargs=boss)
                await client.send_message(message.channel, message.author.mention + " Records successfully erased.\n")
                return True

            elif vaivora_constants.regex.boss.command.arg_all.match(command[0]):
                err_code = await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R]\
                                       [vaivora_constants.command.syntax.BAD]\
                                       [vaivora_constants.command.syntax.SYN][1], \
                                       vaivora_constants.command.syntax.cmd_boss)
                return err_code
            
            boss_idx = await check_boss(command[0])
            if boss_idx < 0  or boss_idx >= len(bosses):
                err_code = await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][vaivora_constants.command.syntax.BAD][vaivora_constants.command.syntax.BOSS][1], \
                                       vaivora_constants.command.syntax.cmd_boss, command[0])
                return err_code

            #         boss erase
            if vaivora_constants.regex.boss.command.arg_erase.match(command[1]) and len(command) < 3:
                await func_discord_db(command_server, rm_ent_boss_db, bosses[boss_idx])
                await client.send_message(message.channel, message.author.mention + " Record successfully erased.\n")
                return True
            elif vaivora_constants.regex.boss.command.arg_erase.match(command[1]):
                await func_discord_db(command_server, rm_ent_boss_db, (bosses[boss_idx], command[2],))
                await client.send_message(message.channel, message.author.mention + " Record successfully erased.\n")
                return True

            #         boss list
            bossrec_str = list()
            if vaivora_constants.regex.boss.command.arg_list.match(command[1]):
                bossrec = await func_discord_db(command_server, check_boss_db, (bosses[boss_idx],)) # possible return
                if not bossrec: # empty
                    await client.send_message(message.channel, message.author.mention + " No results found! Try a different boss.\n")
                    return True
                for brec in bossrec:
                    # following block should be made into function
                    recdate = datetime(int(brec[5]), \
                                       int(brec[6]), \
                                       int(brec[7]), \
                                       int(brec[8]), \
                                       int(brec[9])) \
                              + vaivora_constants.values.time.offset.pacific2server
                    tense = " and "
                    tense_time = " minutes "
                    difftime = datetime.now()+vaivora_constants.values.time.offset.pacific2server-recdate
                    if int(difftime.days) >= 0:
                        tense += "should have respawned at "
                        tense_time += "ago"
                        tense_mins = int(difftime.seconds / 60)
                    else:
                        tense += "will respawn around "
                        tense_time += "from now"
                        tense_mins = int((vaivora_constants.values.time.seconds.in_day - difftime.seconds) / 60)

                    if tense_mins > 99:
                        tense_mins = str(int(tense_mins/60)) + " hours, " + str(tense_mins % 60)
                    elif tense_mins < 0:
                        tense_mins = str(int(24 + tense_mins/60)) + " hours, " + str(tense_mins % 60)
                    else:
                        tense_mins = str(tense_mins)

                    bossrec_str.append("\"" + brec[0] + "\" " + brec[3] + " in ch." + str(int(brec[1])) + tense + \
                                       recdate.strftime("%Y/%m/%d \"%H:%M\"") + \
                                       " (" + str(tense_mins) + tense_time + ")" + \
                                       ". Last known map: # " + brec[2])
                await client.send_message(message.channel, message.author.mention + " Records: ```python\n" + \
                                          '\n\n'.join(bossrec_str) + "\n```")
                return True


            #     (opt) channel: reject if field boss & ch > 1 or if ch > 4
            #     (opt) map: validity
            ##### TODO: Make channel limit specific per boss
            if len(command) > 3:
                #     channel is set
                #     keep track of arg position in case we have 5
                argpos = 3
                if vaivora_constants.regex.boss.location.channel.match(command[argpos]):
                    boss_channel = int(vaivora_constants.regex.format.matching.letters.sub('', command[argpos]))
                    argpos += 1

                #     specifically not an elif - sequential handling of args
                #     cases:
                #         4 args: 4th arg is channel
                #         4 args: 4th arg is map
                #         5 args: 4th and 5th arg are channel and map respectively
                try:
                    if not vaivora_constants.regex.boss.location.channel.match(command[argpos]) or len(command) == 5 or bosses[boss_idx] in bossfl:
                        maps_idx = await check_maps(command[argpos], bosses[boss_idx])
                        if maps_idx < 0 or maps_idx >= len(bosslo[boss]):
                            err_code = await error(message.author, message.channel, \
                                                   vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R]\
                                                   [vaivora_constants.command.syntax.BAD][vaivora_constants.command.syntax.BOSS][2], \
                                                   vaivora_constants.command.syntax.cmd_boss, command[1])
                            return err_code
                except:
                    pass

            #         check if boss is a field boss, and discard if boss channel is not 1
            if bosses[boss_idx] in bossfl and boss_channel != 1:
                err_code = await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R]\
                                       [vaivora_constants.command.syntax.BAD][vaivora_constants.command.syntax.BOSS][4], \
                                       vaivora_constants.command.syntax.cmd_boss, boss_channel, bosses[boss_idx])
                return err_code

            # everything looks good if the string passes through
            # begin compiling record in dict form 'message_args'
            message_args['name'] = bosses[boss_idx]
            message_args['channel'] = boss_channel
            if maps_idx >= 0:
                message_args['map'] = bosslo[message_args['name']][maps_idx]
            elif not message_args['name'] in bossfl:
                message_args['map'] = bosslo[message_args['name']][0]
            else:
                message_args['map'] = 'N/A'

            # process time
            #     antemeridian
            if vaivora_constants.regex.format.time.am.search(command[2]):
                btime = vaivora_constants.regex.format.time.delim.split(vaivora_constants.regex.format.time.am.sub('', command[2]))
                bhour = int(btime[0]) % 12
            #     postmeridian
            elif vaivora_constants.regex.format.time.pm.search(command[2]):
                btime = vaivora_constants.regex.format.time.delim.split(vaivora_constants.regex.format.time.pm.sub('', command[2]))
                bhour = (int(btime[0]) % 12) + 12
            #     24h time
            else:
                btime = command[2].split(':')
                bhour = int(btime[0])
            #     handle bad input

            if bhour > 24:
                err_code = await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R]\
                                       [vaivora_constants.command.syntax.BAD]\
                                       [vaivora_constants.command.syntax.BOSS][3], \
                                       vaivora_constants.command.syntax.cmd_boss, msg=command[2])
                return err_code
            bminu = int(btime[1])
            oribhour  = bhour
            approx_server_time = datetime.now() + vaivora_constants.values.time.offset.pacific2server
            btday = approx_server_time.day if bhour <= int((datetime.now() + vaivora_constants.values.time.offset.pacific2server).hour) \
                                           else (approx_server_time.day-1)
            btmon = approx_server_time.month
            byear = approx_server_time.year

            # late recorded time; correct with -1 day
            mdate = datetime(byear, btmon, btday, hour=bhour, minute=bminu)
            tdiff = approx_server_time-mdate
            if tdiff.seconds < 0:  #or tdiff.seconds > 64800:
                with open(vaivora_constants.values.filenames.debug_file,'a') as f:
                    f.write("server", message.server, "; tdiff", tdiff, "; mdate",mdate)
                return await error(message.author, message.channel, vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][vaivora_constants.command.syntax.BAD][vaivora_constants.command.syntax.BOSS][3], vaivora_constants.command.syntax.cmd_boss, msg=command[2])

            #wait_time = vaivora_constants.values.time.offset.anchor_spawn if vaivora_constants.regex.boss.status.anchored.match(command[1]) else vaivora_constants.values.time.offset.boss_spawn_04h
            wait_time = vaivora_constants.values.time.offset.boss_spawn_04h + \
                        vaivora_constants.values.time.offset.server2pacific
            print(wait_time)
            bhour = bhour + (int(wait_time.seconds) / 3600) # bhour in Pacific/local
            print(wait_time.seconds)
            if message_args['name'] in boseve and vaivora_constants.regex.boss.status.anchored.match(command[1]):
                return await error(message.author, message.channel, \
                                   vaivora_constants.command.syntax.cmd_error\
                                   [vaivora_constants.command.syntax.R]\
                                   [vaivora_constants.command.syntax.BAD]\
                                   [vaivora_constants.command.syntax.BOSS][5], \
                                   vaivora_constants.command.syntax.cmd_boss, msg=command[1])
            elif message_args['name'] in bos02s or vaivora_constants.regex.boss.status.warning.match(command[1]):
                if bhour < 2:
                    bhour += 22
                    btday -= 1
                else:
                    bhour -= 2
            elif message_args['name'] in bos16s:
                bhour += 12 # 12 + 4 = 16
                
            print(bhour)
            if int(bhour / 24):
                bhour = bhour % 24
                tomorrow = (datetime(byear, btmon, btday)+timedelta(days=1))
                btday = tomorrow.day
                btmon = tomorrow.month
                byear = tomorrow.year

            # add them to dict
            message_args['hour']      = bhour
            message_args['mins']      = bminu
            message_args['day']       = btday
            message_args['month']     = btmon
            message_args['year']      = byear
            message_args['status']    = command[1] # anchored or died
            message_args['srvchn']    = message.channel.id

            status  = await func_discord_db(command_server, validate_discord_db)
            if not status: # db is not valid
                err_code = await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error\
                                       [vaivora_constants.command.syntax.R]\
                                       [vaivora_constants.command.syntax.BAD]\
                                       [vaivora_constants.command.syntax.SYN][3], \
                                       vaivora_constants.command.syntax.cmd_boss)
                await func_discord_db(command_server, create_discord_db) # (re)create db
                return err_code

            status = await func_discord_db(command_server, update_boss_db, message_args)
            if not status: # update_boss_db failed
                err_code = await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error\
                                       [vaivora_constants.command.syntax.R][0], \
                                       vaivora_constants.command.syntax.cmd_boss)
                return err_code

            await client.send_message(message.channel, message.author.mention + " " + \
                                      vaivora_constants.command.boss.acknowledge + \
                                      message_args['name'] + " " + message_args['status'] + " at " + \
                                      ("0" if oribhour < 10 else "") + \
                                      str(oribhour) + ":" + \
                                      ("0" if message_args['mins'] < 10 else "") + \
                                      str(message_args['mins']) + ", CH" + str(message_args['channel']) + ": " + \
                                      (message_args['map'] if message_args['map'] != "N/A" else ""))

            #await client.process_commands(message)
            return True # command processed
    
    elif vaivora_constants.fun.ohoho.search(message.content):
        await client.send_message(message.channel, "https://youtu.be/XzBCBIVC7Qg?t=12s")
        return True
    elif vaivora_constants.fun.meme.match(message.content):
        await client.send_message(message.channel, message.author.mention + " " + "http://i.imgur.com/xiuxzUW.png")
        return True
    else:
        #await client.process_commands(message)
        return False

def get_file_length(f):
    with open(f) as a_file:
        n = -1
        for n, ln in enumerate(f):
            pass
        return n + 1

# @func:    check_databases()
async def check_databases():
    await client.wait_until_ready()
    results = dict()
    today = datetime.today() # check on first launch

    while not client.is_closed:
        await asyncio.sleep(60)
        valid_dbs = []
        no_repeat = []
        try:
            f = open(vaivora_constants.values.filenames.valid_db,'r')
        except:
            open(vaivora_constants.values.filenames.valid_db,'a').close()
            f = open(vaivora_constants.values.filenames.valid_db,'r')
        try:
            g = open(vaivora_constants.values.filenames.no_repeat,'r')
        except:
            open(vaivora_constants.values.filenames.no_repeat,'a').close()
            g = open(vaivora_constants.values.filenames.no_repeat,'r')
        for line_f in f:
            valid_dbs.append(line_f.strip())
        for line_g in g:
            no_repeat.append(line_g.strip())
        print("Valid DBs: ", len(valid_dbs))
        for valid_db in valid_dbs:
            # check all timers
            message_send = list()
            cur_channel = str()
            results[valid_db] = await func_discord_db(valid_db, check_boss_db, bosses)
            # sort by time
            if not results[valid_db]:
                continue
            results[valid_db].sort(key=itemgetter(5,6,7,8,9))
            for result in results[valid_db]:
                list_time = [int(t) for t in result[5:10]]
                try:
                    rtime = datetime(*list_time)
                except:
                    #TODO: remove entry
                    continue
                rtime_east = rtime + vaivora_constants.values.time.offset.pacific2server
                tdiff = rtime-datetime.now()
                # if tdiff < 0: # stale data; delete
                #     await func_discord_db(valid_db, rm_ent_boss_db, bd=result)
                # elif tdiff.seconds < 10800 and vaivora_constants.regex.boss.status.anchored.match(result[3]):
                #     message_send.append(format_message_boss(result[0], result[3], rtime_east, result[1]))
                #elif
                if tdiff.days < 0:
                    continue
                if tdiff.seconds < 900 and tdiff.days == 0:
                    msgb = []
                    msgb.append(format_message_boss(result[0], result[3], rtime_east, result[2], result[1]))
                    msgb.append(str(result[4]),)
                    strm = str(result[4]) + ":" + str(result[0]) + ":" + str(result[3]) + ":" + \
                           str(rtime_east) + ":" + str(result[1]) + "\n"
                    if strm.rstrip() in no_repeat or strm in no_repeat:
                        continue
                    else:
                        with open(vaivora_constants.values.filenames.no_repeat, 'a') as h:
                            h.write(strm)
                        message_send.append(msgb)
                # elif tdiff.seconds > 72000:
                #     await func_discord_db(valid_db, rm_ent_boss_db, result)
            # message: str, str
            if len(message_send) == 0:
                continue
            # right_now = datetime.now()
            # dated_fil = "-" + str(right_now.year) + str(right_now.month) + str(right_now.day) + \
            #             "." + str(right_now.hour) + str(right_now.minute)
            # # remove clutter while nothing is reported
            # os.rename(vaivora_constants.values.filenames.no_repeat, vaivora_constants.values.filenames.no_repeat + dated_fil)
            # with open('wings-norepeat-temp','a')
            # len(line_g)-len(message_send)
            # for i in range(len(line_g)):
            # implement later.

            r = "@here"
            srv = client.get_server(vaivora_constants.regex.db.ext.sub('', valid_db))
            for role in srv.roles:
                if role.mentionable and role.name == "Boss Hunter":
                    r = role.mention
                    break
            cur_channel = ''
            for message in message_send:
                if cur_channel != message[-1] and not vaivora_constants.regex.format.matching.letters.match(message[-1]):
                    if cur_channel:
                        messtr += "```"
                        await client.send_message(srv.get_channel(cur_channel), messtr)
                    cur_channel = message[-1]
                    #TODO: Replace 15 with custom server time threshold
                    messtr = r + " The following bosses will spawn within " + "15" + " minutes: ```python\n"
                messtr += message[0]
            # flush
            messtr += "```"
            await client.send_message(srv.get_channel(cur_channel), messtr)
        #await client.process_commands(message)
        f.close()
        g.close()
        await asyncio.sleep(1)

def format_message_boss(boss, status, time, bossmap, channel):
    if status == "warned":
        bossmap = [(bossmap,)]
    elif not boss in bossfl:
        bossmap = bosslo[boss]
    elif bossmap == 'N/A':
        bossmap = ['[Map Unknown]',]
    elif boss == "Blasphemous Deathweaver" and re.search("[Aa]shaq", bossmap):
        bossmap = [m for m in bosslo[boss][2:-1] if m != bossmap]
    elif boss == "Blasphemous Deathweaver":
        bossmap = [m for m in bosslo[boss][0:2] if m != bossmap]
    else:
        bossmap = [m for m in bosslo[boss] if m != bossmap]

    if vaivora_constants.regex.boss.status.anchored.search(status):
        report_time = time+timedelta(hours=-3)
        status_str = " was anchored"
    elif vaivora_constants.regex.boss.status.warning.search(status):
        report_time = time+timedelta(hours=-2)
        status_str = " was warned to spawn"
    else:
        if boss in bos02s:
            report_time = time+timedelta(hours=-2)
        elif boss in bos16s:
            report_time = time+timedelta(hours=-16)
            print(report_time)
        else:
            report_time = time+timedelta(hours=-4)
        status_str = " died"

    status_str  = status_str + " in ch." + str(int(channel)) + " at "
    # if boss not in bos16s and boss not in bos02s:
    #     time_exp    = vaivora_constants.values.time.offset.boss_spawn_04h
    # elif boss in bos16s:
    #     time_exp    = con['TIME.WAIT.16H']
    # elif boss in bos02s:
    #     time_exp    = con['TIME.WAIT.2H']
    expect_str  = (("between " + (time-timedelta(hours=1)).strftime("%Y/%m/%d %H:%M") + " and ") \
                   if vaivora_constants.regex.boss.status.anchored.match(status) else "at ") + \
                  (time).strftime("%Y/%m/%d %H:%M") + \
                  " (in " + str(int((time-datetime.now()+vaivora_constants.values.time.offset.server2pacific).seconds/60)) + " minutes)"

    if "[Map Unknown]" in bossmap:
        map_str     = '.'
    else:
        map_str     = ", in one of the the following maps:" + '\n#    ' + '\n#    '.join(bossmap[0:])
    message     = "\"" + boss + "\"" + status_str + report_time.strftime("%Y/%m/%d %H:%M") + ", and should spawn " + \
                  expect_str + map_str + "\n"
    return message

# @func:    check_boss(str): begin code for checking boss validity
# @arg:
#     boss: str; boss name from raw input
# @return:
#     boss index in list, or -1 if not found
async def check_boss(boss):
    for bossa in bosses:
        if boss in bossa.lower():
            return bosses.index(bossa)
    else:
        # for b in bosses:
        #     if b in boss:
        #         return bosses.index(b)
        for b, syns in bossyn.items():
            if boss in syns or b in boss:
                return bosses.index(b)
    return -1
# end of check_boss

# @func:    check_maps(str, str): begin code for checking map validity
# @arg:
#     maps: str; map name from raw input
#     boss: str; the corresponding boss
# @return:
#     map index in list, or -1 if not found
async def check_maps(maps, boss):
    if boss == "Blasphemous Deathweaver" and not vaivora_constants.regex.boss.location.loc[DW][A].search(maps):
        return -1

    elif vaivora_constants.regex.boss.location.floors_fmt.search(maps) or boss == "Blasphemous Deathweaver":
        # rearrange letters, and remove map name
        if boss == "Wrathful Harpeia":
            mapnum = vaivora_constants.regex.boss.location.floors_fmt.sub(r'\g<floornumber>', maps)
            maps = "Demon Prison District " + mapnum
        else:
            mapnum = vaivora_constants.regex.boss.location.floors_fmt.sub(r'\g<district>\g<basement>\g<floornumber>\g<floor>', maps)
            mapnum = str(mapnum).upper()

        
        if boss == "Blasphemous Deathweaver" and vaivora_constants.regex.boss.location.loc[DW][CM].search(maps):
            mapnum = vaivora_constants.regex.boss.location.loc[DW][CM].sub('', mapnum) # erase name and redo
            maps = "Crystal Mine " + mapnum
        elif boss == "Blasphemous Deathweaver":
            mapnum = vaivora_constants.regex.boss.location.loc[DW][AS].sub('', mapnum) # erase name and redo
            maps = "Ashaq Underground Prison " + mapnum
        # elif boss == "Wrathful Harpeia":
        #     if vaivora_constants.regex.boss.location.loc[HA][A].search(maps):
        #         mapnum = vaivora_constants.regex.boss.location.loc[HA][A].sub('', mapnum) # erase name and redo
        #     if vaivora_constants.regex.boss.location.floors_chk.search(maps):
        #         mapnum = vaivora_constants.regex.boss.location.floors_chk.sub('', mapnum) # erase d or f; doesn't matter!
        #     if vaivora_constants.regex.boss.location.loc[HA][DP].search(maps):
        #         mapnum = vaivora_constants.regex.boss.location.loc[HA][DN].sub('', mapnum) # erase district, keep number, and redo
        #     maps = "Demon Prison District " + mapnum
    # elif vaivora_constants.regex.format.matching.one_number.search(maps) and boss != "Bleak Chapparition":
    #     mapname = vaivora_constants.regex.format.matching.one_number.sub('', bosslo[boss][0])
    #     maps = mapname + maps

    mapidx = -1
    for m in bosslo[boss]:
        if m.lower() in maps.lower():
            if mapidx != -1:
                return -1
            mapidx = bosslo[boss].index(m)
        elif maps.lower() in m.lower():
            if mapidx != -1:
                return -1
            mapidx = bosslo[boss].index(m)
    return mapidx

# @func:  error(**): begin code for error message printing to user
# @arg:
#     user:     Discord.user
#     channel:  server channel
#     etype:    [e]rror type
#     ecmd:     [e]rror (invoked by) command
#     msg:      (optional) message for better error clarity
# @return:
#     -1:     BROAD:  the command was correctly formed but the argument is too broad
#     -2:     WRONG:  the command was correctly formed but could not validate arguments
#     -127:   SYNTAX: malformed command: quote mismatch, argument count
async def error(user, channel, etype, ecmd, msg='', xmsg=''):
    # get the user in mentionable string
    user_name = user.mention
    # convert args
    if msg:
        msg = str(msg)
    if xmsg:
        xmsg = str(xmsg)
    # prepare a list to send message
    ret_msg   = list()

    # boss command only
    if ecmd == vaivora_constants.command.syntax.cmd_boss:
        # broad
        if etype == vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][1]:
            ret_msg.append(user_name + the_following_argument('name') + msg + \
                           ") for `$boss` has multiple matching spawn points:\n")
            ret_msg.append(cmd_usage['code_block'])
            ret_msg.append('\n'.join(bosslo[msg]))
            ret_msg.append(cmd_usage['code_block'])
            ret_msg.append(vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.G][2])
            ret_msg.append(vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.B][2])
            ecode = vaivora_constants.values.error_codes.broad
        elif etype == vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][0]:
            ret_msg.append(user_name + " I'm sorry. Your command failed for unknown reasons.\n" + \
                           "This command failure has been recorded.\n" + \
                           "Please try again shortly.\n")
            with open('wings_of_vaivora-error.txt', 'a') as f:
                f.write(str(datetime.today()) + " An error was detected when " + user_name + " sent a command.")
            ecode = vaivora_constants.values.error_codes.wrong
        # unknown boss
        elif etype == vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][vaivora_constants.command.syntax.BAD][vaivora_constants.command.syntax.BOSS][1]:
            ret_msg.append(user_name + the_following_argument('name') + msg + \
                           ") is invalid for `$boss`. This is a list of bosses you may use:\n")
            ret_msg.append(cmd_usage['code_block'])
            ret_msg.append('\n'.join(bosses))
            ret_msg.append(cmd_usage['code_block'])
            ret_msg.append(vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.B][1])
            ecode = vaivora_constants.values.error_codes.wrong
        elif etype == vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][vaivora_constants.command.syntax.BAD][vaivora_constants.command.syntax.BOSS][5]:
            ret_msg.append(user_name + the_following_argument('status') + msg + \
                           ") is invalid for `$boss`. You may not select `anchored` for its status.\n")
            ecode = vaivora_constants.values.error_codes.wrong
        elif etype == vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][vaivora_constants.command.syntax.BAD][vaivora_constants.command.syntax.BOSS][2]:
            try_msg = list()
            try_msg.append(user_name + the_following_argument('map') + msg + \
                           ") (number) is invalid for `$boss`. This is a list of maps you may use:\n")
            try: # make sure the data is valid by `try`ing
              try_msg.append(cmd_usage['code_block'])
              try_msg.append('\n'.join(bosslo[xmsg]))
              try_msg.append(cmd_usage['code_block'])
              try_msg.append(vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.B][2])
              # seems to have succeeded, so extend to original
              ret_msg.extend(try_msg)
              ecode = vaivora_constants.values.error_codes.wrong
            except: # boss not found! 
              ret_msg.append(user_name + cmd_usage['debug'])
              ret_msg.append(vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.G][1])
              ecode = vaivora_constants.values.error_codes.syntax
              with open(vaivora_constants.values.filenames.debug_file, 'a') as f:
                  f.write('boss not found\n')
        elif etype == vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][vaivora_constants.command.syntax.BAD][vaivora_constants.command.syntax.BOSS][4]:
            ret_msg.append(user_name + the_following_argument('channel') + msg + \
                           ") (number) is invalid for `$boss`. " + xmsg + " is a field boss, thus " + \
                           "variants that spawn on channels other than 1 (or other maps) are considered world bosses " + \
                           "with unpredictable spawns.\n")
            ecode = vaivora_constants.values.error_codes.wrong
        elif etype == vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][vaivora_constants.command.syntax.BAD][vaivora_constants.command.syntax.BOSS][3]:
            ret_msg.append(user_name + the_following_argument('time') + msg + \
                           ") is invalid for `$boss`.\n")
            ret_msg.append("Omit spaces; record in 12H (with AM/PM) or 24H time.\n")
            ret_msg.append(vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.G][1])
            ecode = vaivora_constants.values.error_codes.wrong
        elif etype == vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][vaivora_constants.command.syntax.BAD][vaivora_constants.command.syntax.BOSS][5]:
            ret_msg.append(user_name + the_following_argument('status') + 'anchored' + \
                           ") is invalid for `$boss`.\n" +
                           "You cannot anchor events or bosses of this kind.\n")
            ecode = vaivora_constants.values.error_codes.wrong
        elif etype == vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][vaivora_constants.command.syntax.BAD][vaivora_constants.command.syntax.SYN][2]:
            ret_msg.append(user_name + " Your command for `$boss` had too few arguments.\n" + \
                           "Expected: 4 to 6; got: " + msg + ".\n")
            ret_msg.append(vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.G][1])
            ecode = vaivora_constants.values.error_codes.syntax
        elif etype == vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][vaivora_constants.command.syntax.BAD][vaivora_constants.command.syntax.SYN][4]:
            ret_msg.append(user_name + " Your command for `$boss` had misused quotes somewhere.\n")
            ret_msg.append(vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.G][1])
            ecode = vaivora_constants.values.error_codes.syntax
        elif etype == vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][vaivora_constants.command.syntax.BAD][vaivora_constants.command.syntax.SYN][1]:
            ret_msg.append(user_name + " Your command could not be parsed. Re-check the syntax, and try again.\n" + \
                           ("Message: " + msg) if msg else "")
            ret_msg.append(vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.G][1])
            ecode = vaivora_constants.values.error_codes.syntax
        else:
            ret_msg.append(user_name + cmd_usage['debug'] + "\n" + etype)
            ret_msg.append(vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.G][1])
            ecode = vaivora_constants.values.error_codes.syntax
            await client.send_message(channel, '\n'.join(ret_msg))
            return ecode
        # end of conditionals for vaivora_constants.command.syntax.cmd_boss

        # begin common return for $boss
        ret_msg.append("For syntax: $boss help")
        await client.send_message(channel, '\n'.join(ret_msg))
        return ecode
        # end of common return for $boss

    # todo: reminders, Talt tracking, permissions
    else:
        # todo
        ret_msg.append(user_name + cmd_usage['debug'])
        ret_msg.append(vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.G][1])
        ecode = vaivora_constants.values.error_codes.syntax
        await client.send_message(channel, '\n'.join(ret_msg))
        return ecode 
# end of error

# @func:  the_following_argument(str): begin concatenated string
# @arg:
#     arg: str; e.g. boss, map, time
# @return:
#     str, containing message
def the_following_argument(arg):
    return " The following argument `" + arg + "` ("
# end of the_following_argument

with open('discordtoken', 'r') as f:
    secret = f.read()

client.loop.create_task(check_databases())
client.run(secret)