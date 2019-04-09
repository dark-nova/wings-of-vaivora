# Wings of Vaivora

## Administration Module

### Usage
+ $admin (reload | get_ids)

### Examples
+ $admin reload
    - Means: Reloads all [cogs](cogs) except itself and main.

+ $admin get_ids
    - Means: Gets id's of all members of a guild.

### Options
+ reload
    - Reloads all cogs except itself and main.
    - Note that this is intended **only** to reload updates to the following [cogs](cogs):
        * [settings.py](cogs/settings.py)
        * [boss.py](cogs/boss.py)
        * [gems.py](cogs/gems.py)
        * [offset.py](cogs/offset.py)
        * [meme.py](cogs/meme.py)
    - Do **not** modify behavior to reload the entire bot. ***Only use some kind of script management like systemd to restart.***
    - Can (and should) be used first if issues arise for the aforementioned cogs.

+ get_ids
    - Gets id's of all members of a guild.
    - Sends a DM with the id's, with the member (as a string) and id per line.

#### File last modified: 2019-04-09 10:11 (UTC-7)

[cog]: (cogs)