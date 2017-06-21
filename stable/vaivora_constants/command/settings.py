#vaivora_constants.command.boss
#requires: vaivora_constants.command.syntax
import vaivora_constants.command.syntax

modname         =   "settings"

command         =   []

cmd_frag        =   vaivora_constants.command.syntax.code_block + "ini\n" + "[$settings] commands" + "\n" + \
                    ";===================" + "\n" + \
                    vaivora_constants.command.syntax.heading + "\n"

N               =   "necessary"
O               =   "optional"
H               =   "help"

A               =   "type A"
B               =   "type B"
C               =   "type C"
D               =   "type D"
E               =   "type E"

arg             =   dict()
arg[N]          =   dict()
arg[N][0]       =   "[prefix]"
arg[N][1]       =   "[settings]"
arg[N][2]       =   dict()
arg[N][2][A]    =   "[(un)set|get|rm]"
arg[N][2][B]    =   "[(un)verify|(in)validate]"
arg[N][2][C]    =   "[promote|demote]"
arg[N][3]       =   dict()
arg[N][3][A]    =   "[talt]"
arg[N][3][B]    =   "[channel]"
arg[N][3][C]    =   "[role]"
arg[N][3][D]    =   "[prefix]"
arg[N][4]       =   dict()
arg[N][4][A]    =   "[n]"
arg[N][4][B]    =   "[user|group]"
arg[N][4][C]    =   "[['custom prefix']]"
arg[N][4][D]    =   "[boss|management]"
arg[N][4][E]    =   "[authorized|member]"
arg[O]          =   dict()
arg[O][1]       =   "(user ...)"
arg[O][2]       =   "(talt|points)"
arg[O][3]       =   "(channel ...)"
arg[H]          =   "[help]"

                #       $         settings          (un)set|get          talt                 n                    units             user(s)           
                #       $         settings          (un)set|get          channel              boss|mgmt            channel(s)
                #       $         settings          veri|(in)val         talt                 user(s)/grp
                #       $         settings          (un)set|get          prefix               custom pre
                #       $         settings          (un)set|get          role                 auth|member          user(s)
                #       $         settings          (pro/de)mote         user(s)/grp
usage       =   arg[N][0] + " " + arg[N][1] + " " + arg[N][2][A] + " " + arg[N][3][A] + " " + arg[N][4][A] + " " + arg[O][2] + " " + arg[O][1] + "\n" + \
                arg[N][0] + " " + arg[N][1] + " " + arg[N][2][A] + " " + arg[N][3][B] + " " + arg[N][4][D] + " " + arg[O][3] + "\n" + \
                arg[N][0] + " " + arg[N][1] + " " + arg[N][2][B] + " " + arg[N][3][A] + " " + arg[N][4][B] + "\n" + \
                arg[N][0] + " " + arg[N][1] + " " + arg[N][2][A] + " " + arg[N][3][D] + " " + arg[N][4][C] + "\n" + \
                arg[N][0] + " " + arg[N][1] + " " + arg[N][2][A] + " " + arg[N][3][C] + " " + arg[N][4][E] + " " + arg[N][4][B] + "\n" + \
                arg[N][0] + " " + arg[N][1] + " " + arg[N][2][C] + " " + arg[N][4][B] + "\n"
usage           +=  vaivora_constants.command.syntax.code_block

cmd_frag    +=  usage
command.append(cmd_frag)

arg_info    =   list()
arg_info.append(vaivora_constants.command.syntax.code_block + "ini\n")
arg_info.append(";===================\n")
arg_info.append(arg[N][0] + "\n" + \
                "    (default) [$] or [Vaivora, ]; this server may have others. Run [$settings get prefix] to check.\n")
arg_info.append(arg[N][1]  + "\n" + \
                "    (always) [" + modname + "]; goes after prefix. e.g. [$" + modname + "], [Vaivora, " + modname + "]\n")
arg_info.append(arg[N][2][A]  + "\n" + \
                "; requires [talt], [channel], [role], and [prefix]\n" + \
                "    Changes mode of setting for the appropriate item.\n")
arg_info.append(arg[N][2][B]  + "\n" + \
                "; requires [talt] only\n" + \
                "    Confirms or denies [member]-tier submissions, either by user or all if optional user argument is blank.\n")
arg_info.append(arg[N][2][C]  + "\n" + \
                "    A convenience command for raising user privilege directly.\n" + \
                "    Raises or lowers the associated users from [None] to [member] to [authorized].\n")
arg_info.append(arg[N][3][A]  + "\n" + \
                "; requires [set], [get], [unset], and [rm] with [talt] or [role];\n" + \
                ";          [verify], [unverify], and [validate], or [invalidate] with [talt]; or \n" + \
                ";          [promote] or [demote]\n"
                "    Changes the associated target's or targets' [talt] contribution.\n")
arg_info.append(arg[N][3][B]  + "\n" + \
                "; requires [set], [get], [unset], or [rm]\n" + \
                "    Changes the associated [channel]'s properties: [management] or [boss].\n")
arg_info.append(arg[N][3][C]  + "\n" + \
                "; requires [set], [get], [unset], or [rm]\n" + \
                "    Changes the associated target's or targets' Wings of Vaivora [role].\n")
arg_info.append(arg[N][3][D]  + "\n" + \
                "; requires [set], [get], [unset], or [rm]\n" + \
                "    Adds or remove a custom [prefix] for the server to use.\n")
arg_info.append(vaivora_constants.command.syntax.code_block)
cmd_frag        =  ''.join(arg_info)
command.append(cmd_frag)

arg_info    =   list()
arg_info.append(vaivora_constants.command.syntax.code_block + "ini\n")
arg_info.append(arg[N][4][A]  + "\n" + \
                "; requires [set] and [rm], with [talt]\n" + \
                "    Registers the [talt] contribution for the associated target's or targets'.\n")
arg_info.append(arg[N][4][B]  + "\n" + \
                "; requires [set], [get], [unset], [rm] with  [promote], [demote]\n" + \
                "    Targets the [user] or [group].\n")
arg_info.append(arg[N][4][C]  + "\n" + \
                "; requires [set], [get], [unset], or [rm]\n" + \
                "    Adds or removes a custom prefix to use instead of [$] or [Vaivora, ].\n")
arg_info.append(arg[N][4][D]  + "\n" + \
                "; requires [set], [get], [unset], or [rm]\n" + \
                "    Changes the target [channel] or channels' property to [management] or [boss].\n")
arg_info.append(arg[N][4][E]  + "\n" + \
                "; requires [set], [get], [unset], or [rm]\n" + \
                "    Changes the target [user]s or [group]s to [member] or [authorized].\n")
arg_info.append(arg[O][1]     + "\n" + \
                "; (optional) Default: uses the user who typed the command\n" + \
                "    Suitable only for [talt] settings, if changing contribution to others.\n")
arg_info.append(arg[O][2]     + "\n" + \
                "; (optional) Default: uses Talt as unit\n" + \
                "    Suitable only for [talt] settings. Sets units to be used.\n")
arg_info.append(arg[O][3]     + "\n" + \
                "; (optional) Default: uses channel the command was typed in\n" + \
                "    Suitable only for [channel] settings. Directly names channels to be assigned types.\n")
arg_info.append(vaivora_constants.command.syntax.code_block)

cmd_frag        =  ''.join(arg_info)
command.append(cmd_frag)

examples        =   vaivora_constants.command.syntax.example + \
                    "[$settings set role authorized @user1 @user2]\n" + \
                    "[$settings unset role member @everyone @sorry] ; remove entries\n" + \
                    "[$settings get talt] ; this returns how much Talt the guild has\n" + \
                    "[$settings validate talt @contributor @taltdaddy] ; validates users' contributions, or leave blank to validate all\n" + \
                    "[$settings invalidate talt] ; why you do this?\n" + \
                    "[$settings get role member] ; prints all the member-tier users\n" + \
                    "[$settings set talt 1000 @richman] ; add Talt to someone else if they didn't do it\n" + \
                    "[$settings set talt 1000] ; boy, you're rich!\n" + \
                    "[$settings set channel boss #bus_times] ; this is totally appropriate\n"

cmd_frag        = vaivora_constants.command.syntax.code_block + "ini\n" + examples

cmd_frag        += vaivora_constants.command.syntax.code_block
command.append(cmd_frag)

acknowledge     = "Thank you! Your command has been acknowledged and recorded.\n"
