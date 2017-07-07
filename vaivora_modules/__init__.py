__all__ =   [     "db", \
                  "version", \
                  "boss", \
                  "settings", \
                  "secrets"
            ]

vaivora = [ "vaivora_modules" ] * len(__all__)

modules = [ '.'.join(t) for t in zip(vaivora, __all__) ]