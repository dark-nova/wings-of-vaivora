#vaivora_constants.values.words.message
#requires: vaivora_constants.command.boss
import vaivora_constants.command.boss

reason  =   "Reason: "
welcome =   "Thank you for inviting me to your server! " + \
            "I am a representative bot for the Wings of Vaivora, here to help you record your journey.\n" + \
            "\nHere are some useful commands: \n\n" + \
            vaivora_constants.command.boss.command + \
            '\n'*2 + \
            "(To be implemented) Talt, Reminders, and Permissions. Check back soon!\n"
            # '\n'.join(cmd_usage['talt']) # + \
            # '\n'.join(cmd_usage['remi']) # + \
            # '\n'.join(cmd_usage['perm'])
