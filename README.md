# Wings of Vaivora
#### _A_ [`TOS`][tos] [`Discord`][discord] _bot project._
---

# Features
+   ### Boss Tracking

    #### *Recommended user level:* **member**

    ##### Purpose: to allow `members` to record bosses
    ___

    Tired of manually tracking bosses? Say no more with this feature.

    Prefix your command with `$boss` or `Vaivora, boss`, like:

        $boss "Earth Canceril" died 12:59am "Royal Mausoleum Workers' Chapel" ch1
        Vaivora, boss "Earth Archon" anchored 13:01 "Royal Mausoleum Storage" ch2

    ---

    ### Syntax
    `[prefix]boss [target]:[boss] [status] [time] [channel] [map]`

    `[prefix]boss [target] [entry] [map]`

    `[prefix]boss [target]:[boss] [query]`

    `[prefix]boss [target]:all [type]`

    `[prefix]boss help`

    ### Examples
    `$boss fl died 12:00pm 4f`; channel should be omitted for field bosses (`fl` being `Burning Fire Lord`)

    `Vaivora, boss crab died 14:00 ch2`; map should be omitted for world bosses (`crab` being `Earth Canceril`; consult `$boss BOSS alias` for shorthand)

    ### Arguments
    0.  Prefix: `$`, `Vaivora, `
        Module: "boss"
        e.g. `$boss`, `Vaivora, boss`
          
    1.  **[target]:** **[boss]**, `all`
        + [boss]:
            - Either part of, or full name; if spaced, enclose in double-quotes (`"`)
        + `all`:
            - For 'all' bosses.
        Some commands only take specific options, so check first.

    2.  
        - **[status]:** `died`, `anchored`, `warned`
            + `died`:
                * The boss died or despawned (if field boss).
            + `anchored`:
                * The *world* boss was anchored. You or someone else has stayed in the map, leading to spawn.
            + `warned`:
                * The *field* boss was warned to spawn, i.e. `The field boss will appear in awhile.`
            + *Do not use with **[entry]**, **[query]**, or **[type]** commands.*
        - **[entry]:** `list`, `erase`
            + `list`:
                * Lists the entries for the boss you have chosen. If `all`, all records will be printed.
            + `erase`:
                * Erases the entries matching the boss or `all`. *Optional* parameter **[map]** restricts which records to erase.
            + *Do not use with **[status]**, **[query]**, or **[type]** commands.*
        - **[query]:** `synonyms`, `maps`
            + `synonyms`:
                * Synonyms for the boss to use, for shorthand for **[status]** and **[entry]** commands.
                * e.g. `spider` used in place of `Blasphemous Deathweaver`
            + `maps`:
                * Maps for the boss you choose.
            + *Valid for **[target]:[boss]** only.*
            + *Do not use with **[status]**, **[entry]**, or **[type]** commands.*
        - **[type]**: `world`, `field`
            + `world`:
                * Bosses that spawn on specific mechanics and do not wander maps. They can spawn in all channels.
                * Cubes drop loosely on the ground and must be claimed.
            + `field`:
                * Bosses that spawn in a series of maps, only on Channel 1 in regular periods.
                * Cubes automatically go into inventory of parties of highest damage contributors.
    3.  **[time]**
        - e.g. 9:00p
        - e.g. 21:00
            + Both these times are equivalent. Make sure to reccord 'AM' or 'PM' if you're using 12 hour format.
        - *Required for **[status]** commands.
        - Remove spaces. 12 hour and 24 hour times acceptable, with valid delimiters `:` and `.`. Use server time.

    4.  **[channel]**
        - e.g. ch1
        - e.g. 1
            + Both these channels are equivalent. You may drop the `CH`.
        - *Optional*
        - Suitable only for *world* bosses.`*` If unlisted, CH`1` will be assumed.

    5.  **[map]**
        - e.g. `vid`
            + Corresponds to `Videntis Shrine`, a map where `Violent Cerberus` spawns.
        - *Optional*
        - Suitable only for *field* bosses.`*` If unlisted, this will be unassumed.

    6. `help`
        - Sends a direct message to you about how to use the command.


    +   `*` 
        Notes about world and field bosses:
                
        You should record the channel for world bosses because they can spawn in any of the channels in their respective maps.

        Likewise, you should record the map for field bosses because they pick a different map on each subsequent spawn. Spawns do not repeat maps.

---
---

+   ### Talt Tracking
    
    ##### Part of the `Settings` module.

    #### *Recommended user level:* **varies**

    ##### Purpose: to record and verify Talt donations, and to approve permissions of verifiers
    
    ___

    ### Syntax
    `[prefix]settings [modify] talt [value] [unit] [@mention ...]`

    `[prefix]settings [validation]`

    ### Examples
    `$settings add talt 12`; adds 12 Talt to yourself

    `$settings set talt 12`; sets your contribution to 12 Talt. Not the same as above.

    `$settings add talt 240 points`; equivalent to the first command

    `$settings add talt 12 @mention`; adds 12 Talt to mentioned target(s)

    ### Arguments
    0.  Prefix: `$`, `Vaivora, `
        Module: "settings"
        e.g. `$settings`, `Vaivora, settings`
          
    1.  
        - **[modify]:** `add`, `set`, `unset`, `rm`
            + `add`:
                * Adds directly to previous record.
            + `set`:
                * Modifies the previous record entirely.
            + `unset, rm`:
                * Removes set values.
        - **[validation]:** `validate`, `verify`, `invalidate`, `unverify`
            + `validate` & `verify`:
                * Validates temporary records.
            + `invalidate` & `unverify`:
                * Invalidates temporary records.
            + **You must be at least `Authorized` to do so!**

    2. `talt`
        - Changes the associated target's or targets' `Talt` contribution. This is a necessary keyword.
        
    3. **[value]:**
        - How much you are using. Keep in mind that default measurement is `Talt`, and not `Points`.
        - See **[unit]** for more information.

    4. **[unit]:** `talt`, `points`
        + *Optional* 
        + `talt`:
            * Default. Unit weight of 1, or 20 points.
        + `points`:
            * Unit weight of **0.05** or, 20 points = 1 Talt. Invalid if not divisible by 20.

    5.  **[@mention]:**
        + *Optional*
        + Mention people to tag them with the contribution you listed, instead of yourself.
        + **You must be at least `Authorized` to do so, and your mentions must be at least `Member`s!**

---
---
    
### In development.
#### Last modified: 2017-08-24 13:37 (UTC-7)

---


[tos]: https://treeofsavior.com/    "'Tree of Savior'"
[discord]: https://discordapp.com/  "Chatting app and platform"