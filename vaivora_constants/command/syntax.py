#vaivora_constants.command.syntax

# cmd['talt']                 = "Command: Talt Tracker" ####TODO
# cmd['reminders']            = "Command: Reminders"    ####TODO

heading         = "Usage:\n"
code_block      = "```"
back_tick       = "`"
heading_arg     = "Arguments:\n"
example         = "Examples:\n"
debug_msg       = "Debug message. Something went wrong.\n"

make_sure       = "Make sure to properly record "
command_was     = "Your command was "

boss_arg        = "the boss's "
boss_msg        = make_sure + boss_arg


G               = "General"
B               = "Boss"
R               = "Reason: "

BAD             = "Bad "
BOSS            = "Boss "
SYN             = "Syntax "

cmd_error       = dict()
# Your ccommand was...
cmd_error[G]    = dict()
cmd_error[G][1] = command_was + "malformed.\n"
cmd_error[G][2] = command_was + "ambiguous.\n"
# Make sure to properly record the boss's...
cmd_error[B]    = dict()
cmd_error[B][1] = boss_msg + "name.\n"
cmd_error[B][2] = boss_msg + "map.\n"
cmd_error[B][3] = boss_msg + "status.\n"

cmd_error[R]                = dict()
cmd_error[R][0]             = R + "Unknown"

cmd_error[R][BAD]           = dict()

# Reason: Bad ...
cmd_error[R][BAD][SYN]      = dict()
cmd_error[R][BAD][SYN][1]   = R + BAD + "Syntax"
cmd_error[R][BAD][SYN][2]   = R + BAD + "Argument Count"
cmd_error[R][BAD][SYN][3]   = R + BAD + "Database"
cmd_error[R][BAD][SYN][4]   = R + BAD + "Quote Count"

# Reason: Bad Boss ...
cmd_error[R][BAD][BOSS]     = dict()
cmd_error[R][BAD][BOSS][1]  = R + BAD + BOSS + "Name"
cmd_error[R][BAD][BOSS][2]  = R + BAD + BOSS + "Map"
cmd_error[R][BAD][BOSS][3]  = R + BAD + BOSS + "Time"
cmd_error[R][BAD][BOSS][4]  = R + BAD + BOSS + "Channel (Field)"
cmd_error[R][BAD][BOSS][5]  = R + BAD + BOSS + "Status (Anchor)"
