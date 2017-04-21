__all__ =   [     "db", \
                  "version", \
                  "utils", \
                  "boss"
            ]

vaivora = [ "vaivora_modules" ] * len(__all__)

modules = [ '.'.join(t) for t in zip(vaivora, __all__) ]