# Wings of Vaivora

## Migrating from "asyncio"

### Breaking changes
*See also: [changelog](../CHANGELOG.md)*

- Server settings are now handled by the database.
Changes to the datatypes from the original sever settings
are handled using new schemas defined in the [DB doc](./DB.md).
- Internally, Discord id's are now `int`.
Similarly, any db use of `real` is now `integer`.
- "asyncio" depended on Python `3.4` to `3.6` primarily.
"rewrite" uses `3.6` to `3.7`.
- Previous blocking code (besides the server settings json)
using `sqlite3` now use `aiosqlite`.
- Existing records in the `boss` table of all databases
***will be unconditionally purged***.
If you want to preserve these records,
ensure you copy them manually elsewhere first.

### Migrating files
Make sure to run the utility below:

```
$ python utils/convert_db.py
```

If you are still getting errors regarding the db files,

e.g.
```
'...failed! in 111 with owner 222'
```

consider running this utility as a last resort:

```
$ python utils/force_rebuild.py
```
**Note that it is a destructive file process and preserves nothing!**

#### File last modified: 2019-02-26 15:54 (UTC-8)