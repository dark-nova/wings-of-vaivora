# Wings of Vaivora

## Events Module

### Usage
+ $events (add | update | del) `<event>` `<end-date>` [`<end-time>`]
+ $events (enable | disable) `<permanent-event>`
+ $events list

### Examples
+ $events add "Some Event" 1999/9/9
    - Means: Adds an event called "Some Event" with an ending date of September 9, 1999
+ $events enable Boruta
    - Means: Enables a recurring alert for Boruta

### Options
+ add
    - Adds a custom event.

+ update
    - Updates an event. If none with the same name exist, the command fails.

+ del
    - This can be `rm`, `del`, or `delete`.
    - Deletes a custom event.

+ `<event>`
    - The name of a custom event to add.
    - Can be anything but multi-word phrases must quoted.
    - All non-alphanumeric input will be sanitized.

+ `<end-date>`
    - The end date to pick.
    - If an event ends on midnight, please ensure you use the previous day.
    - Format: `YYYY/MM/DD`. Please do not use any other format.

+ [`<end-time>`]
    - An optional argument for add/update/del `<event>`.
    - The specific time for when an event will end.
    - Format: `HH:MMAP` where `AP` is an optional `AM` or `PM`. `HH` can be 24-hour.

+ enable
    - Enables a <`permanent-event`>.
    - Enabled alerts will:
        - send messages to the first channel marked as `events`.
        - also ping roles designated as `events`.
        - Use `$settings` to do modify channels/users/roles.

+ disable
    - Disables a <`permanent-event`>.

+ <`permanent-event`>
    - Permanent events in-game.
    - Options:
        - Boruta - a weekly message on Monday at 7PM
        - Guild Territory War - a weekly message on Sunday at 8PM
        - Use `$offset` for setting server times per Discord guild.

+ list
    - Shows all events.
    - Custom events will have their time remaining listed.
    - Permanent events will show either disabled or enabled.

### Important Note

`$events` can be considered an optional plugin to `$settings`. Therefore, it can only be used only in channels marked as `settings`.

`$events` can be called by aliases `$event`, `$alert`, and `$alerts`.

#### File last modified: 2019-04-12 20:44 (UTC-7)
