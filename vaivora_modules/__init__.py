__all__ =   [
                "version",
                "disclaimer",
                "changelogs", 
                "secrets",
                "db",
                "boss",
                "settings"
            ]

vaivora =   [ "vaivora_modules" ] * len(__all__)

modules =   [ '.'.join(t) for t in zip(vaivora, __all__) ]