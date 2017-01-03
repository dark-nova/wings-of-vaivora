# Wings of Vaivora
#### _A_ [`Tree of Savior`][tos] [`Discord`][discord] _bot project._
---

# Features
+   ### Boss Tracking

    #### *Recommended user level:* **member** & **moderator** *(for specific commands)*

    ##### Purpose: to allow `members` to record bosses
    ___

    Tired of manually tracking bosses? Say no more with this feature.
    ---

    Prefix your command with `$boss` or `Vaivora, boss`, like:

        $boss "Earth Canceril" died ch1 12:59am "Royal Mausoleum Workers' Chapel"
        Vaivora, boss "Earth Archon" anchored ch2 13:01 "Royal Mausoleum Storage" 

    ---
    ### Syntax:

        $boss BossName|"boss name" died|anchored time [chN] [Map|"Map"]
        $boss BossName|"boss name" verified|erase [chN]
        $boss BossName|"boss name" list [chN]
        $boss all list


    ### Arguments
    ---
    1.  Boss Name or `all` **(required)**

        Either part of, or full name; if spaced, enclose in double-quotes (`"`)

        `all` when used with `list` will display all valid entries.

    2.  `died`, `anchored`, `verified`, `erase`, or `list` **(required)**

        + `died` to represent a *kill*
        + `anchored` to represent an *initial spawn*
        + `verified` to represent a *confirmation of last known entry*
        + `erase` to remove an entry - **suggestion: moderator and higher only**
        + `list` to display all entries for *Argument 1*


    3.  time **(required *for* ** `died` ***and*** `anchored` **)**

        You may go with short format (24H default) or specify A(m) or P(m). e.g. `13:00`, `1:00a`, `1:00AM`, etc.

        This *must* be recorded in server time.

    4.  *Channel* `N` *(optional)*

        + Field bosses: do not list a channel - it will be stripped regardless.
        + World bosses: default `N` is `1`.

        You may omit `Ch`, but fill in the `N` which is valid from 1 to 4 inclusive, or less depending on boss.

    5.  Map *(optional)*

        Handy for field bosses only. World bosses don't move across maps. This is optional and if unlisted will be unassumed.


+   ### Reminders

    #### *Recommended user level:* **all**

    ##### Purpose: for individual members to have reminders by a certain time
    
    ___

    ### Syntax:

        $remind "comment" time [date]
        Vaivora, record "comment" time [date] 

    ### Arguments
    ---
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

    *Vaivora* command
    ---
    `Vaivora, record`


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

        ### Arguments
        ---
        1.  `N` **(required)**

            The value to use.

        2. units *(optional)*

            The units to use, among `talt` and `points`. Default is `talt`.

        3. `@user` *(optional)*


        *Vaivora* command
        ---
        `Vaivora, credit`


    +   ### Donation Validation

        #### *Recommended user level:* **moderator**

        ##### Purpose: for moderators (or similar role) to approve and verify user records.
        
        ___

        ### Syntax:

            $talt validated @user [@user ...]
            Vaivora, validated @user [@user ...]
      
        Arguments
        ---
        1.  `validated` **(required)**

            Do not use any other word here.

        2.  `@user` **(one *or more* required)**

            Mention the user.


        *Vaivora* command
        ---
        `Vaivora, validated`


+   ### Permission Management.

    #### *Recommended user level:* **administrator**

    ##### Purpose: for administrators to add roles to users for `Wings of Vaivora` specifically. Does not affect Discord Server permissions.

    ___

    ### Abstract Permissions Structure

    #### role *(synonym)*

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

    Arguments
    ---
    1.  `grant` or `revoke` **(required)**

        This command can go in both ways: privilege granting and removing.

        For `revoke`, you only need to specify the users. Upon `revoke`ing, the associated users become `all`.

    2.  `role` **(required *for*** `grant`**)**

        Use only one role at a time. Users may only have one role, which is *separate* from the Discord server's roles. (Strictly for `Wings of Vaivora`.)

    2.  `@user` **(one *or more* required)**

        You may approve as many as possible.

    *Vaivora* command
    ---
    `Vaivora, approve`

    `Vaivora, revoke`

    

### *Work in progress.*
---

[tos]: https://treeofsavior.com/    ""TOS""
[discord]: https://discordapp.com/  "Chatting app and platform"