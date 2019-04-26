# Wings of Vaivora Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [3.6.1] - 2019-04-25
### Fixed
- Critical/major issues listed on the repo, in particular:
- Events alerts output to repeatedly #14
- Events outputs to the wrong channel #15
- Permanent events ignore the day they're supposed to run #16

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
- Moved both `process_record` and `get_time_diff` from [bot.py](bot.py) to reduce clutter.
- Moved `get_offset` from `$boss` and renamed it `get_boss_offset` to make it less ambiguous.
- The background loop in [bot.py](bot.py) has been broken into smaller chunks.
- Combined some offset/tz calculating functions into one in [vaivora.utils](vaivora/utils.py)

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
- `discord.py` was added back to [requirements.txt](./requirements.txt) as "rewrite" is now stable.

## [3.4] - 2019-04-06
### Added
- New [cog](cogs/admin.py) for administration - `$admin`

## [3.3] - 2019-03-27
### Changed
- `server_settings` has been deleted, as they're no longer used.

### Fixed
- Vaivora member role users can now use some `$settings` commands as intended, if their role was based on Discord roles. (#8)

## [3.2.1] - 2019-03-19
### Added
- Additional range slices for `$settings get points`. You can now choose from `a-b`, `-b`, or `a-`. (#6)

### Fixed
- `$gems gem2lv` now no longer breaks when final levels exceed 8. (#5)
- Boss record checks should now play nicely with `$offset` related changes. (#7)

## [3.2] - 2019-03-07
### Fixed
- Wings of Vaivora now runs on the latest rewrite.

## [3.1] - 2019-03-06
### Added
- `remove`, `unset` subcommands for `$settings`. You can now remove problematic Discord id's.
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
- Feature request #1 has been completed.

## [3.0] - 2019-02-26
### Added
- Custom checks were added, to streamline valid command usage.
- Add separate command groups for settings commands.
- Made a mistake with channels? You can now use `$settings purge` to erase them to redo.
- Cogs. ~~Unfortunately, `$boss` cannot be made into a cog due to argument positioning.~~
- Releases are now available. Release archives can be made using [build.py](./build.py).
- In case the database has issues (you'll notice in startup if it happens), run [force_rebuild.py](utils/force_rebuild.py). ***This is destructive.***
- [Migrating document](docs/MIGRATING.md) added for info about migration to "rewrite".

### Changed
- The `$settings` module has been rewritten from a class interface to a helper module for the `db` module.
- `$settings` no longer has its own class. Instead, it will act as a middleman similar to how `$boss` works.
- [db.py](vaivora/db.py) consequently has become the backend of data manipulation.
- Existing boss records will be dumped from this update. Fields now use `integer` instead of `real`. (No more decimal precision!) [convert_db.py](utils/convert_db.py) must be run to ensure this happens.
- Owners are now automatically added `s-authorized` on each boot. Old owners are removed to prevent loopholes.
- File checks in `check_databases()` in [bot.py](./bot.py) will skip problematic databases.
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
- [utils](utils): utilities for managing/adjusting files
- [convert_db.py](utils/convert_db.py) added to transfer data from legacy server settings json files to sqlite database.

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

## [i1.9f] - 2018-04-19
### Fixed
- Corrected issue with `$boss all list` when printing a very long list

## [n1.9e] - 2018-02-04
### Fixed
- Fixed `settings` help

### Acknowledgment
- Thanks to **Wolfy** for bug report.

## [n1.9d] - 2018-02-04
### Fixed
- Fixed role manipulation.

## [n1.9c] - 2018-01-18
### Fixed
- Fixed `$settings` `talt` module.

## [n1.9b] - 2018-01-18
### Fixed
- Corrected user mentions for `$boss`. May also have fixed mentions in other functions.

## [i1.9a] - 2018-01-09
### Changed
- Tidied up the boss module for obsoleted components.

### Fixed
- Corrected Molich spawn map.

### Acknowledgment
- Thanks to **Wolfy** for the information.

## [m1.9] - 2017-12-17
### Changed
- Updated boss maps (demon lords are now categorized as "demon" bosses)

### Acknowledgment
- Thanks to **TerminalEssence** for the confirmed information on boss timers

## [m1.8e] - 2017-12-04
### Changed
- `add_changelog.py` has been added to faciliate new changelog additions.
- Changelogs have also been migrated from a simple txt implementation to json.
- `add_changelogs.py` will be undergoing some additional changes later as well.

## [i1.8d] - 2017-08-24
### Fixed
- Boss role mention

### Upcoming
- Duplicate guild changelogs if person is server owner of more than 1 server

### Acknowledgment
- Thanks to **Jiyuu** for the bug report.

### Note
I'm actually getting quite burnt out on this project. I feel like with the exception of one person, nobody actually cares about the person behind the project.

I'm wearing thin, and I'm wearing thin _fast_.

As of now, one more bugfix is planned but after that, the project will be indefinitely on hold. If you want to contribute, feel free and I can pull merge requests.

## [i1.8c] - 2017-08-24
### Changed
- Began removing some files for uniform use (secrets go into secrets.py; example file on github in vaivora_modules)

### Fixed
- Corrected more things (boss module specifically) with unresolved id changes

## [i1.8b] - 2017-08-23
### Fixed
- Identified an issue with discord.py id's no longer having identifying punctuation, and fixed with a workaround

## [i1.8a] - 2017-08-23
### Fixed
- Fixed issue with boss role in settings
- Closed an open condition that led to exceptions

### Acknowledgment
- Thanks to **Jiyuu** for the bug report (boss role).

## [m1.8] - 2017-08-23
### Added
- Github: https://github.com/dark-nova/wings-of-vaivora

### Changed
- Settings has been fully rewritten, so that means I can push this as open source.
- Some "fun" easter eggs had to be removed to follow the new Discord Bot API.
- Boss timers should now be sorted by time descending.
- Disclaimer and Terms have been added.

### Fixed
- Corrected an unmentioned bug with wrong argument position for `$boss`

### Acknowledgment
- Thanks to **Jiyuu** for the feature request (time descending).

### Disclaimer and Terms
--- 2017/08/22, v.1 ---
- Data is not collected from users in an identifiable way. All data stored is in the form of id's generated by discord.py.
- However, please be aware that features later may involve personally identifiable data collection.
- Wings of Vaivora will have changes to the disclaimer for each of these updates. It is up to you to allow or deny.

## [i1.7v] - 2017-08-09
### Changed
- World boss timers are back

### Fixed
- Demon Lord set A spawns fixed (Inner Wall District 8, etc)

### Acknowledgment
- Thanks to **Donada** for the request (world boss timers).
- Thanks to **Jiyuu**, **Wolfy**, and **beeju** for the bug reports.

## [i1.7u] - 2017-08-08
### Fixed
- Channel setting

### Acknowledgment
Thanks to **Jiyuu** for the bug report.

## [i1.7t] - 2017-08-08
### Fixed
- Punctuation single quote

### Note
I have been really busy with life. I don't think I can maintain this project as much as I could before, and I've also had issues motivating myself with this project.

I will have the source readily available, at least one iteration of Wings of Vaivora, once I have completed rewriting Settings. Please bear with me. I know it's been a long while, and for those who may want to look into the code, I'm just one person maintaining everything.

Thank you.

## [i1.7s] - 2017-08-03
### Fixed
- Fixed 12pm errors.

## [i1.7r] - 2017-08-02
### Changed
- What is time? Seven hours, thirty minutes? Seven hours, twenty minutes? Seven hours, ten minutes? Seven hours?

## [i1.7q] - 2017-08-02
### Changed
- Changed Demon Lord spawns for real -- I should really just re-evaluate myself

## [i1.7p] - 2017-08-02 [YANKED]
### Changed
- Changed Demon Lord grouping

## [i1.7o] - 2017-08-01
### Added
- `$boss help` works now

### Changed
- Adjusted time to spawn for Demon Lords (for real now; issue was unnoticed arithmetic with regular time)

## [i1.7n] - 2017-08-01
### Fixed
- Adjusted time to spawn for Demon Lords.

## [i1.7m] - 2017-08-01
### Fixed
- Adjusted time to spawn for lesser field bosses.

### Acknowledgment
- Thanks to **Wolfy** for the contribution.

## [m1.7l] - 2017-07-31
### Added
- Adjusted field bosses and added two new records corresponding to "Alluring Succubus" and "Frantic Molich". Times are still hypothetical until the update arrives.

## [i1.7k] - 2017-07-28
### Added
- Added Abomination anchor option. `[$boss abom anchored 0:00]` produces an alert 1 hour from the anchor time.

### Fixed
- Set exception handling for tracking repeat messages

### Acknowledgment
- Thanks to **Wolfy** for the request (Abomination).

## [i1.7j] - 2017-07-20
### Fixed
- Set exception handling for emojis to prevent total bot failure
- Adjusted 12:00am as a time

### Acknowledgment
- Thanks to **Wolfy** for the bug report (time).

## [i1.7i] - 2017-07-08
### Fixed
- Adjusted anchor message using `$boss list`

## [i1.7h] - 2017-07-08
### Fixed
- Fixed logic errors with empty maps again - resolved with changing list with `Map Unknown` to empty string

## [i1.7g] - 2017-07-08
### Fixed
- Fixed logic errors with getting changelogs. Sorry, I know you guys must have gotten too many changelogs lately through PM, mostly repetitive.

## [i1.7f] - 2017-07-08
### Fixed
- Alerts are now fixed for a couple more issues.
    1. handling 12pm - solved using hour > 24 instead of hour > 23
    2. handling empty maps - solved by assigning an unbound variable on the condition

## [m1.7e] - 2017-07-08
### Changed
- Alerts will no longer use a redundant measure of text files in raw info to prevent repeat of duplicate mentions. And... (see Fixed)
- Caveat to new alert/periodic check system: if bot goes offline and you had a record still valid, you will receive at least one duplicate mention.

### Fixed
- Alerts are now fixed. Sorry. This was long overdue and I've had issues and was occupied today. This was a couple issues:
    1. not converting local time (Pacific Daylight Time) to server time (Eastern Daylight Time) - solved using `timedelta(hours=-3)`
    2. not sending to the right channel, instead a `str` which discord.py made no sense of - solved using `channel.id`
    3. not sending messages after input - solved using `message.server` instead of `server_id`
    4. not sending messages on account of syntax/type error - solved by typing to `str`

## [m1.7d] - 2017-07-07
### Fixed
- Apologies for the multiple changes to Wings of Vaivora. You may receive fewer notifications now.

### Note
- Reminder: you can unsubscribe using `$unsubscribe` in this DM.

## [n1.7c] - 2017-07-07
### Changed
- Boss module has been fully re-written.
- DB module has been re-written, partially. Probably won't need to re-write this in full.

### Fixed
- Corrected issues with boss module after rewrite.

### Upcoming
- Settings module re-write.
- Open source Vaivora later

## [i1.7b] - 2017-07-06
### Changed
- Boss module has been fully re-written.

### Note
- Formerly known as svn 2pre-2

## [n1.7a] - 2017-07-01
### Changed
- Migrated boss module files together, mostly.

### Note
- Formerly known as svn 2pre-1

## [i1.6r] - 2017-06-28
### Fixed
- Server join issue.
- Talt Tracker issue for setting remainder Talt via `$settings set (0-20) (current points)`.

## [i1.6q] - 2017-06-18
### Fixed
- Corrected an issue with `anchor` keyword for `$boss`.

### Upcoming
- Code rewrite before publishing as open source. Estimated time: 1-2 weeks

## [i1.6p] - 2017-06-15
### Fixed
- Corrected old boss record printing completely.

### Acknowledgment
- Thanks to **Wolfy** for the bug report.

## [i1.6o] - 2017-06-15
### Changed
- `$settings set talt ...` - sets target's Talt directly.
- `$settings add talt ...` - the former behavior of `set talt`; adds Talt.

## [i1.6n] - 2017-06-15
### Changed
- Better output for Talt commands.

## [i1.6m] - 2017-06-14
### Fixed
- Adjusted logic for mentioning group or users with boss alerts. For real this time.

### Acknowledgment
- Thanks to **Wolfy** for the bug report and additional testing.

## [i1.6l] - 2017-06-11
### Changed
- Change release system from [milestone, nightly] to [milestone, nightly, bugfix]

### Fixed
- Adjusted logic for mentioning group or users with boss alerts.

## [i1.6k] - 2017-06-11
### Fixed
- Fixed issues with mentions on boss notice.

### Acknowledgment
- Thanks to **Galoal** for the bug report.

## [i1.6j] - 2017-06-11
### Fixed
- Fixed issues with member level & Talt contribution.

## [m1.6i] - 2017-06-10
### Added
- `$settings get talt all` - to get all your guild's contribution
- `$settings reset talt [@user ...]` - to reset a user's contribution (to fix)
- `$settings rebase` - to rebuild Talt levels if you think something's wrong

### Fixed
- Corrected issue with Guild Level corresponding to Talt.

## [m1.6h] - 2017-06-10
### Fixed
- Identified and fixed issue with adding Talt for others. Was impromperly recorded to command user, not the target.

## [m1.6g] - 2017-06-10
### Fixed
- Correctly mentions people in `$boss` specific features, if assigned `boss` role.

## [m1.6f] - 2017-06-10
### Fixed
- Corrected logic issue with assigning permissions.

## [m1.6e] - 2017-06-10
### Added
- Talt verification is now in place.
- `$settings verify|validate [@user ...]`
- `$settings unverify|invalidate [@user ...]`
- Leave the mentions blank to mass (in)validate. Suitable only for `Authorized` roles only.

### Changed
- Changed an easter egg.

## [m1.6d] - 2017-06-09
### Fixed
- Corrected an issue with field boss entries not recording when map is omitted.

### Acknowledgment
- Thanks to **Wolfy** for the bug report.

## [m1.6c] - 2017-06-07
### Added
- Added `$settings help`.

## [m1.6b] - 2017-06-07
### Fixed
- Corrected issues with Talt Tracker: issues with individual permission comparison fixed.

### Acknowledgment
- Thanks to **Sunshine** for the bug report.

## [m1.6a] - 2017-06-07
### Fixed
- Corrected issues with Talt Tracker.

## [m1.6] - 2017-06-07
### Added
- Check out the new Settings module! `$settings help` for more info.

## [m1.5g] - 2017-06-06
### Changed
- Removed `@here` notification in preparation of custom setting. For now, you may use a role called `Boss Hunter` (caps important).

## [m1.5f] - 2017-05-19
### Fixed
- Revert previous "fix".

## [m1.5e] - 2017-05-19 [YANKED]
### Fixed
- Fixed argument count check. Preparing to condense some modules later for code clarity.

### Upcoming
- Open Source SoonTM

## [m1.5d] - 2017-05-15
### Fixed
- Corrected issue with some commands not printing.
- Subsequently, you may receive more than 1 message/response when you ask for help on a command.

### Acknowledgment
- Thanks to **Onesan** for the bug report.

## [m1.5c] - 2017-05-08
### Fixed
- Corrected issue with recording bosses on multiple channels.

## [m1.5b] - 2017-04-23
### Fixed
- Corrected issue with adding to (un)subscriptions.

### Acknowledgment
- Thanks to **Wolfy** for the bug report.

## [m1.5a] - 2017-04-23
### Fixed
- Corrected issue with specific deletions. Field boss records can now be deleted without issue.

## [m1.5] - 2017-04-22
### Added
- Added `$help` for commands. Give it a try in any channel or DM!

### Changed
- Added a small status to show when things are ready. Slightly better now.

## [m1.4] - 2017-04-21
### Added
- Added `$subscribe` and `$unsubscribe` to DM commands.
- You can subscribe to changelogs even if you're not a server owner.
- Added a small status to show when things are ready.

### Fixed
- Fixed issue with world bosses with no channel recorded as recorded as ch.0.

### Upcoming
- Talt T...I keep mentioning this.
- Ways to fetch changelogs.
- Better help system, and DM commands including feedback.

### Acknowledgment
- Thanks to **Jiyuu** for the feature request (status).

## [m1.3d] - 2017-04-21
### Note
- duplicate changelog of [m1.3c]

## [m1.3c] - 2017-04-21
### Fixed
- Fixed issue with Ellaganos not recording. Possibly some other bosses were impacted.

### Acknowledgment
- Thanks to **Jiyuu** and **Wolfy** for the bug report.

## [m1.3b] - 2017-04-20
### Fixed
- Fixed potential issue with Kubas interfering with boss reporting.
- Fixed issue with channel for world bosses not recording.

## [m1.3a] - 2017-04-19
### Fixed
- Fixed issue with map and boss detection. Partial map names should now be interpreted correctly.

### Acknowledgment
- Thanks to **Jiyuu** for the bug report.

## [m1.3] - 2017-04-19
### Added
- You can now query for boss aliases (less typing) and boss locations to scout for them better.

### Changed
- Migrated boss modules out of the main script, and began the process of developing custom settings.

### Upcoming
- Talt Tracker. For real!
- Custom settings. This will be done by JSON within Python, most likely.
- A way to send bug reports. This will take awhile, but I intend to bake this into the script.

### Acknowledgment
- Thanks to **Jiyuu** for the feature request (added).

## [m1.2d] - 2017-04-12
### Fixed
- Identified the issue linked to records not reporting within threshold of 15 minutes.
- Identified several other issues related to the above.
- The "no repeat" file used to archive announced records was repeatedly erased. I suppose I learned a lesson in `a` and `a+` file modes.

### Acknowledgment
- Thanks to **Kiito** for the bug report.

## [m1.2c] - 2017-04-12
### Fixed
- Fixed a misreferenced variable that caused issues with recording bosses.

### Acknowledgment
- Thanks to **Kiito** for the bug report.

## [m1.2b] - 2017-04-11
### Fixed
- Fixed logic with record files (not databases) that kept deleting contents.
- Fixed issuee with Deathweaver. You are now required to list map for Deathweaver.

### Acknowledgment
- Thanks to **TerminalEssence** for the bug report, once again.

### Note
- Sorry for the notifications. Will be many like this for server owners...

## [m1.2a] - 2017-04-11
### Changed
- Changed the changelog delivery to server owners. Changelogs will come in separate messages. Apologies if you don't want notifications!

### Fixed
- Fixed logic with missing/broken references -- imported all the relevant modules. This may have impacted boss alerts. Sorry.

## [m1.2] - 2017-04-10
### Added
- New error message for overlapping times.

### Fixed
- Fixed issues with Deathweaver's map not recording. (For real!)
- Corrected some other issues with the code. No more duplicate Deathweaver entries, for example.
- Entries should be checked properly for time to prevent overlap.

## [m1.1d] - 2017-04-10
### Fixed
- Fixed issues with Deathweaver's map not recording.

### Acknowledgment
- Thanks to **TerminalEssence** for the bug report.

## [m1.1c] - 2017-04-09
### Fixed
- Fixed issues with databases not connecting.
- Fixed issues with commands.
- Stopped Wings of Vaivora from shouting changelogs everytime. (MAYBE.)

### Acknowledgment
- Thanks to **Jiyuu** for the feedback on all this.

## [m1.1b] - 2017-04-09
### Fixed
- Versioning *really* corrected.
- Several bugs related to file creation also fixed.

## [m1.1a] - 2017-04-09
### Fixed
- Versioning corrected.

## [m1.1] - 2017-04-09
### Changed
- 'Wings of Vaivora' has been rewritten fully with the constants module in place.

### Fixed
- Squished some bugs related to the migration of modules.

### Upcoming
- Custom settings, including the option to 'unsubscribe' from these notifications, will be implemented after.
- Custom permissions will also be included.

## [m1.0] - 2017-03-29
### Changed
- 'Wings of Vaivora' has been rewritten using a separate module for constants. Performance should subsequently be higher.
- The welcome message should now be clearer with a brighter display.

### Upcoming
- Previous modules will be migrated over to separate modules, like constants.
- Talt Tracker will now be prioritized.
- Custom settings, including the option to 'unsubscribe' from these notifications, will be implemented after.
- Custom permissions will also be included.
