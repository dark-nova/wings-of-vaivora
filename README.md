# Wings of Vaivora
#### _A_ [`Tree of Savior`][tos] [`Discord`][discord] _bot project._
---

# Features
+   ### Boss Tracking

    #### *Recommended user level:* **member**

    ##### Purpose: to allow `members` to record bosses
    ___

    Tired of manually tracking bosses? Say no more with this feature.

    Prefix your command with `$boss` or `Vaivora, boss`, like:

        $boss "Earth Canceril" died ch1 12:59am "Royal Mausoleum Workers' Chapel"
        Vaivora, boss "Earth Archon" anchored ch2 13:01 "Royal Mausoleum Storage" 

    ---

    ### Syntax
    `[prefix]boss [target]:[boss] [status] [time] [channel] [map]`

    `[prefix]boss [target]:([boss], all) [entry] [map]`

    `[prefix]boss [target]:[boss] [query]`

    `[prefix]boss [target]:all [type]`

    `[prefix]boss help`

    ### Examples
    `$boss cerb died 12:00pm 4f`; channel should be omitted for field bosses

    `Vaivora, boss crab died 14:00 ch2`; map should be omitted for world bosses

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
                * Erases the entries matching the boss or `all`. Optional parameter **[map]** restricts which records to erase.
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
                * Debuffs have no effect on them, and they do not give the 'Field Boss Cube Unobtainable' debuff.
                * Cubes drop loosely on the ground and must be claimed.
            + `field`:
                * Bosses that spawn in a series of maps, only on Channel 1 in regular periods.
                * If you do not have the 'Field Boss Cube Unobtainable' debuff, upon killing, you obtain it.
                * The debuff lasts 8 hours roughly and you do not need to be online for it to tick down.
                * The debuff prevents you from contributing to other field bosses (no damage contribution),
                * so you cannot provide for your party even if your partymates do not have the debuff.
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
            + Corresponds to `Videntis Shrine`, a map where `Starving Ellaganos` spawns.
        - *Optional*
        - Suitable only for *field* bosses.`*` If unlisted, this will be unassumed.

    `*` 
```
    Notes about world and field bosses:
    
    Field bosses in channels other than 1 are considered 'world boss' variants, and should not be recorded because they spawn unpredictably, because they're jackpot bosses.
    
    Field bosses with jackpot buffs may also spawn in channel 1 but should not be recorded, either.
    
    You should record the channel for world bosses because they can spawn in any of the channels in their respective maps.
```

    6. `help`
        - Sends a direct message to you about how to use the command.

---
---

+   ### Reminders

    #### *Recommended user level:* **all**

    ##### Purpose: for individual members to have reminders by a certain time
    
    ___

    ### Syntax:

        $remind "comment" time [date]
        Vaivora, record "comment" time [date] 

    ### Arguments:

    1.  comment **(required)**

        The reminder in comment form, enclosed in double-quotes.

    2.  time **(required)**

        e.g. `13:00`, `1:11PM`, `6:00a`

    3.  date *(optional)*

        The date you want to be reminded. Defaults to today's date.

        Format like so: \[YY\]YY/MM/DD -

        + two or four digit year accepted;
        + delimiter optional, but restricted to:
            + slash, `/`
            + hyphen, `-`
            + dot, `.`
        + month and day may be single digit but *must* be delimited if so.

    #### *Vaivora* command:
        Vaivora, record

---
---

+   ### Talt Tracking.

    #### *Recommended user level:* **varies**

    ##### Purpose: to record and verify Talt donations, and to approve permissions of verifiers
    
    ___


    +   ### Donation Tracking (user)

        #### *Recommended user level:* **member**

        ##### Purpose: for users to submit their Talt donations.
        
        ___

        ### Syntax:

            $talt N [units] [@user]
            Vaivora, credit N [units] [@user]

        ### Arguments:

        1.  `N` **(required)**

            The value to use.

        2. units *(optional)*

            The units to use, among `talt` and `points`. Default is `talt`.

        3. `@user` *(optional)*


        #### *Vaivora* command:
            Vaivora, credit

    ___

    +   ### Donation Validation

        #### *Recommended user level:* **moderator**

        ##### Purpose: for moderators (or similar role) to approve and verify user records.
        
        ___

        ### Syntax:

            $talt validated @user [@user ...]
            Vaivora, validated @user [@user ...]
      
        ### Arguments:

        1.  `validated` **(required)**

            Do not use any other word here.

        2.  `@user` **(one *or more* required)**

            Mention the user.

        #### *Vaivora* command:
            Vaivora, validated

---
---

+   ### Permission Management.

    #### *Recommended user level:* **administrator**

    ##### Purpose: for administrators to add roles to users for `Wings of Vaivora` specifically. Does not affect Discord Server permissions.

    ___

    +   ### Abstract Permissions Structure

        +   #### role *(synonym)*

        1.  `administrator` *(admin)*
            + Top of the server
            + Grants roles
            + All permissions

        2.  `moderator` *(mod)*
            + Below `administrator`
            + Cannot make role changes
            + Elevated permissions for settings

        3.  `guild member` *(member)*
            + Guild member as personally defined by `moderator`s or `administrator`s
            + Below `administrator` 
            + Can use most functions
            + Cannot make role changes
            + Cannot change settings

        4.  `all` *(all)*
            + Everyone else
            + Cannot use most functions
            + Cannot make role changes
            + Cannot change settings
            + Least permissions *(or almost none)*

    ___

    ### Syntax:

        $vaivora grant|revoke role @user [@user ...]
        Vaivora, grant|revoke role @user [@user ...]

    ### Arguments: 

    1.  `grant` or `revoke` **(required)**

        This command can go in both ways: privilege granting and removing.

        For `revoke`, you only need to specify the users. Upon `revoke`ing, the associated users become `all`.

    2.  `role` **(required *for*** `grant`**)**

        Use only one role at a time. Users may only have one role, which is *separate* from the Discord server's roles. (Strictly for `Wings of Vaivora`.)

    2.  `@user` **(one *or more* required)**

        You may approve as many as possible.

    #### *Vaivora* command::

        Vaivora, approve
        Vaivora, revoke

---
---
    
### In development.
#### Last modified: 2017-01-03 15:47 (UTC-8)

---


[tos]: https://treeofsavior.com/    "'TOS'"
[discord]: https://discordapp.com/  "Chatting app and platform"