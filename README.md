# Wings of Vaivora
 _A_ [`Tree of Savior`][tos] [`Discord`][discord] _bot project._
---

### Features
1.  ## Boss Tracking
    ___

    Tired of manually tracking bosses? Say no more with this feature.
    ---

    Prefix your command with `$boss` or `Vaivora, boss`, like:

        $boss "Earth Canceril" died ch1 12:59am "Royal Mausoleum Workers' Chapel"
        Vaivora, boss "Earth Archon" anchored ch2 13:01 "Royal Mausoleum Storage" 

    ---
    Syntax:

        $boss BossName|"boss name" died|anchored ChN 00:00 [Map|"Map"]

    Arguments
    ---
    1.  Boss Name **(required)**
        Either part of, or full name; if spaced, enclose in double quotes, `"`
    2.  Died/Anchored **(required)**
        Either one or the other to signify usage
    3.  *Channel* `N` **(required)**
        You may omit `Ch`, but fill in the `N` which is valid from 1 to 4 inclusive.
    4.  Time **(required)**
        You may go with short format (24H default) or specify A(m) or P(m). i.e. 13:00, 1:00a, 1:00AM, etc.
    5.  Map *(optional)*
        Handy for field bosses only. World bosses don't move across maps.

2.  ## Reminders.
    ___

    For individual members to use; general purpose.
    ---

    Syntax:

        $remind "comment" time [date]
        Vaivora, note "comment" time [date] 

    Arguments
    ---
    1.  comment **(required)**
        The reminder in comment form, enclosed in quotes.
    2.  time **(required)**
        Examples: `13:00`, `1:11PM`, `6:00a`
    3.  date *(optional)*
        The date you want to be reminded. Defaults to today's date.
        Format like so: \[YY\]YY/MM/DD -
        + two or four digit year accepted;
        + delimiter optional, but restricted to:
            + slash, `/`
            + hyphen, `-`
            + dot, `.`
        + month and day may be single digit but *must* be delimited if so.

3.  ## Talt Tracking.
    ___

    Wings of Vaivora has two primary functions for Talt, plus one auxiliary function for permissions:
    ---

    1.  ### Donation Tracking (user)
        #### Recommended user level: guild member
        ___

        For users to submit their Talt donations.
        ---

        Syntax:

            $talt @user N [talt|points]
            Vaivora, credit @user N [talt|points]

        Arguments
        ---
        1.  `@user` **(required)**
            Mention the user.
        2.  `N` **(required)**
            The value to use.
        3. units *(optional)*
            The units to use. Default is `talt`.

        Vaivora command
        ---
        `Vaivora, credit`

    2.  ### Donation Validation
        #### Recommended user level: moderator
        ___

        For moderators (or similar role) to approve and verify user records.
        ---

        Syntax:

            $talt validated @user [@user ...]
            Vaivora, validated @user [@user ...]
      
        Arguments
        ---
        1.  `validated` **(required)**
            Do not use any other word here.
        2.  `@user` (one or more required)
            Mention the user.

        Vaivora command
        ---
        `Vaivora, validated`

    3.  ### Setup for Permissions
        #### Recommended user level: administrator
        ___

        For administrators to add moderators for Talt contribution verification.
        ---

        Syntax:

            $talt approve|revoke @user [@user ...]
            Vaivora, approve|revoke @user [@user ...]

        Arguments
        ---
        1.  `approve` or `revoke` **(required)**
            This command can go in both ways: privilege granting and removing.
        2.  `@user`(one or more required)
            You may approve as many as possible.

        Vaivora command
        ---
        `Vaivora, approve`
        `Vaivora, revoke`

### *Work in progress.*
---

[tos]: https://treeofsavior.com/    "\"TOS\""
[discord]: https://discordapp.com/  "Chatting app and platform"