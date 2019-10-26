# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [4.0] - Unreleased
### Added
- [`vaivora.boss`](vaivora/boss.py) now contains most of the data handling for the [boss cog](cogs/boss.py). Subsequently, many functions were migrated from the cog to the new class.
- [`vaivora.config`](vaivora/config.py) is now used for one-time loading configuration files
- Exception handling added to [`checks.py`](checks.py), to replace sending messages from the checks themselves
- [`vaivora.db`](vaivora/db.py) now uses user-defined `Exceptions` instead of simply `return`ing `False`.
- Better type-hints and docstrings. This may not propagate entirely - we'll see.

### Changed
- Prefix changed to `v!`. `$` is too common, and the others were extraneous.
- Use `yaml.safe_load` instead of `yaml.load`
- Replaced `Exception` in [`vaivora.db`](vaivora/db.py) with more specific `sqlite3.OperationalError`.
- Moved DB validity check from background loop to `before_loop`.
- Loggers are now created in [`vaivora.config`](vaivora/config.py).
- Some `on_guild_join` logic in [`bot.py`](bot.py) was moved into a listener function that replaced the old `add_new_guild` in both [`cogs.boss`](cogs/boss.py) and [`cogs.events`](cogs/events.py)
- Broke this changelog into two: [this](CHANGELOG.md) file and [one](CHANGELOG-pre_2.0.md) for before 2.0, the first update compatible with the now-stable `discord.py`.
- Older version syntax in the new changelog has been converted to the standard used in the current changelog. i.e. `1.1` or `1.1.1`. e.g. `m1.0` -> `1.0`, `m1.1a` -> `1.1.1`

### Removed
- Presence setting in `on_ready` in [`bot.py`](bot.py)

## [3.8.1] - 2019-08-21
### Added
- Used `inspect.cleandoc` to format triple-quoted strings
- Added `asyncio.sleep` to every message chunking to prevent spamming
- Message chunking is now used in every applicable block
- [`vaivora.db.Database.get_channel`](vaivora/db.py) became `get_channels`, as the function returns a list
- Added `logging`, replacing barbaric `print`s; outputs to `vaivora.log`

## [3.8] - 2019-08-21
### Added
- New message chunking in [`vaivora.common`](vaivora/common.py) to better process sending a list of messages
- Background handling migrated from [`bot.py`](bot.py) to respective modules, [`cogs.boss`](cogs/boss.py) and [`cogs.events`](cogs/events.py) - #18

### Changed
- Reverted from `constants` to use f-strings
- Migrated from `secrets.py` to [`config.yaml`](config.yaml.example) for better settings management; include `PyYAML` for this
- Likewise, moved the actual "constants" (bosses; guild from `$settings`) into their respective files [`boss.yaml`](boss.yaml) and [`guild.yaml`](guild.yaml)
- Updated [`README.md`](README.md)
- Renamed `vaivora.utils` to [`vaivora.common`](vaivora/common.py) to distinguish from `utils`
- Updated both [`utils.convert_db`](utils/convert_db.py) and [`utils.force_rebuild`](utils/force_rebuild.py), replacing `os` with `pathlib.Path`; add some exceptions instead of returning `False`
- ([`bot.py`](bot.py)) `bot.run` changed to `bot.start`
- Bumped to Python 3.7, because some f-strings won't work otherwise

### Deprecated
- Removed `pynt`; `build.py` will also be removed in a near future update - not useful for configuration

## [3.7] - 2019-05-27
### Added
- New subcommands `values` and `efficiency` under `$gems` - #13

## [3.6.2] - 2019-05-18
### Changed
- Individual command checks are now consolidated as best as possible using parent commands.

### Fixed
- Custom events can now be added as intended - #18

## [3.6.1] - 2019-04-25
### Fixed
- Critical/major issues listed on the repo, in particular:
    - Events alerts output to repeatedly - #14
    - Events outputs to the wrong channel - #15
    - Permanent events ignore the day they're supposed to run - #16
- Events should now be addable. - #17

## [3.6] - 2019-04-24
### Added
- New command [`$events`](cogs/events.py) and [doc](docs/EVENTS.md)
- By extension, `$settings` can now add/set/remove users/roles/channels as `events`.

### Changed
- Boss constants were cleaned up to be more readable.
- Docstrings were simplified.
- Type hints are now used in every situation without ambiguous arguments.
- Some variable names were made more uniform.
- `get_time_diff` was made more versatile and should handle even edge cases.
- Moved both `process_record` and `get_time_diff` from [`bot.py`](bot.py) to reduce clutter.
- Moved `get_offset` from `$boss` and renamed it `get_boss_offset` to make it less ambiguous.
- The background loop in [`bot.py`](bot.py) has been broken into smaller chunks.
- Combined some offset/tz calculating functions into one in [`vaivora.utils`]

### Fixed
- Boss role mentions should no longer be erroneously removed from alerts.
- Listing boss results should now accurately conform to a guild offset and time zone.
- Getting Vaivora-set channels should now work again.
- `$settings` commands now have proper exception catching for commands.

## [3.5] - 2019-04-09
### Changed
- Adjusted the versioning to be slightly more sensible.
- `$admin reload` was broken into 3 composite parts:
    - `$admin reload_all` now achieves what `$admin reload` formerly did
    - `$admin reload <cog> ...` now lets the user reload individual cogs
    - `reloader` was added as a middleman between both Discord commands and the commandline

## [3.4.1] - 2019-04-09
### Added
- New document was added for [`$admin`](docs/ADMIN.md)

### Changed
- `discord.py` was added back to [`requirements.txt`](requirements.txt) as "rewrite" is now stable.

## [3.4] - 2019-04-06
### Added
- New [cog](cogs/admin.py) for administration - `$admin`

## [3.3] - 2019-03-27
### Changed
- `server_settings` has been deleted, as they're no longer used.

### Fixed
- Vaivora member role users can now use some `$settings` commands as intended, if their role was based on Discord roles. - #8

## [3.2.1] - 2019-03-19
### Added
- Additional range slices for `$settings get points`. You can now choose from `a-b`, `-b`, or `a-`. - #6

### Fixed
- `$gems gem2lv` now no longer breaks when final levels exceed 8. - #5
- Boss record checks should now play nicely with `$offset` related changes. - #7

## [3.2] - 2019-03-07
### Fixed
- Wings of Vaivora now runs on the latest rewrite.

## [3.1] - 2019-03-06
### Added
- `remove`, `unset` subcommands for `$settings`. You can now remove problematic Discord IDs.
- Similarly, commands that yield invalid parameters (e.g. deleted channels, roles) will automatically attempt to prune those invalid mentions.
- `add` subcommand for contributions, so you don't have to set all the time.
- `$gems` was added as a [cog](cogs/gems.py). Now you can calculate gem experience on the fly.
- A new command `$offset` was added to [cogs](cogs/offset.py).
- `$offset` lets you assign time zone and offset, on a per-guild basis.

### Changed
- Time difference is no longer static. Depends now on local time for the host, and per-guild with `$offset`.
- An unintended consequence of allowing custom time zones and offsets is that records are now recorded in respect to local time. That is to say, the boss spawn time is directly written to the database. No reverse manipulation is required.
- Related to the time changes, `pendulum` behaves much more differently than the original `datetime`.

### Fixed
- Servers can now set their own time zone and delays. - #1

## [3.0] - 2019-02-26
### Added
- Custom checks were added, to streamline valid command usage.
- Add separate command groups for settings commands.
- Made a mistake with channels? You can now use `$settings purge` to erase them to redo.
- Cogs. ~~Unfortunately, `$boss` cannot be made into a cog due to argument positioning.~~
- Releases are now available. Release archives can be made using [`build.py`](build.py).
- In case the database has issues (you'll notice in startup if it happens), run [`force_rebuild.py`](utils/force_rebuild.py). ***This is destructive.***
- [Migrating document](docs/MIGRATING.md) added for info about migration to "rewrite".

### Changed
- The `$settings` module has been rewritten from a class interface to a helper module for the `db` module.
- `$settings` no longer has its own class. Instead, it will act as a middleman similar to how `$boss` works.
- [`db.py`](vaivora/db.py) consequently has become the backend of data manipulation.
- Existing boss records will be dumped from this update. Fields now use `integer` instead of `real`. (No more decimal precision!) [`convert_db.py`](utils/convert_db.py) must be run to ensure this happens.
- Owners are now automatically added `s-authorized` on each boot. Old owners are removed to prevent loopholes.
- File checks in `check_databases()` in [`bot.py`](bot.py) will skip problematic databases.
- Similarly, all duplicates in tables `roles`, `channels`, and `contributions` will be removed.
- Likewise, existing entries with `s-authorized` roles are removed.
- "Separate command groups for settings" means that all current and future `$settings` subcommands will literals, not regex. i.e. `$settings set channel boss #channel` instead of something like `$settings set ch boss #channel`.
- `vaivora_modules` changed to `vaivora`. Brevity is the soul of wit.
- `$settings` was moved to [cogs](cogs/settings.py).
- `$boss` and `meme`s are now [cogs](cogs/boss.py) [too](cogs/meme.py).
- Some `$settings` commands now no longer require `authorized` to use. e.g. `member`s are able to set their own contribution record.

### Deprecated
- Translation modules moved out of their respective directories. I don't think this project will ever be made to run in multiple languages simultaneously.
- `server_settings` directory to be deleted a month after this version releases.

### Removed
- `$settings <validation>` commands were removed. Instead, `member`s are now trusted to set some records. (See Changed)

## [2.0] - 2019-02-11
### Added
- Documents for more info have been added to `docs`.
- [`utils`](utils): utilities for managing/adjusting files
- [`convert_db.py`](utils/convert_db.py) added to transfer data from legacy server settings json files to sqlite database.

### Changed
- Wings of Vaivora now uses the discord.py rewrite branch.
- `sqlite3` was swapped for `aiosqlite`.
- Similarly, `json` settings were migrated to `aiosqlite`.
- README has been refreshed.
- Constants were added back, with eventual translation modules possible.
- Changelogs are now in a more digestible format! with styling from https://keepachangelog.com/

### Deprecated
- Current `$settings` module will be modernized.

### Removed
- Old files including old server settings, version files, etc.
