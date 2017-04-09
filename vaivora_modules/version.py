milestone   = "[m]"
unstable    = "[n]" # nightly

version_n   = []
subver_n    = []
hotfix_n    = []
status_n    = []
date_n      = []
changelog   = []

version_n.append('1')
subver_n.append('0')
hotfix_n.append('')
status_n.append(milestone)
date_n.append("2017/03/29")

def check_revisions(srv_ver):
    count   = -1
    srv_ver = srv_ver.split('.')

    if not srv_ver[1][0:-1]:
        hotfix = ''
        subver = srv_ver
    else:
        hotfix = srv_ver[1][-1]
        subver = srv_ver[1][0:-1]

    while version_n[count]  >  srv_ver[0][1:]   or \
          subver_n[count]   >  subver           or \
          hotfix_n[count]   >  hotfix           or \
          (version_n[count] == srv_ver[0][1:]   and \
           subver_n[count]  == subver           and \
           hotfix_n[count]  == hotfix           and \
           status_n[count]  <= srv_ver[0][0]):
        print(hotfix_n[count], hotfix)
        count -= 1

    return (count+1)


def get_current_version():
    return status_n[-1] + version_n[-1] + "." + subver_n[-1] + hotfix_n[-1]


def get_header():
    return """```ini
[Version:] """ + get_current_version() + """
[Date:]    """ + date_n[-1] + """```"""


def get_index(st, v, su, h):
    z   = zip(status_n, version_n, subver_n, hotfix_n)
    for n, status, version, subver, hotfix in zip(range(len(version_n)), status_n, version_n, subver_n, hotfix_n):
        if st == status and v == version and su == subver and h == hotfix:
            return n
    return -1


def get_changelogs(idx=0):
    return '\n'.join(changelog[idx:])


current     = get_header() + \
"""```diff
+ 'Wings of Vaivora' has been rewritten using a separate module for constants. Performance should subsequently be higher.
+ The welcome message should now be clearer with a brighter display.

- Upcoming changes:
  + Previous modules will be migrated over to separate modules, like constants.
  + Talt Tracker will now be prioritized.
  + Custom settings, including the option to 'unsubscribe' from these notifications, will be implemented after.
  + Custom permissions will also be included.
```
"""

changelog.append(current)


version_n.append('1')
subver_n.append('1')
hotfix_n.append('')
status_n.append(milestone)
date_n.append("2017/04/09")

current     = get_header() + \
"""```diff
+ 'Wings of Vaivora' has been rewritten fully with the constants module in place.
+ Squished some bugs related to the migration of modules.
+ Actually published this. Sorry for the delay on the downtime!

- Upcoming changes:
  + Talt Tracker to be developed next
  + Custom settings, including the option to 'unsubscribe' from these notifications, will be implemented after.
  + Custom permissions will also be included.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('1')
hotfix_n.append('a')
status_n.append(milestone)
date_n.append("2017/04/09")

current     = get_header() + \
"""```diff
+ Versioning corrected.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('1')
hotfix_n.append('b')
status_n.append(milestone)
date_n.append("2017/04/09")

current     = get_header() + \
"""```diff
+ Versioning _really_ corrected.
+ Several bugs related to file creation also fixed.
```"""

changelog.append(current)
