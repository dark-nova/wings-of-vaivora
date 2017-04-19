# import additional constants
from datetime import timedelta, datetime
from importlib import import_module as im
import vaivora_constants
for mod in vaivora_constants.modules:
    im(mod)

# @func:    formmat_message_boss(str, str, datetime, str, int)
# @arg:
#   boss:
#       str
def format_message_boss(boss, status, time, bossmap, channel):
    kubas_ch    = ''
    if vaivora_constants.regex.boss.status.warning.match(status):
        bossmap     = [bossmap,]
    elif boss in vaivora_constants.command.boss.bosses_world:
        bossmap     = vaivora_constants.command.boss.boss_locs[boss]
    elif bossmap == 'N/A':
        bossmap     = ['[Map Unknown]',]
    elif boss == "Blasphemous Deathweaver" and vaivora_constants.regex.boss.location.DW_AS.search(bossmap):
        bossmap     = [m for m in vaivora_constants.command.boss.boss_locs[boss][2:-1] if m != bossmap]
    elif boss == "Blasphemous Deathweaver":
        bossmap     = [m for m in vaivora_constants.command.boss.boss_locs[boss][0:2] if m != bossmap]
    else:
        bossmap     = [m for m in vaivora_constants.command.boss.boss_locs[boss] if m != bossmap]

    if boss == "Kubas Event":
        kubas_ch    = 1 if int(channel) == 2 else 2
        kubas_ch    = " [Machine of Riddles, ch."  + str(kubas_ch) + "]."

    if vaivora_constants.regex.boss.status.anchored.search(status):
        report_time = time+timedelta(hours=-3)
        status_str  = " was anchored"
    elif vaivora_constants.regex.boss.status.warning.search(status):
        report_time = time+timedelta(hours=-2)
        status_str  = " was warned to spawn"
    else:
        if   boss in vaivora_constants.command.boss.boss_spawn_02h:
            report_time = time+timedelta(hours=-2)
        elif boss in vaivora_constants.command.boss.boss_spawn_16h:
            report_time = time+timedelta(hours=-16)
        else:
            report_time = time+timedelta(hours=-4)
        status_str = " died"

    status_str  = status_str + " in ch." + str(int(float(channel))) + " at "
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
                  expect_str + map_str + kubas_ch + "\n"
    return message