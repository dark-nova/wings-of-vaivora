# Wings of Vaivora
#### _A [Tree of Savior][tos] [Discord][discord] bot project._

## Overview

**Wings of Vaivora** runs on the [discord.py][discord.py] [API][api].

This repository contains 3 branches:
- `master`, the stable version. You should expect the bot to work if configured correctly.
- `rewrite`, the development version. The bot may **not** run. You should not use this.
- `asyncio_archive`, the archived version built on discord.py "asyncio".

## Usage
- [`$boss` for Boss Tracking](docs/BOSS.md)
- [`$settings` for Guild Settings](docs/SETTINGS.md)
- [`$gems` for Gem Calculations](docs/GEMS.md)
- [`$offset` for Time Zones and Offsets](docs/OFFSET.md)
- [`$admin` for (limited) administration commands](docs/ADMIN.md)

## Requirements
_subject to change_

- latest Python 3 (`3.6` to `3.7`)
- [discord.py][discord.py] and all of its dependencies
- dependencies in [requirements.txt](requirements.txt)
- setup with [Discord Developer Apps][dev]; use `pynt` (see Setup) to add your bot token

## Setup
Set up your environment for self-hosting. Read Requirements for dependencies.
Python virtualenv is highly recommended for managing your files, including dependencies.
Like so:

```
$ mkdir -p venv
$ python -m virtualenv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
$ pynt
```
Note: this setup has only been tested on Debian-like distros.

## Migrating from "asyncio"
- Read [here](docs/MIGRATING.md)

## Contributing
- Read [here](docs/CONTRIBUTING.md)


#### File last modified: 2019-04-24 17:38 (UTC-7)

[tos]: https://treeofsavior.com/
[discord]: https://discordapp.com/
[discord.py]: https://github.com/Rapptz/discord.py
[api]: http://discordpy.readthedocs.io/en/latest/api.html
[dev]: https://discordapp.com/developers/applications/me