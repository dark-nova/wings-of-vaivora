#vaivora_constants.command.boss
#requires: vaivora_constants.command.syntax
import vaivora_constants.command.syntax

command     =   vaivora_constants.command.syntax.code_block + "ini\n" + "[$boss] commands" + "\n" + \
                ";================" + "\n" + \
                vaivora_constants.command.syntax.heading + "\n"

N               =   "necessary"
O               =   "optional"
H               =   "help"

A               =   "type A"
B               =   "type B"

arg             =   dict()
arg[N]          =   dict()
arg[N][0]       =   "[prefix]"
arg[N][1]       =   dict()
arg[N][1][A]    =   "[boss|all]"
arg[N][1][B]    =   "boss"
arg[N][2]       =   dict()
arg[N][2][A]    =   "[died|anchored|warned]"
arg[N][2][B]    =   "[erase|list]"
arg[N][3]       =   "(time)"
arg[O]          =   dict()
arg[O][1]       =   "(chN)"
arg[O][2]       =   "(map)"
arg[H]          =   "help"

usage       =   arg[N][0] + " " + arg[N][1][B] + " " + arg[N][2][A] + " " + arg[N][3] + " " + arg[O][1] + " " + arg[O][2] + " " + "\n" + \
                arg[N][0] + " " + arg[N][1][A] + " " + arg[N][2][B] + " " + arg[O][2] + "\n" + \
                arg[N][0] + " " + arg[N][1][B] + " " + arg[H] + "\n"

command     +=  usage

arg_info    =   list()
arg_info.append(arg[N][1][B]  + "\n" + \
                "    Either part of, or full name; if spaced, enclose in double-quotes (`\"`)\n" + \
                "    [all] for all bosses\n")
arg_info.append(arg[N][2][A]  + "\n" + \
                "    Valid for [boss] only, to indicate its status. Do not use with [erase] or [list].\n")
arg_info.append(arg[N][2][B]  + "\n" + \
                "    Valid for both [boss] and [all] to [erase] or [list] entries.\n" + \
                "    Do not use with [died], [anchored], or [warned].\n")
arg_info.append(arg[N][3]     + " ; required for [died] and [anchored]\n" + \
                "    Remove spaces. 12 hour and 24 hour times acceptable, with valid delimiters \":\" and \".\". Use server time.\n")
arg_info.append(arg[O][2]     + " ; optional\n" + \
                "    Handy for field bosses* only. If unlisted, this will be unassumed.\n")
arg_info.append(arg[O][1]     + " ; optional\n" + \
                "    Suitable only for world bosses.[*] If unlisted, CH[1] will be assumed.\n" + "\n")
arg_info.append("[*] ; Notes about world and field bosses:\n" + \
                "    ; Field bosses in channels other than 1 are considered 'world boss' variants.\n" + \
                "    ; and should not be recorded because they spawn unpredictably.\n")

command     +=  ''.join(arg_info)

examples    =   vaivora_constants.command.syntax.example + \
                "[$boss cerb died 12:00pm 4f]        ; channel can be omitted for field bosses\n" + \
                "[Vaivora, boss crab died 14:00 ch2] ; map can be omitted for world bosses\n"

command     +=  examples

command     += "\n" + vaivora_constants.command.syntax.code_block


arg_min     = 3
arg_max     = 5

acknowledge = "Thank you! Your command has been acknowledged and recorded.\n"
