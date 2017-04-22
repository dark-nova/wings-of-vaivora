# import additional constants
from datetime import datetime, timedelta
from importlib import import_module as im
import vaivora_constants
for mod in vaivora_constants.modules:
    im(mod)

# @func:    check_boss(str) : int
#   checks boss validity
# @arg:
#     boss: str; boss name from raw input
# @return:
#     boss index in list, or -1 if not found or more than 1 matching
def check_boss(entry):
    match = ''
    for boss in vaivora_constants.command.boss.bosses:

        if entry in boss.lower():

            if not match:

                match = boss

            else:

                return -1
    
    if not match and entry in vaivora_constants.command.boss.boss_syns:

        for b, syns in vaivora_constants.command.boss.boss_synonyms.items():

            if entry in syns and not match:

                match = b

            elif entry in syns:

                return -1
    
    if not match:

        return -1

    return vaivora_constants.command.boss.bosses.index(match)

# @func:    check_maps(str, str) : int
#       begin code for checking map validity
# @arg:
#       maps: map name from raw input
#       boss: the corresponding boss, as guaranteed by variable
# @return:
#       map index in list, or -1 if not found or too many maps matched
def check_maps(maps, boss):
    map_number  = ''
    mapidx      = -1
    maps        = maps.lower()
    # Deathweaver map did not match
    if boss == "Blasphemous Deathweaver" and not vaivora_constants.regex.boss.location.DW_A.search(maps):
        return -1

    if boss in vaivora_constants.command.boss.bosses_with_floors:
        # rearrange letters, and remove map name
        if boss == "Wrathful Harpeia" or boss == "Demon Lord Blut":
            map_number = vaivora_constants.regex.format.matching.letters.sub('', maps)
            map_number = vaivora_constants.regex.boss.location.floors_arr.sub(r'\g<floornumber>', map_number)
        elif not vaivora_constants.regex.boss.location.floors_fmt.match(maps):
            map_number = vaivora_constants.regex.boss.location.floors_ltr.sub('', maps)
            map_number = vaivora_constants.regex.boss.location.floors_arr.sub(r'\g<basement>\g<floornumber>\g<floor>', map_number)
        else:
            map_number = vaivora_constants.regex.boss.location.floors_ltr.sub('', maps)

    #vaivora_constants.regex.format.matching.letters.sub(map_number)

    if boss == "Blasphemous Deathweaver" and vaivora_constants.regex.boss.location.DW_CM.search(maps):
        maps = "Crystal Mine " + map_number
    elif boss == "Blasphemous Deathweaver":
        maps = "Ashaq Underground Prison " + map_number
    elif map_number:
        maps = map_number
    elif boss in vaivora_constants.command.boss.bosses_with_floors and not map_number:
        return -1
    
    maps    = maps.lower()

    print(boss, maps, vaivora_constants.command.boss.boss_locs[boss])

    for m in vaivora_constants.command.boss.boss_locs[boss]:
        if maps in m.lower():
            print(maps, m)
            if mapidx != -1:
                return -1
            mapidx = vaivora_constants.command.boss.boss_locs[boss].index(m)

    return mapidx


# @func:    get_syns(str) : str
# @arg:
#       boss: the name of the boss
# @return:
#       a str containing a list of synonyms for boss
def get_syns(boss):
    return boss + " can be called using the following aliases: ```python\n" + \
           "#   " + '\n#   '.join(vaivora_constants.command.boss.boss_synonyms[boss]) + "```\n"

# @func:    get_maps(str) : str
# @arg:
#       boss: the name of the boss
# @return:
#       a str containing the list of maps for a boss
def get_maps(boss):
    return boss + " can be found in the following maps: ```python\n" + \
           "#   " + '\n#   '.join(vaivora_constants.command.boss.boss_locs[boss]) + "```\n"

# @func:    get_bosses_world() : str
# @return:
#       a str containing the list of world bosses
def get_bosses_world():
    return "The following bosses are considered world bosses: ```python\n" + \
           "#   " + '\n#   '.join(vaivora_constants.command.boss.bosses_world) + "```\n"

# @func:    get_bosses_field() : str
# @return:
#       a str containing the list of field bosses
def get_bosses_field():
    return "The following bosses are considered field bosses: ```python\n" + \
           "#   " + '\n#   '.join(vaivora_constants.command.boss.bosses_field) + "```\n"

# @func:    validate_channel(str) : int
# @arg:
#       boss: the name of the boss
# @return:
#       the channel parsed, or 1 (default) if ch could not be parsed or incorrect
def validate_channel(ch):
    if vaivora_constants.regex.boss.location.channel.match(ch):
        return int(vaivora_constants.regex.format.matching.letters.sub('', ch))
    else:
        return 1
