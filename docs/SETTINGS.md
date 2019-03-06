# Wings of Vaivora

## Settings Module

### Usage
+ $settings `<setting>` `<talt>` `<talt-value>` [`<talt-unit>`] [`<@mention>`]
+ $settings `<setting>` `<obj>` (`<role>` [`<@mention>`] | `<channel>` [`<#channel>`])
+ $settings help

### Examples
+ $settings add talt 12 talt
    - Means: Add 12 Talt to your guild record.

+ $settings set talt 12
    - Means: Sets your guild record of Talt to 12. Not the same as adding.

+ $settings add talt 240 points
    - Means: The same as `$settings add talt 12`, with optional unit.

+ $settings add talt 12 `@person`
    - Means: Add 12 Talt to `@person`'s guild record.
    - You must be "Authorized" to do this.

+ $settings set channel Settings #settings
    - Means: Sets this channel to "Settings".
    - Note: this disables Settings in all channels not marked as "Settings".

+ $settings set role authorized `@person`
    - Means: Sets `@person` to be "Authorized".
    - You must be "Authorized" to do this.
    - Note: guild owners are considered "Super-Authorized" and must set this up first.

### Options
+ `<setting>`
    - This can be "add", "set", "remove", or "get". Manipulates records.
    - Options:
        * "add" can only be used for Talt-related subcommands. Increments relative to user's base.
        * "set" can be used for all associated subcommands. Sets Talt, [Role][role], and Channel.
        * "remove" can be used for all associated subcommands. Removes Talt contribution, [Roles][role] from users mentioned, etc.
        * "get" can be used for all associated subcommands. Retrieves Talt contribution, highest [Role][role] from users mentioned, etc.
    - Note: "Super-Authorized" will only be shown as "Authorized".

+ `<obj>`
    - This is the object to modify. For users, "roles". For channels, "channels".

+ `<channel>`
    - This can be "settings" or "boss". Sets channels (and restricts others).
    - Options:
        * "settings": Adds a channel to allow all settings commands. 'get'ters will still be unrestricted.
        * "boss": Adds a channel to accept boss record manipulation.
    - Once a channel is set (and none were, before), many commands are no longer read outside the allowed channels.

+ `<contribution>`
    - This can be "points", "talt", or "contributions".
    - Options:
        * "points": shown in the guild UI in-game
        * "talt": defined to be the item; 1 talt = 20 points
        * "contributions": the same as "points"
    - Allows manipulation of Talt guild records.

+ `<contribution-value>`
    - A number. The amount to use for `talt`. 20 points = 1 talt

+ guild
    - A special subcommand target for `<setting>` `talt`. Cannot use "add" or "remove".
    - `<setting>` "get" prints how many points (and Talt) the guild has.
    - `<setting>` "set" allows you to set the current points.
    - Missing points (unlisted contributions) will be stored in a hidden variable, for consistency.

+ `<@mention>`
    - (optional) A Discord member or role.
    - Preferably, you should use the mention format for this. You may use ID's if necessary.
    - If omitted in the `<setting>` command, the command user will be assumed.

+ [`<#channel>`]
    - (optional) A Discord channel.
    - You must use the channel link format for this.
    - Both you and Wings of Vaivora must be able to see the channel.
    - If omitted in the `<setting>` command, the current channel will be assumed.

+ help
    - Prints this page.

#### File last modified: 2019-03-05 16:15 (UTC-8)

[role]: . "Discord roles are different from Wings of Vaivora's Roles."