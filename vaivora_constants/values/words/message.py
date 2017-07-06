#vaivora_constants.values.words.message
#requires: vaivora_constants.command.boss
#import vaivora_constants.command.boss

reason  =   "Reason: "
welcome =   "Thank you for inviting me to your server! " + "\n"  + \
            "I am a representative bot for the Wings of Vaivora, here to help you record your journey." + "\n" + "\n" + \
            "Here are some useful commands:" + "\n" + \
            """```ini
            [$boss ...] or [Vaivora, boss ...] ; refer to [$boss help] or [Vaivora, boss help] for more info ```""" + \
            "(To be implemented) Talt, Reminders, and Permissions. Check back soon!" + "\n" 
            # '\n'.join(cmd_usage['talt']) # + \
            # '\n'.join(cmd_usage['remi']) # + \
            # '\n'.join(cmd_usage['perm'])

helpmsg =   "Need help? You can ask me for info!" + "\n"  + \
            "Here are server-only commands: ```ini" + "\n"  + \
            "[boss]" + "\n" + \
            "```" + "\n"  + \
            "Here are DM-only commands: ```ini" + "\n" + \
            "[unsubscribe] [subscribe] ; subscribe to changelogs!" + "\n" + \
            "```" + "\n" + \
            "Here are some help commands for server and DM:  ```ini" + "\n" + \
            "[boss help]    ; for [$boss]" + "\n" + \
            "[help]         ; for general help and this message" + "\n" + \
            "```" + "\n" + \
            "Precede each command with a `prefix`." + "\n" + \
            "Valid `prefix`es: `Vaivora,<space>` and `$`" + "\n" + \
            "Examples: ```ini" + "\n" + \
            "[$boss help], [Vaivora, boss help]" + "\n" + \
            "[$help], [Vaivora, help]" + "\n" + \
            "```" + "\n"