# Wings of Vaivora

## Administration Module

### Usage
+ $admin (reload `<cog>` [`<cog>` ...] | reload_all | get_ids)

### Examples
+ $admin reload cogs.boss
    - Means: Reloads the [boss](../cogs/boss.py) cog.

+ $admin reload_all
    - Means: Reloads all [cogs](../cogs) except itself and main.

+ $admin get_ids
    - Means: Gets id's of all members of a guild.

### Options
+ reload
    - Reloads any number of cogs after the subcommand.
    - Can reload any cog except itself and main.
    - Do **not** modify behavior to reload the entire bot. ***Only use some kind of script management like systemd to restart.***
    - Can (and should) be used first if issues arise for the aforementioned cogs.

+ `<cog>`
    - A cog to reload. Uses syntax 'cogs.filename'.
    - You must supply one or more for the reload subcommand.

+ reload_all
    - Reloads all cogs except itself and main.
    - Note that this is intended **only** to reload updates to the following [cogs](../cogs):
        * [settings.py](../cogs/settings.py)
        * [boss.py](../cogs/boss.py)
        * [gems.py](../cogs/gems.py)
        * [offset.py](../cogs/offset.py)
        * [events.py](../cogs/events.py)
        * [meme.py](../cogs/meme.py)
    - Do **not** modify behavior to reload the entire bot. ***Only use some kind of script management like systemd to restart.***
    - Can (and should) be used first if issues arise for the aforementioned cogs.

+ get_ids
    - Gets id's of all members of a guild.
    - Sends a DM with the id's, with the member (as a string) and id per line.

#### File last modified: 2019-04-24 17:53 (UTC-7)
