import asyncio

# import additional constants
from importlib import import_module as im
import vaivora_constants
for mod in vaivora_constants.modules:
    im(mod)

# constants
TIME        = "Time"
BOSS        = "Module: Boss"
REMINDERS   = "Module: Reminders"
TALT        = "Module: Talt Tracker"
PERMISSIONS = "Module: Permissions"

# database formats
columns = dict()
columns[TIME]           = ('year', 'month', 'day', 'hour', 'minute')
columns[BOSS]           = ('name', 'channel', 'map', 'status', 'text_channel') + columns[TIME]
columns[REMINDERS]      = ('user', 'comment') + columns[TIME]
columns[TALT]           = ('user', 'previous', 'current', 'valid') + columns[TIME]
columns[PERMISSIONS]    = ('user', 'role')

# and the database formats' types
types = dict()
types[TIME]             = ('real',)*5
types[BOSS]             = ('text',) + ('real',) + ('text',)*3 + types[TIME]
types[REMINDERS]        = ('text',)*2 + types[TIME]
types[TALT]             = ('text',) + ('real',)*3 + types[TIME]
types[PERMISSIONS]      = ('text',)*2

# zip, create, concatenate into tuple
boss_db         = tuple('{} {}'.format(*t) for t in 
                        zip(columns[BOSS], types[BOSS]))
reminders_db    = tuple('{} {}'.format(*t) for t in 
                        zip(columns[REMINDERS], types[REMINDERS]))
talt_db         = tuple('{} {}'.format(*t) for t in 
                        zip(columns[TALT], types[TALT]))
permissions_db  = tuple('{} {}'.format(*t) for t in
                        zip(columns[PERMISSIONS], types[PERMISSIONS]))


# def check_databases():
#     valid_dbs = []
#     no_repeat = []
#     ready_ent = dict()
#     try:
#         f = open(vaivora_constants.values.filenames.valid_db,'r')
#     except:
#         open(vaivora_constants.values.filenames.valid_db,'a').close()
#         f = open(vaivora_constants.values.filenames.valid_db,'r')
#     try:
#         g = open(vaivora_constants.values.filenames.no_repeat,'r')
#     except:
#         open(vaivora_constants.values.filenames.no_repeat,'a').close()
#         g = open(vaivora_constants.values.filenames.no_repeat,'r')

#     for line_f in f:
#         valid_dbs.append(line_f.strip())
#     for line_g in g:
#         no_repeat.append(line_g.strip())
#     for valid_db in valid_dbs:
#         # check all timers
#         message_send = list()
#         current_channel = str()
#         results[valid_db] = await func_discord_db(valid_db, check_boss_db, bosses)
#         # sort by time
#         if not results[valid_db]:
#             continue
#         results[valid_db].sort(key=itemgetter(5,6,7,8,9))
#         for result in results[valid_db]:
#             list_time = [int(t) for t in result[5:10]]
#             try:
#                 rtime = datetime(*list_time)
#             except:
#                 #TODO: remove entry
#                 continue
#             rtime_east = rtime + vaivora_constants.values.time.offset.pacific2server
#             tdiff = rtime-datetime.now()
#             # if tdiff < 0: # stale data; delete
#             #     await func_discord_db(valid_db, rm_ent_boss_db, bd=result)
#             # elif tdiff.seconds < 10800 and vaivora_constants.regex.boss.status.anchored.match(result[3]):
#             #     message_send.append(format_message_boss(result[0], result[3], rtime_east, result[1]))
#             #elif
#             if tdiff.days < 0:
#                 continue
#             if tdiff.seconds < 900 and tdiff.days == 0:
#                 msgb = []
#                 msgb.append(format_message_boss(result[0], result[3], rtime_east, result[2], result[1]))
#                 msgb.append(str(result[4]),)
#                 strm = str(result[4]) + ":" + str(result[0]) + ":" + str(result[3]) + ":" + \
#                        str(rtime_east) + ":" + str(result[1]) + "\n"
#                 if strm.rstrip() in no_repeat or strm in no_repeat:
#                     continue
#                 else:
#                     with open(vaivora_constants.values.filenames.no_repeat, 'a') as h:
#                         h.write(strm)
#                     message_send.append(msgb)
#             # elif tdiff.seconds > 72000:
#             #     await func_discord_db(valid_db, rm_ent_boss_db, result)
#         # message: str, str
#         if len(message_send) == 0:
#             continue

#         ready_ent[]

#         r = "@here"
#         srv = client.get_server(vaivora_constants.regex.db.ext.sub('', valid_db))
#         for role in srv.roles:
#             if role.mentionable and role.name == "Boss Hunter":
#                 r = role.mention
#                 break
#         for message in message_send:
#             if current_channel != message[-1] and not vaivora_constants.regex.format.matching.letters.match(message[-1]):
#                 if current_channel:
#                     messtr += "```"
#                     ready_ent[current_channel] = messtr
#                     await client.send_message(srv.get_channel(current_channel), messtr)
#                 current_channel = message[-1]
#                 #TODO: Replace 15 with custom server time threshold
#                 messtr = r + " The following bosses will spawn within " + "15" + " minutes: ```python\n"
#             messtr += message[0]
#         # flush
#         messtr += "```"
#         await client.send_message(srv.get_channel(current_channel), messtr)
#     #await client.process_commands(message)
#     f.close()
#     g.close()
