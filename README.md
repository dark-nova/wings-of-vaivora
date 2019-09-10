# Wings of Vaivora

## Overview

**Wings of Vaivora**, a [Discord][discord] bot made for [Tree of Savior][tos], was created using [`discord.py`][discord.py]. The bot aims to enhance or simplify some mechanics in-game, notably through a reminder system. Wings of Vaivora was originally inspired by a similar Discord bot named **Talt Bot**, authored by **Velcro**.

## Branches

- `master`, the stable version: [3.8.1]
    - You should expect the bot to work if configured correctly.
- `rewrite`, the development version: [3.8.1]
    - The bot may **not** run. You should not use this.
- `asyncio_archive`, the archived version: [n1.9g]
    - You should not use this. Built on `discord.py` "asyncio".

## Usage

Command usage below:

- [`$boss` for Boss Tracking](docs/BOSS.md)
- [`$settings` for Guild Settings](docs/SETTINGS.md)
- [`$gems` for Gem Calculations](docs/GEMS.md)
- [`$offset` for Time Zones and Offsets](docs/OFFSET.md)
- [`$events` for Event Tracking](docs/EVENTS.md)
- [`$admin` for (limited) administration commands](docs/ADMIN.md)

## Requirements

This code is designed around the following:

- Python 3.7
    - [`discord.py`][discord.py] and all of its dependencies
    - other [requirements](requirements.txt)
- setup with [Discord Developer Apps][dev]
    - create an application, create a bot user from the application, get the token

## Setup

Set up your environment for self-hosting. Read [Requirements](#Requirements) for dependencies.
Python `venv` is highly recommended for managing your files, including dependencies.
Like so:

```
$ git clone <url> && cd wings-of-vaivora
$ # venv may be installable in package management.
$ # For Debian-like distros, `apt install python3-venv`
$ python -m venv venv
$ . venv/bin/activate
(venv) $ pip install -r requirements.txt
(venv) $ # See directly below for setting up your config.
(venv) $ python bot.py
```

To set up your configuration, copy [`config.yaml.example`](config.yaml.example) into `config.yaml` and change all the fields according to your build. I have left some defaults that may be preferred.

You may also want to customize [`emoji.yaml`](emoji.yaml.example). Copy from `emoji.yaml.example` to `emoji.yaml` and change the values as you'd like. You may also use custom emojis if you choose.

⚠ Note that this setup has only been tested on Debian-like distros. Other \*nix derivatives should work fine, but no guarantees will be made. **Windows is not supported.**

⚠ The community of `discord.py` strongly recommends using an init-like management tool, e.g. `systemd`, if you desire to run the script in the background. I leave you to research how to set this up.

## Migrating from "asyncio"
- Read [here](docs/MIGRATING.md)

## Contributing
- Read [here](docs/CONTRIBUTING.md)

## Disclaimer

This project is not affiliated with or endorsed by [Tree of Savior][tos], [Discord][discord], or [`discord.py`][discord.py]. See [`LICENSE`](LICENSE) and [terms of use](TERMS.md) for more detail.


[tos]: https://treeofsavior.com/
[discord]: https://discordapp.com/
[discord.py]: https://github.com/Rapptz/discord.py
[api]: http://discordpy.readthedocs.io/en/latest/api.html
[dev]: https://discordapp.com/developers/applications/me