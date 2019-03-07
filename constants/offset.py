HELP = []
HELP.append(
"""
```
Usage:
    $offset set (server <server>|offset <offset>)
    $offset get (server|offset)
    $offset list

Examples:
    $offset set server 1
        Means: Set the offset of this guild to 1.
    $offset get server
        Means: Shows list of servers.
    $offset list
        Means: List all server time zones to choose.
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

    server
        Not to be confused with <server>.
        The parameter name for server.

    <server>
        The server to use. Can be a given integer from the list, where:
            [0] America/New_York    [NA]    Klaipeda      default
            [1] America/Sao_Paulo   [SA]    Silute
            [2] Europe/Berlin       [EU]    Fedimian
            [3] Asia/Singapore      [SEA]   Telsiai
        You are also allowed to enter your own time zone if desired. See below.
        Custom servers must be listed as *canonical* in the Wikipedia table.

    offset
        Not to be confused with <offset>.
        The parameter name for offset.

    <offset>
        The current gem experience listed in the gem's UI. Ranges from 0 to 1 below its current maximum.

    list
        Lists the available <server>s to pick.
```
Time zones: <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>
""")

LIST = """
Here are the server time zones available:

{}"""

SUCCESS = 'You have successfully modified the guild {}.'
SUCCESS_GET_TZ = 'Your guild\'s time zone is {}.'

FAIL = 'You have entered an invalid {} value!'
FAIL_DB = 'Couldn\'t save to database. Check file permissions.'
FAIL_NO_TZ = 'Your guild doesn\'t appear to have a time zone set.'
