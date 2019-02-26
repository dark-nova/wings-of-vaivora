# Wings of Vaivora

## Settings Module

### Usage
+ $settings <setting> <talt> <talt-value> [<talt-unit>] [`<@mention>`]
+ $settings <setting> (<role> [`<@mention>`] | <channel> [`<#channel>`])
+ $settings <validate>
+ $settings <role-change> `<@mention>`
+ $settings help

### Examples
+ $settings add talt 12 talt
    - Means: Add 12 Talt to your guild record.
    - Note: If not "Authorized" or "Member", this is only temporary. It must be validated.
    - Default unit is "points".

+ $settings set talt 12
    - Means: Sets your guild record of Talt to 12. Not the same as adding.

+ $settings add talt 240 points
    - Means: The same as `$settings add talt 12`, with optional unit.

+ $settings add talt 12 `@person`
    - Means: Add 12 Talt to `@person`'s guild record.
    - You must be "Authorized" to do this.

+ $settings set channel management #management
    - Means: Sets this channel to "Management".
    - Note: this disables Management in all channels not marked as "Management".

+ $settings set role authorized `@person`
    - Means: Sets `@person` to be "Authorized".
    - You must be "Authorized" to do this.
    - Note: guild owners are considered "Super-Authorized" and must set this up first.

### Options
+ <setting>
    - This can be "add", "set", "remove", or "get". Manipulates records.
    - Options:
        * "add" can only be used for Talt-related subcommands. Increments relative to user's base.
        * "set" can be used for all associated subcommands. Sets Talt, [Role][role], and Channel.
        * "remove" can be used for all associated subcommands. Removes Talt contribution, [Roles][role] from users mentioned, etc.
        * "get" can be used for all associated subcommands. Retrieves Talt contribution, highest [Role][role] from users mentioned, etc.
    - Note: "Super-Authorized" will only be shown as "Authorized".

+ <validate>
    - Validates or invalidates records to save.
    - Options:
        * "validate" affirms temporary changes made by non-Authorized members.
        * "invalidate" removes temporary changes as if they never happened.

+ <role-change>
    - Changes a Discord role/member's [Role][role]. Shortcut for <setting>.
    - Hierarchy: none < Member < Authorized (< Super-Authorized)
    - Options:
        * "promote": increases the mentioned Discord role/member's [Role][role] by 1
        * "demote": lowers the [Role][role] by 1
    - Cannot "promote" past "Authorized"; and cannot "demote" under none.
    - Note: Cannot set the "Boss" [Role][role] using this shortcut command.

+ <talt>
    - This can be "talt" or "contribution". Allows manipulation of Talt guild records.

+ <talt-value>
    - A number. The amount to use for `talt`. 20 points = 1 talt

+ [<talt-unit>]
    - (optional) Sets the unit to use. 20 points = 1 Talt. By default, "points" will be used if omitted.
    - Options:
        * "points": shown in-game
        * "talt": the Talt item
    - Note: the Guild UI in-game always uses points.

+ guild
    - A special subcommand target for <setting> `talt`. Cannot use "add" or "remove".
    - <setting> "get" prints how many points (and Talt) the guild has.
    - <setting> "set" allows you to set the current points.
    - Missing points (unlisted contributions) will be stored in a hidden variable, for consistency.

+ <@mention>
    - (optional for <validate>) A Discord member. You must use the mention format for this.

+ [<#channel>]
    - (optional) A Discord channel. You must use the channel link format for this.
    - Both you and Wings of Vaivora must be able to see the channel.
    - If omitted in the <setting> command, the current channel will be assumed.

+ help
    - Prints this page.

#### File last modified: 2019-02-26 15:43 (UTC-8)

[role]: . "Discord roles are different from Wings of Vaivora's Roles."