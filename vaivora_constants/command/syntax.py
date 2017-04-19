#vaivora_constants.command.syntax

# cmd['talt']                 = "Command: Talt Tracker" ####TODO
# cmd['reminders']            = "Command: Reminders"    ####TODO


cmd_pre         = "Command: "
cmd_boss        = cmd_pre + "Boss\n"

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
cmd_error[G]                    = dict()
cmd_error[G][1]                 = command_was + "malformed.\n"
cmd_error_cmd_malformed         = cmd_error[G][1]
cmd_error[G][2]                 = command_was + "ambiguous.\n"
cmd_error_cmd_ambiguous         = cmd_error[G][2]
cmd_error[G][3]                 = command_was + "correct, but the data was wrong.\n"
cmd_error_cmd_wrong             = cmd_error[G][3]

# Make sure to properly record the boss's...
cmd_error[B]                    = dict()
cmd_error[B][1]                 = boss_msg + "name.\n"
cmd_error_record_name           = cmd_error[B][1]
cmd_error[B][2]                 = boss_msg + "map.\n"
cmd_error_record_map            = cmd_error[B][2]
cmd_error[B][3]                 = boss_msg + "status.\n"
cmd_error_record_status         = cmd_error[B][3]

cmd_error[R]                    = dict()
cmd_error[R][0]                 = R + "Unknown\n"
cmd_error_unknown               = cmd_error[R][0]
cmd_error[R][1]                 = R + "Ambiguous\n"
cmd_error_ambiguous             = cmd_error[R][1]

cmd_error[R][BAD]               = dict()

# Reason: Bad ...
cmd_error[R][BAD][SYN]          = dict()
cmd_error[R][BAD][SYN][1]       = R + BAD + "Syntax\n"
cmd_error_bad_syntax            = cmd_error[R][BAD][SYN][1]
cmd_error[R][BAD][SYN][2]       = R + BAD + "Argument Count\n"
cmd_error_bad_syntax_arg_ct     = cmd_error[R][BAD][SYN][2]
cmd_error[R][BAD][SYN][3]       = R + BAD + "Database\n"
cmd_error_bad_syntax_db         = cmd_error[R][BAD][SYN][3]
cmd_error[R][BAD][SYN][4]       = R + BAD + "Quote Count\n"
cmd_error_bad_syntax_quote      = cmd_error[R][BAD][SYN][4]

# Reason: Bad Boss ...
cmd_error[R][BAD][BOSS]         = dict()
cmd_error[R][BAD][BOSS][1]      = R + BAD + BOSS + "Name\n"
cmd_error_bad_boss_name         = cmd_error[R][BAD][BOSS][1]
cmd_error[R][BAD][BOSS][2]      = R + BAD + BOSS + "Map\n"
cmd_error_bad_boss_map          = cmd_error[R][BAD][BOSS][2]
cmd_error[R][BAD][BOSS][3]      = R + BAD + BOSS + "Time\n"
cmd_error_bad_boss_time         = cmd_error[R][BAD][BOSS][3]
cmd_error[R][BAD][BOSS][3.1]    = R + BAD + BOSS + "Time (Overlap)\n"
cmd_error_bad_boss_time_wrap    = cmd_error[R][BAD][BOSS][3.1]
cmd_error[R][BAD][BOSS][4]      = R + BAD + BOSS + "Channel (Field)\n"
cmd_error_bad_boss_channel      = cmd_error[R][BAD][BOSS][4]
cmd_error[R][BAD][BOSS][5]      = R + BAD + BOSS + "Status (Anchor)\n"
cmd_error_bad_boss_status       = cmd_error[R][BAD][BOSS][5]
