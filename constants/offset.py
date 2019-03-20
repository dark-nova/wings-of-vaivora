HELP = []
HELP.append(
"""
```
Usage:
    $offset set (tz <tz>|offset <offset>)
    $offset get (tz|offset)
    $offset list

Examples:
    $offset set tz 1
        Means: Set the offset of this guild to 1.
    $offset get tz
        Means: Shows list of tzs.
    $offset list
        Means: List all tz time zones to choose.
```
""")

HELP.append(
"""
```
Options:
    set
        Sets the next parameter.

    get
        Gets the next parameter.

    tz
        Not to be confused with <tz>.
        The parameter name for time zone.

    <tz>
        The tz to use. Can be a given integer from the list, where:
            [0] America/New_York    [NA]    Klaipeda      default
            [1] America/Sao_Paulo   [SA]    Silute
            [2] Europe/Berlin       [EU]    Fedimian
            [3] Asia/Singapore      [SEA]   Telsiai
        You are also allowed to enter your own time zone if desired. See below.
        Custom tzs must be listed as *canonical* in the Wikipedia table.

    offset
        Not to be confused with <offset>.
        The parameter name for offset.

    <offset>
        The offset from server time.
        For instance, if you are 1 hour behind your chosen server, use offset `-1`.

    list
        Lists the available <tz>s to pick.
```
Time zones: <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>
""")

LIST = """
Here are the tz time zones available:

{}"""

DEFAULT = 'America/New_York'

SUCCESS = 'You have successfully modified the guild {}.'
SUCCESS_GET = 'Your guild\'s {} is {}.'

FAIL = 'You have entered an invalid {} value!'
FAIL_DB = 'Couldn\'t save to database. Check file permissions.'
FAIL_NONE = 'Your guild doesn\'t appear to have a(n) {} set.'
