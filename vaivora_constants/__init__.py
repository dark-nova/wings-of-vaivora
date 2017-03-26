__all__ = [ #"values", \
            #"command", \
            #"regex", \
            #"values.time", \
            "values.time.wait", \
            "values.time.offset", \
            "values.time.seconds", \
            "command.syntax", \
            # command.boss requires command.syntax
            "command.boss", \
            # values.words.message requires command.boss
            "values.words.message", \
            "values.filenames", \
            "values.error_codes", \
            # "command.talt_tracker", \
            # "command.reminders", \
            "regex.db", \
            "regex.boss.status", \
            "regex.boss.location", \
            "regex.boss.command", \
            "regex.format.matching", \
            "regex.format.time"
            ]

vaivora = [ "vaivora_constants" ] * len(__all__)

modules = [ '.'.join(t) for t in zip(vaivora, __all__) ]