# Wings of Vaivora

## Offset Module

### Usage
+ $offset set (tz `<tz>`|`<offset>`)
+ $offset get (`<tz>`|`<offset>`)
+ $offset list

### Examples
+ $offset set tz 1
    - Means: Set the offset of this guild to 1.
+ $offset get tz
    - Means: Shows list of tzs.

### Options
+ set
    - Sets the next parameter.

+ get
    - Gets the next parameter.

+ tz
    - Not to be confused with `<tz>`.
    - The parameter name for tz.

+ `<tz>`
    - The tz to use. Can be a given integer from the list, where:
    ```
        [0] America/New_York    [NA]    Klaipeda      default
        [1] America/Sao_Paulo   [SA]    Silute
        [2] Europe/Berlin       [EU]    Fedimian
        [3] Asia/Singapore      [SEA]   Telsiai
    ```
    - You are also allowed to enter your own time zone if desired. See below.
    - Custom tzs must be listed as *canonical* in the Wikipedia table.

+ offset
    - Not to be confused with `<offset>`.
    - The parameter name for offset.

+ `<offset>`
    - The offset from server time.
    - For instance, if you are 1 hour behind your chosen server, use offset `-1`.

+ list
    - Lists the available `<tz>`s to pick.

Time zones: <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>

### Important Note

`$offset` can be considered an optional plugin to `$settings`. Therefore, it can only be used only in channels marked as `settings`.
