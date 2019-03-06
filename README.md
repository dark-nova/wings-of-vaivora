# Wings of Vaivora
#### _A [Tree of Savior][tos] [Discord][discord] bot project._

## Overview

_Wings of Vaivora_ runs on the [discord.py][discord.py] [API][api] ("rewrite").
The previous version built on `discord.py` "asyncio" has been frozen in branch `asyncio_archive`.

## Usage
- [`$boss` for Boss Tracking](docs/BOSS.md)
- [`$settings` for Guild Settings](docs/SETTINGS.md)
- [`$gems` for Gem Calculations](docs/GEMS.md)

## Requirements
_subject to change_

- latest Python 3 (`3.6` to `3.7` are fine, but `3.6` is suggested)
- [discord.py][discord.py] and all of its dependencies
- dependencies in [requirements.txt](requirements.txt)
- setup with [Discord Developer Apps][dev]; use `pynt` (see Setup) to add your bot token

## Setup
Set up your environment for self-hosting. Read Requirements for dependencies.
Python virtualenv is highly recommended for managing your files, including dependencies.
Like so:

```
$ python -m virtualenv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
$ pynt
```

## Migrating from "asyncio"
- Read [here](docs/MIGRATING.md)

## Contributing
- Read [here](docs/CONTRIBUTING.md)


#### File last modified: 2019-03-05 16:15 (UTC-8)

[tos]: https://treeofsavior.com/
[discord]: https://discordapp.com/
[discord.py]: https://github.com/Rapptz/discord.py/tree/rewrite
[api]: http://discordpy.readthedocs.io/en/rewrite/api.html
[dev]: https://discordapp.com/developers/applications/me